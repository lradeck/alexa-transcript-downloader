from datetime import datetime, timezone

import pandas as pd
import yaml
from pytz import timezone

from dtos import Record, Device


class InOut:
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
    COLUMNS = ["record_key",
               "recordType",
               "timestamp",
               "customerId",
               "device_name",
               "device_entity_id",
               "is_binary_feedback_provided",
               "is_feedback_positive",
               "utteranceType",
               "domain",
               "intent",
               "skillName",
               "conversation",
               ]

    @classmethod
    def read_yaml(cls, file):
        with open(file, 'r') as stream:
            return yaml.safe_load(stream)

    @classmethod
    def date_as_str_to_timestamp(cls, date):
        timestamp = 0
        try:
            timestamp = int(datetime.strptime(date, InOut.DATE_FORMAT).timestamp() * 1000)
        except:
            pass
        return timestamp

    @classmethod
    def timestamp_to_date_as_str(cls, timestamp):
        return datetime.fromtimestamp(timestamp / 1000.0,
                                      tz=timezone('Europe/Berlin')).strftime(InOut.DATE_FORMAT)

    @classmethod
    def read_from_excel(cls, file_name):
        df = pd.read_excel(file_name)
        records = set()
        for index, row in df.iterrows():
            record_key = row[InOut.COLUMNS[0]]
            record_type = row[InOut.COLUMNS[1]]
            timestamp = InOut.date_as_str_to_timestamp(row[InOut.COLUMNS[2]])
            customer_id = row[InOut.COLUMNS[3]]
            device_name = row[InOut.COLUMNS[4]]
            device_entity_id = row[InOut.COLUMNS[5]]
            is_binary_feedback_provided = row[InOut.COLUMNS[6]]
            is_feedback_positive = row[InOut.COLUMNS[7]]
            utterance_type = row[InOut.COLUMNS[8]]
            domain = row[InOut.COLUMNS[9]]
            intent = row[InOut.COLUMNS[10]]
            skill_name = row[InOut.COLUMNS[11]]
            conversation = eval(row[InOut.COLUMNS[12]])
            r: Record = Record(record_key, record_type, timestamp, customer_id, Device(device_name, device_entity_id),
                               is_binary_feedback_provided, is_feedback_positive, utterance_type, domain, intent,
                               skill_name, conversation)
            records.add(r)
        return records

    @classmethod
    def write_to_excel(cls, records, file_name):
        if len(records) > 0:
            df = pd.DataFrame([{
                InOut.COLUMNS[0]: r.record_key,
                InOut.COLUMNS[1]: r.record_type,
                InOut.COLUMNS[2]: InOut.timestamp_to_date_as_str(r.timestamp),
                InOut.COLUMNS[3]: r.customer_id,
                InOut.COLUMNS[4]: r.device.device_name,
                InOut.COLUMNS[5]: r.device.device_entity_id,
                InOut.COLUMNS[6]: r.is_binary_feedback_provided,
                InOut.COLUMNS[7]: r.is_feedback_positive,
                InOut.COLUMNS[8]: r.utterance_type,
                InOut.COLUMNS[9]: r.domain,
                InOut.COLUMNS[10]: r.intent,
                InOut.COLUMNS[11]: r.skill_name,
                InOut.COLUMNS[12]: r.conversation
            } for r in records],
                columns=InOut.COLUMNS)

            writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Sheet1')
            writer.save()
