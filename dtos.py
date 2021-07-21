import json

import pandas as pd


def is_null(var):
    return pd.isnull(var) or var == ""


class Device:
    def __init__(self, device_name, device_entity_id) -> None:
        self.device_name = device_name if not is_null(device_name) else None
        self.device_entity_id = device_entity_id if not is_null(device_entity_id) else None

    def __hash__(self):
        return hash(str(self.device_name))

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4, ensure_ascii=False)

    def __repr__(self):
        return self.toJSON()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False


class Record:
    def __init__(self, record_key, record_type, timestamp, customer_id, device: Device,
                 is_binary_feedback_provided, is_feedback_positive, utterance_type,
                 domain, intent, skill_name,
                 conversation) -> None:
        self.record_key = record_key if not is_null(record_key) else None
        self.record_type = record_type if not is_null(record_type) else None
        self.timestamp = timestamp if not is_null(timestamp) else None
        self.customer_id = customer_id if not is_null(customer_id) else None
        self.device = device if not is_null(device) else None
        self.is_binary_feedback_provided = is_binary_feedback_provided if not is_null(
            is_binary_feedback_provided) else None
        self.is_feedback_positive = is_feedback_positive if not is_null(is_feedback_positive) else None
        self.utterance_type = utterance_type if not is_null(utterance_type) else None
        self.domain = domain if not is_null(domain) else None
        self.intent = intent if not is_null(intent) else None
        self.skill_name = skill_name if not is_null(skill_name) else None
        self.conversation = conversation

    def __hash__(self):
        return hash(str(self.record_key))

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4, ensure_ascii=False)

    def __repr__(self):
        return self.toJSON()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False


class CustomerHistoryRecord:
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
                          [(v["recordItemType"], v["transcriptText"])
                           for v in r["voiceHistoryRecordItems"]])
                   for r in j["customerHistoryRecords"]]

        return CustomerHistoryRecord(records,
                                     j["encodedRequestToken"],
                                     j["noDataFoundWithinTimeLimit"],
                                     j["lastRecordTimestamp"])

    def __init__(self, records: [Record], encoded_request_token,
                 no_data_found_within_time_limit, last_record_timestamp) -> None:
        self.records = records
        self.encoded_request_token = encoded_request_token if not is_null(encoded_request_token) else None
        self.no_data_found_within_time_limit = no_data_found_within_time_limit if not is_null(
            no_data_found_within_time_limit) else None
        self.last_record_timestamp = last_record_timestamp if not is_null(last_record_timestamp) else None

    def __hash__(self):
        return hash(str(self.encoded_request_token))

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4, ensure_ascii=False)

    def __repr__(self):
        return self.toJSON()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False
