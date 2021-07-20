import json
from datetime import datetime


class Device:
    device_name: str
    device_entity_id: None

    def __init__(self, device_name: str, device_entity_id: None) -> None:
        self.device_name = device_name
        self.device_entity_id = device_entity_id

    def __hash__(self):
        return hash(str(self.device_name))

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4, ensure_ascii=False)

    def __repr__(self):
        return self.toJSON()


class VoiceHistoryRecordItem:
    record_item_key: str
    record_item_type: str
    utterance_id: str
    timestamp: int
    transcript_text: str
    agent_visual_name: str

    def __init__(self, record_item_key: str, record_item_type: str, utterance_id: str, timestamp: int,
                 transcript_text: str, agent_visual_name: str) -> None:
        self.record_item_key = record_item_key
        self.record_item_type = record_item_type
        self.utterance_id = utterance_id
        self.timestamp = timestamp
        self.transcript_text = transcript_text
        self.agent_visual_name = agent_visual_name

    def __hash__(self):
        return hash(str(self.record_item_key))

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4, ensure_ascii=False)

    def __repr__(self):
        return self.toJSON()


class Record:
    record_key: str
    record_type: str
    timestamp: int
    customer_id: str
    device: Device
    is_binary_feedback_provided: bool
    is_feedback_positive: bool
    utterance_type: str
    domain: str
    intent: str
    skill_name: str
    voice_history_record_items: [VoiceHistoryRecordItem]

    def __init__(self, record_key: str, record_type: str, timestamp: int, customer_id: str, device: Device,
                 is_binary_feedback_provided: bool, is_feedback_positive: bool, utterance_type: str,
                 domain: str, intent: str, skill_name: str,
                 voice_history_record_items: [VoiceHistoryRecordItem]) -> None:
        self.record_key = record_key
        self.record_type = record_type
        self.timestamp = timestamp
        self.customer_id = customer_id
        self.device = device
        self.is_binary_feedback_provided = is_binary_feedback_provided
        self.is_feedback_positive = is_feedback_positive
        self.utterance_type = utterance_type
        self.domain = domain
        self.intent = intent
        self.skill_name = skill_name
        self.voice_history_record_items = voice_history_record_items

    def __hash__(self):
        return hash(str(self.record_key))

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4, ensure_ascii=False)

    def __repr__(self):
        return self.toJSON()


class CustomerHistoryRecord:
    encodedRequestToken: str
    noDataFoundWithinTimeLimit: bool
    lastRecordTimestamp: None
    records: [Record]

    @classmethod
    def from_json(cls, j):
        records = [Record(r["recordKey"],
                          r["recordType"],
                          r["timestamp"],
                          r["customerId"],
                          Device(r["device"]["deviceName"],
                                 r["device"]["deviceEntityId"]),
                          r["isBinaryFeedbackProvided"],
                          r["isFeedbackPositive"],
                          r["utteranceType"],
                          r["domain"],
                          r["intent"],
                          r["skillName"],
                          [VoiceHistoryRecordItem(v["recordItemKey"],
                                                  v["recordItemType"],
                                                  v["utteranceId"],
                                                  v["timestamp"],
                                                  v["transcriptText"],
                                                  v["agentVisualName"])
                           for v in r["voiceHistoryRecordItems"]])
                   for r in j["customerHistoryRecords"]]

        return CustomerHistoryRecord(records,
                                     j["encodedRequestToken"],
                                     j["noDataFoundWithinTimeLimit"],
                                     j["lastRecordTimestamp"])

    def __init__(self, records: [Record], encoded_request_token: str,
                 no_data_found_within_time_limit: bool, last_record_timestamp: None) -> None:
        self.records = records
        self.encoded_request_token = encoded_request_token
        self.no_data_found_within_time_limit = no_data_found_within_time_limit
        self.last_record_timestamp = last_record_timestamp

    def __hash__(self):
        return hash(str(self.encodedRequestToken))

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4, ensure_ascii=False)

    def __repr__(self):
        return self.toJSON()
