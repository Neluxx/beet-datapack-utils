import pytest

from datapack_utils import Version, parse_version


def test_parse_and_compare():
    assert parse_version("1.20.5") < "1.21"
    assert Version("26.3") >= "26.3"
    assert Version("26.3") > Version("26.2")
    assert Version("1.21.0") == "1.21"
    assert hash(Version("1.21.0")) == hash(Version("1.21"))
    assert str(Version("1.21.9")) == "1.21.9"


def test_sorting():
    versions = sorted(map(Version, ["26.3", "1.19", "1.21.9", "1.20.5"]))
    assert [str(v) for v in versions] == ["1.19", "1.20.5", "1.21.9", "26.3"]


def test_invalid_version():
    with pytest.raises(ValueError):
        Version("26.3-snapshot-1")
    assert Version("26.3") != "26.3-snapshot-1"
    assert Version("26.3") != 26.3
