import pickle
import unittest
from typing import List

from dtos import Record
from in_out import InOut


class TestStringMethods(unittest.TestCase):
    def test_io(self):
        test_records = pickle.load( open( "test_records.p", "rb" ) )
        print(len(test_records))
        InOut().write_to_excel(test_records, "test.xlsx")
        read_records =  InOut().read_from_excel("test.xlsx")
        print(len(read_records))
        for f, b in zip(test_records, read_records):
            if f != b:
                print(f)
                print(b)
                exit(0)

        assert test_records == read_records
