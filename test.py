import os
import pickle
import unittest

from in_out import InOut


class Testclass(unittest.TestCase):

    def ttest_timestamp_conversion(self):
        timestamp_in = 1612878616023
        date_in = InOut.timestamp_to_date_as_str(timestamp_in)
        timestamp_out = InOut.date_as_str_to_timestamp(date_in)
        assert timestamp_in == timestamp_out


    def test_io(self):
        test_records = pickle.load(open("test_records.p", "rb"))
        print(len(test_records))
        InOut().write_to_excel(test_records, "test.xlsx")
        read_records = InOut().read_from_excel("test.xlsx")
        os.remove("test.xlsx")

        assert test_records == read_records
