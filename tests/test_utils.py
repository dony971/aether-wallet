import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.helpers import aeth_from_units, units_from_aeth, shorten_hash


def test_aeth_conversion():
    assert aeth_from_units(10_000_000_000) == 1.0
    assert aeth_from_units(1_000_000_000) == 0.1
    assert aeth_from_units(0) == 0.0


def test_units_conversion():
    assert units_from_aeth(1.0) == 10_000_000_000
    assert units_from_aeth(0.1) == 1_000_000_000
    assert units_from_aeth(0.0) == 0


def test_shorten_hash():
    h = "abcdef1234567890"
    assert shorten_hash(h, 4) == "abcd...7890"
    assert shorten_hash("abcd", 2) == "abcd"
    assert shorten_hash("abc", 1) == "abc"
