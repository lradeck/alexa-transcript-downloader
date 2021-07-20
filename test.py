import pickle
import time
import unittest
from datetime import datetime
from typing import List

from pytz import timezone

from dtos import Record
from in_out import InOut


class TestClass(unittest.TestCase):
    def test_timestamp_conversion(self):
        timestamp_in = 1612878616023
        date_in = InOut.timestamp_to_date_as_str(timestamp_in)
        timestamp_out = InOut.date_as_str_to_timestamp(date_in)
        assert timestamp_in == timestamp_out

    def test_io(self):
        test_records = pickle.load( open( "test_records.p", "rb" ) )
        print(len(test_records))
        InOut().write_to_excel(test_records, "test.xlsx")
        read_records = InOut().read_from_excel("test.xlsx")
        for t in test_records:
            for r in read_records:
                if t.record_key == r.record_key and t not in read_records:
                    print(t)

        for r in read_records:
            if r in test_records:
                print("yes")
            else:
                print("no")
        print(len(read_records))

        assert test_records == read_records
