"""
Smoke test for P3_HOSTNAME validation (issue #54).

Run from the repository root:
    python3 tests/test_p3_hostname_validation.py
or with pytest:
    pytest tests/test_p3_hostname_validation.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from p2pp.variables import validate_p3_hostname, P3_HOSTNAME_MAX_LENGTH


def test_valid_hostnames():
    assert validate_p3_hostname("192.168.1.42") == "192.168.1.42"
    assert validate_p3_hostname("my-palette-3.local") == "my-palette-3.local"
    assert validate_p3_hostname("P3_1234.host-name") == "P3_1234.host-name"
    assert validate_p3_hostname("  p3.local  ") == "p3.local"


def test_empty_and_none():
    assert validate_p3_hostname("") is None
    assert validate_p3_hostname("   ") is None
    assert validate_p3_hostname(None) is None


def test_invalid_characters():
    # URL injection attempts must be rejected
    assert validate_p3_hostname("evil.com:5000/x#") is None
    assert validate_p3_hostname("host/../../admin") is None
    assert validate_p3_hostname("localhost header: x") is None
    assert validate_p3_hostname("h@x0r") is None
    assert validate_p3_hostname("host\nname") is None
    assert validate_p3_hostname("[fe80::1]") is None


def test_length_limits():
    assert validate_p3_hostname("a" * P3_HOSTNAME_MAX_LENGTH) == "a" * P3_HOSTNAME_MAX_LENGTH
    assert validate_p3_hostname("a" * (P3_HOSTNAME_MAX_LENGTH + 1)) is None


def test_non_string():
    assert validate_p3_hostname(12345) is None
    assert validate_p3_hostname(["host"]) is None


if __name__ == "__main__":
    test_valid_hostnames()
    test_empty_and_none()
    test_invalid_characters()
    test_length_limits()
    test_non_string()
    print("All hostname validation tests passed.")
