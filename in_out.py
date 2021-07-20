from datetime import datetime, timezone
import time

import pandas as pd
import yaml

from dtos import Record, VoiceHistoryRecordItem, Device
from pytz import timezone


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
               "voice1Key",
               "voice1Type",
               "voice1UtteranceId",
               "voice1Timestamp",
               "voice1Transcript",
               "voice1AgentVisualName",
               "voice2Key",
               "voice2Type",
               "voice2UtteranceId",
               "voice2Timestamp",
               "voice2Transcript",
               "voice2AgentVisualName",
               "voice3Key",
               "voice3Type",
               "voice3UtteranceId",
               "voice3Timestamp",
               "voice3Transcript",
               "voice3AgentVisualName"
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
            voice_history_record_items = []

            for i in range(12, 29, 6):
                record_item_key = row[InOut.COLUMNS[i]]
                if not pd.isnull(record_item_key):
                    record_item_type = row[InOut.COLUMNS[i + 1]]
                    utterance_id = row[InOut.COLUMNS[i + 2]]
                    v_timestamp = InOut.date_as_str_to_timestamp(row[InOut.COLUMNS[i + 3]])
                    transcript_text = row[InOut.COLUMNS[i + 4]]
                    agent_visual_name = row[InOut.COLUMNS[i + 5]]

                    vr = VoiceHistoryRecordItem(record_item_key, record_item_type, utterance_id, v_timestamp,
                                                transcript_text, agent_visual_name)
                    voice_history_record_items.append(vr)

            r: Record = Record(record_key, record_type, timestamp, customer_id, Device(device_name, device_entity_id),
                               is_binary_feedback_provided, is_feedback_positive, utterance_type, domain, intent,
                               skill_name, voice_history_record_items)
            records.add(r)
        return records

    @classmethod
    def write_to_excel(cls, records, file_name):
        if len(records) > 0:
            dict =
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
                InOut.COLUMNS[12]: r.voice_history_record_items[0].record_item_key
                if 0 < len(r.voice_history_record_items) else None,
                InOut.COLUMNS[13]: r.voice_history_record_items[0].record_item_type
                if 0 < len(r.voice_history_record_items) else None,
                InOut.COLUMNS[14]: r.voice_history_record_items[0].utterance_id
                if 0 < len(r.voice_history_record_items) else None,
                InOut.COLUMNS[15]: InOut.timestamp_to_date_as_str(r.voice_history_record_items[0].timestamp)
                if 0 < len(r.voice_history_record_items) else None,
                InOut.COLUMNS[16]: r.voice_history_record_items[0].transcript_text
                if 0 < len(r.voice_history_record_items) else None,
                InOut.COLUMNS[17]: r.voice_history_record_items[0].agent_visual_name
                if 0 < len(r.voice_history_record_items) else None,
                InOut.COLUMNS[18]: r.voice_history_record_items[1].record_item_key
                if 1 < len(r.voice_history_record_items) else None,
                InOut.COLUMNS[19]: r.voice_history_record_items[1].record_item_type
                if 1 < len(r.voice_history_record_items) else None,
                InOut.COLUMNS[20]: r.voice_history_record_items[1].utterance_id
                if 1 < len(r.voice_history_record_items) else None,
                InOut.COLUMNS[21]:InOut.timestamp_to_date_as_str(r.voice_history_record_items[1].timestamp)
                if 1 < len(r.voice_history_record_items) else None,
                InOut.COLUMNS[22]: r.voice_history_record_items[1].transcript_text
                if 1 < len(r.voice_history_record_items) else None,
                InOut.COLUMNS[23]: r.voice_history_record_items[1].agent_visual_name
                if 1 < len(r.voice_history_record_items) else None,
                InOut.COLUMNS[24]: r.voice_history_record_items[2].record_item_key
                if 2 < len(r.voice_history_record_items) else None,
                InOut.COLUMNS[25]: r.voice_history_record_items[2].record_item_type
                if 2 < len(r.voice_history_record_items) else None,
                InOut.COLUMNS[26]: r.voice_history_record_items[2].utterance_id
                if 2 < len(r.voice_history_record_items) else None,
                InOut.COLUMNS[27]: InOut.timestamp_to_date_as_str(r.voice_history_record_items[2].timestamp)
                if 2 < len(r.voice_history_record_items) else None,
                InOut.COLUMNS[28]: r.voice_history_record_items[2].transcript_text
                if 2 < len(r.voice_history_record_items) else None,
                InOut.COLUMNS[29]: r.voice_history_record_items[2].agent_visual_name
                if 2 < len(r.voice_history_record_items) else None,

            } for r in records],
                columns=InOut.COLUMNS)

            writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Sheet1')
            writer.save()
