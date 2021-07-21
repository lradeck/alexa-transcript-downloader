import asyncio
import glob
import json
import logging
import os
import pickle
import sys
from datetime import datetime
from pathlib import Path

import structlog
from aiohttp import ClientSession
from pytz import timezone
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait

from dtos import CustomerHistoryRecord
from in_out import InOut
from arsenic import get_session, services, browsers, keys

FILE_DATE_FORMAT = "%Y_%m_%d %H_%M_%S"


def set_arsenic_log_level(level=logging.WARNING):
    logger = logging.getLogger('arsenic')

    def logger_factory():
        return logger

    structlog.configure(logger_factory=logger_factory)
    logger.setLevel(level)


async def get_new_valid_session(user, password):
    print("Logging into user " + user + "...")
    set_arsenic_log_level(level=logging.CRITICAL)
    service = services.Chromedriver(binary='./chromedriver.exe', log_file=os.devnull)
    browser = browsers.Chrome()
    # browser.capabilities = {
    #     "goog:chromeOptions": {"args": ["--headless", "--disable-gpu"]}
    # }

    async with get_session(service, browser) as session:
        await session.get("https://alexa.amazon.de")
        email_input = await session.get_element("#ap_email")
        await email_input.send_keys(user)
        password_input = await session.get_element("#ap_password")
        await password_input.send_keys(password)
        submit = await session.get_element("#signInSubmit")
        await submit.click()
        try:
            await session.wait_for_element(120, "#fa-carousel-title")
        except TimeoutException:
            print("Skipping " + user + " because of timeout. Did you confirm the login email?")
            return None
        print("Successfully obtained cookies for user " + user)
        return {cookie["name"]: cookie["value"] for cookie in await session.get_all_cookies()}


def get_task_results():
    credentials_file = sys.argv[1]
    if credentials_file and os.path.exists(credentials_file):
        credentials = InOut.read_yaml(credentials_file)
    else:
        print("Credentials not found. Please provide the credentials file.")
        exit(0)

    loop = asyncio.get_event_loop()
    done_tasks = loop.run_until_complete(create_tasks(loop, credentials))
    return [task.result() for task in done_tasks]


async def create_tasks(loop, credentials):
    tasks = []
    for username in credentials:
            task = loop.create_task(execute_task(username, credentials[username]))
            tasks.append(task)
    done_tasks, _ = await asyncio.wait(tasks)
    return done_tasks


def get_parameters(previous_request_token):
    p1 = ('startTime', '0')
    p2 = ('endTime', str(int(datetime.now().timestamp() * 1000)))
    p3 = ('previousRequestToken', previous_request_token)
    return (p1, p2, p3) if previous_request_token else (p1, p2)


async def execute_task(user, password):
    cookie_jar = await get_new_valid_session(user, password)
    if not cookie_jar:
        return set()
    session = ClientSession()
    session.cookie_jar.update_cookies(cookie_jar)
    headers = {
        'authority': 'www.amazon.de',
        'rtt': '50',
        'downlink': '10',
        'ect': '4g',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
        'sec-ch-ua-mobile': '?0',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    all_records = set()
    previous_request_token = None
    counter = 0

    while previous_request_token is not None or counter == 0:
        response = await session.get('https://www.amazon.de/alexa-privacy/apd/rvh/customer-history-records',
                                     headers=headers,
                                     params=get_parameters(previous_request_token))
        text = await response.text()
        history_record = CustomerHistoryRecord.from_json(json.loads(text))
        if len(history_record.records) > 0:
            previous_request_token = history_record.encoded_request_token
            all_records.update(history_record.records)
            print("Added " + str(len(all_records)) + " records for customer " + user)
        else:
            previous_request_token = None
        counter = counter + 1

    await session.close()
    return all_records


def read_last_records():
    os.chdir(".")
    dates = []
    old_records = set()
    for file in glob.glob("*.xlsx"):
        try:
            dates.append(datetime.strptime(Path(file).stem, FILE_DATE_FORMAT))
        except:
            pass
    if len(dates) > 0:
        dates.sort()
        old_records = InOut.read_from_excel(dates[0].strftime(FILE_DATE_FORMAT) + ".xlsx")

    return old_records


def run():
    script_execution = datetime.now(timezone('Europe/Berlin')).strftime(FILE_DATE_FORMAT)
    total_dir = Path(script_execution)
    data = get_task_results()
    total_records = set()
    for records in data:
        total_records.update(records)
    last_records = read_last_records()
    total_records = total_records.union(last_records)
    pickle.dump(total_records, open("test_records.p", "wb"))
    InOut().write_to_excel(total_records, script_execution + ".xlsx")
    print("Downloaded " + str(len(total_records)) + " records of " + str(len(data)) + " participants.")
    print(str(len(total_records) - len(last_records)) + " records were new.")


run()
