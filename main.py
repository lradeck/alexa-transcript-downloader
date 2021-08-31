import asyncio
import glob
import json
import logging
import os
import pickle
import sys
from datetime import datetime
from json import JSONDecodeError
from pathlib import Path

import backoff as backoff
import structlog
from aiohttp import ClientSession
from arsenic import get_session, services, browsers
from arsenic.errors import InvalidCookieDomain, ArsenicTimeout
from pytz import timezone

from dtos import CustomerHistoryRecord
from in_out import InOut

FILE_DATE_FORMAT = "%Y_%m_%d %H_%M_%S"


def set_arsenic_log_level(level=logging.WARNING):
    logger = logging.getLogger('arsenic')

    def logger_factory():
        return logger

    structlog.configure(logger_factory=logger_factory)
    logger.setLevel(level)


async def get_cookie_jar(session):
    return {cookie["name"]: cookie["value"] for cookie in await session.get_all_cookies()}


async def login_with_cookies(session, previous_user_cookie, user):
    await session.get("https://alexa.amazon.de")
    for key, value in previous_user_cookie.items():
        try:
            await session.add_cookie(key, value)
        except InvalidCookieDomain as e:
            print(e)
    try:
        await session.get("https://alexa.amazon.de")
        await session.wait_for_element(5, "#d-header-title")

        cookie_jar = await get_cookie_jar(session)
        await dump_cookies(user, cookie_jar)
        print("Logged in with user " + user + " by using cookies.")
        return cookie_jar
    except ArsenicTimeout:
        print("Could not login user " + user + " with its old cookies.")
        print("Deleting cookies...")
        await delete_existing_cookie(user)


async def delete_existing_cookie(user):
    existing_cookies = await read_cookies()
    for user_cookie_tuple in existing_cookies:
        if user_cookie_tuple[0] == user:
            existing_cookies.remove(user_cookie_tuple)


async def get_new_valid_session(user, password, previous_user_cookie, service):
    print("Logging into user " + user + "...")
    set_arsenic_log_level(level=logging.CRITICAL)
    browser = browsers.Chrome()
    browser.capabilities = {
        "goog:chromeOptions": {"args": ["--headless", "--disable-gpu"]}
    }

    cookies = {}
    if previous_user_cookie:
        async with get_session(service, browser) as session:
            cookies = await login_with_cookies(session, previous_user_cookie, user)

    if not cookies:
        async with get_session(service, browser) as session:
            cookies = await login_over_form(cookies, password, session, user)

    return cookies


async def login_manually(password, service, user):
    browser = browsers.Chrome()
    async with get_session(service, browser) as session2:
        print("Trying to login over login form...")
        await fill_login_form_and_submit(password, session2, user)
        try:
            await session2.wait_for_element(6000, "#d-header-title")
            cookies = await get_cookie_jar(session2)
            await dump_cookies(user, cookies)
        except ArsenicTimeout:
            print("Could not login to user " + user + ". Aborting script.")
            exit(0)
    return cookies


async def read_cookies():
    try:
        return pickle.load(open("cookies.p", "rb"))
    except FileNotFoundError:
        return []


async def dump_cookies(user, cookies):
    await delete_existing_cookie(user)
    existing_cookies = await read_cookies()
    existing_cookies.append((user, cookies))
    pickle.dump(existing_cookies, open("cookies.p", "wb"))


@backoff.on_exception(backoff.expo, ArsenicTimeout)
async def login_over_form(cookies, password, session, user):
    await fill_login_form_and_submit(password, session, user)
    try:
        await session.wait_for_element(20, "#d-header-title")
        cookies = await get_cookie_jar(session)
        await dump_cookies(user, cookies)
        print("Logged in with user " + user + " by using form.")
    except ArsenicTimeout:
        print("Could not login user " + user + " automatically because of timeout. Trying again...")
    return cookies


async def fill_login_form_and_submit(password, session, user):
    await session.get("https://alexa.amazon.de")
    try:
        await session.wait_for_element(20, "#ap_email")
    except ArsenicTimeout:
        print("Amazon is replying slowly...")
    email_input = await session.get_element("#ap_email")
    await email_input.send_keys(user)
    password_input = await session.get_element("#ap_password")
    await password_input.send_keys(password)
    submit = await session.get_element("#signInSubmit")
    div = await session.get_element("div[data-a-input-name=rememberMe]")
    checkbox = await div.get_element(".a-icon.a-icon-checkbox")
    await checkbox.click()
    await submit.click()


