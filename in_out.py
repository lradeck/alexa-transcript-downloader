from datetime import datetime

import pandas as pd
import yaml


class InOut:
    @classmethod
    def read_yaml(cls, file):
        with open(file, 'r') as stream:
            return yaml.safe_load(stream)

    @classmethod
    def write_to_excel(cls, records, file_name='data.xlsx'):
        if len(records) > 0:
            df = pd.DataFrame([{
                "record_key": r.record_key,
                "recordType": r.record_type,
                "timestamp": datetime.utcfromtimestamp(int(r.timestamp / 1000)).strftime('%Y-%m-%d %H:%M:%S'),
                "customerId": r.customer_id,
                "device_name": r.device.device_name,
                "device_entity_id": r.device.device_entity_id,
                "is_binary_feedback_provided": r.is_binary_feedback_provided,
                "is_feedback_positive": r.is_feedback_positive,
                "utteranceType": r.utterance_type,
                "domain": r.domain,
                "intent": r.intent,
                "skillName": r.skill_name,
                "voice1Key": r.voice_history_record_items[0].record_item_key
                if 0 < len(r.voice_history_record_items) else None,
                "voice1Type": r.voice_history_record_items[0].record_item_type
                if 0 < len(r.voice_history_record_items) else None,
                "voice1UtteranceId": r.voice_history_record_items[0].utterance_id
                if 0 < len(r.voice_history_record_items) else None,
                "voice1Timestamp": datetime.utcfromtimestamp(
                    int(r.voice_history_record_items[0].timestamp / 1000)).strftime('%Y-%m-%d %H:%M:%S')
                if 0 < len(r.voice_history_record_items) else None,
                "voice1Transcript": r.voice_history_record_items[0].transcript_text
                if 0 < len(r.voice_history_record_items) else None,
                "voice1AgentVisualName": r.voice_history_record_items[0].agent_visual_name
                if 0 < len(r.voice_history_record_items) else None,
                "voice2Key": r.voice_history_record_items[1].record_item_key
                if 1 < len(r.voice_history_record_items) else None,
                "voice2Type": r.voice_history_record_items[1].record_item_type
                if 1 < len(r.voice_history_record_items) else None,
                "voice2UtteranceId": r.voice_history_record_items[1].utterance_id
                if 1 < len(r.voice_history_record_items) else None,
                "voice2Timestamp": datetime.utcfromtimestamp(
                    int(r.voice_history_record_items[1].timestamp / 1000)).strftime('%Y-%m-%d %H:%M:%S')
                if 1 < len(r.voice_history_record_items) else None,
                "voice2Transcript": r.voice_history_record_items[1].transcript_text
                if 1 < len(r.voice_history_record_items) else None,
                "voice2AgentVisualName": r.voice_history_record_items[1].agent_visual_name
                if 1 < len(r.voice_history_record_items) else None,
                "voice3Key": r.voice_history_record_items[2].record_item_key
                if 2 < len(r.voice_history_record_items) else None,
                "voice3Type": r.voice_history_record_items[2].record_item_type
                if 2 < len(r.voice_history_record_items) else None,
                "voice3UtteranceId": r.voice_history_record_items[2].utterance_id
                if 2 < len(r.voice_history_record_items) else None,
                "voice3Timestamp": datetime.utcfromtimestamp(
                    int(r.voice_history_record_items[2].timestamp / 1000)).strftime('%Y-%m-%d %H:%M:%S')
                if 2 < len(r.voice_history_record_items) else None,
                "voice3Transcript": r.voice_history_record_items[2].transcript_text
                if 2 < len(r.voice_history_record_items) else None,
                "voice3AgentVisualName": r.voice_history_record_items[2].agent_visual_name
                if 2 < len(r.voice_history_record_items) else None,

            } for r in records],
                columns=["record_key",
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
                         ])

            writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Sheet1')
            writer.save()