async def collect_cookies(loop, credentials, service):
    tasks = []

    previous_cookies = []
    try:
        previous_cookies = pickle.load(open("cookies.p", "rb"))
    except FileNotFoundError:
        print("No previous cookies were found. ")
        pass

    previous_user_cookies = None
    for username in credentials:
        for user_cookie_tuple in previous_cookies:
            if username == user_cookie_tuple[0]:
                previous_user_cookies = user_cookie_tuple[1]
        task = loop.create_task(execute_login(username, credentials[username], previous_user_cookies, service))
        tasks.append(task)
    done_tasks, _ = await asyncio.wait(tasks)
    return done_tasks


def get_parameters(previous_request_token):
    p1 = ('startTime', '0')
    p2 = ('endTime', str(int(datetime.now().timestamp() * 1000)))
    p3 = ('previousRequestToken', previous_request_token)
    return (p1, p2, p3) if previous_request_token else (p1, p2)


async def execute_collection(user, cookie):
    session = ClientSession()
    session.cookie_jar.update_cookies(cookie)
    all_records = set()
    previous_request_token = None
    counter = 0

    while previous_request_token is not None or counter == 0:
        previous_request_token = await update_all_records(all_records, previous_request_token, session, user)
        counter = counter + 1

    await session.close()
    return all_records


async def create_collection(loop, user_cookie_tuples):
    tasks = []
    for tuple in user_cookie_tuples:
        task = loop.create_task(execute_collection(tuple[0], tuple[1]))
        tasks.append(task)
    done_tasks, _ = await asyncio.wait(tasks)
    return done_tasks


async def execute_login(user, password, previous_user_cookie, service):
    cookie_jar = await get_new_valid_session(user, password, previous_user_cookie, service)
    return user, cookie_jar


@backoff.on_exception(backoff.expo, JSONDecodeError)
async def update_all_records(all_records, previous_request_token, session, user):
    headers = {
        'authority': 'www.amazon.de',
        'rtt': '50',
        'downlink': '10',
        'ect': '4g',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
        'sec-ch-ua-mobile': '?0',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/90.0.4430.93 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    response = await session.get('https://www.amazon.de/alexa-privacy/apd/rvh/customer-history-records',
                                 headers=headers,
                                 params=get_parameters(previous_request_token))
    text = await response.text()
    print(response)
    print(text)
    history_record = CustomerHistoryRecord.from_json(json.loads(text))
    if len(history_record.records) > 0:
        previous_request_token = history_record.encoded_request_token
        all_records.update(history_record.records)
        print("Added " + str(len(all_records)) + " records for customer " + user)
    else:
        previous_request_token = None
    return previous_request_token


def read_last_records():
    os.chdir(".")
    dates = []
    old_records = set()
    for file in glob.glob("*.xlsx"):
        try:
            dates.append(datetime.strptime(Path(file).stem, FILE_DATE_FORMAT))
        except:
            print("Beim Verarbeiten der Xlsx-Dateien ist ein Fehler aufgetreten.")
            pass
    if len(dates) > 0:
        old_records = InOut.read_from_excel(max(dates).strftime(FILE_DATE_FORMAT) + ".xlsx")

    return old_records


def run():
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    script_execution = datetime.now(timezone('Europe/Berlin')).strftime(FILE_DATE_FORMAT)
    service = services.Chromedriver(binary='./chromedriver.exe', log_file=os.devnull)
    credentials_file = sys.argv[1]

    credentials = None
    if credentials_file and os.path.exists(credentials_file):
        credentials = InOut.read_yaml(credentials_file)
    else:
        print("Credentials not found. Please provide the credentials file.")
        exit(0)

    loop = asyncio.get_event_loop()
    done_tasks = loop.run_until_complete(collect_cookies(loop, credentials, service))
    user_cookie_tuples = []
    for task in done_tasks:
        user_cookie_tuples.append(task.result())

    final_cookies = []
    for user_cookie_tuple in user_cookie_tuples:
        if not user_cookie_tuple[1]:
            user = user_cookie_tuple[0]
            cookies = asyncio.run(login_manually(credentials[user], service, user))
            final_cookies.append((user, cookies))
        else:
            final_cookies.append((user_cookie_tuple[0], user_cookie_tuple[1]))

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    done_tasks = loop.run_until_complete(create_collection(loop, final_cookies))
    total_records = set()
    for task in done_tasks:
        result = task.result()
        total_records.update(result)

    last_records = read_last_records()
    total_records = total_records.union(last_records)
    diff = total_records.difference(last_records)
    pickle.dump(total_records, open("test_records.p", "wb"))
    InOut().write_to_excel(total_records, script_execution + ".xlsx")
    print("Added " + str(len(diff)) + " new records to existing " + str(
        len(last_records)) + " records.")


run()
