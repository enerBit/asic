import pathlib

import pytest
from asic.files.definitions import SUPPORTED_FILE_CLASSES

from tests.conftest import ALL_FILES

pytestmark = pytest.mark.parametrize(
    "remote_path,expected",
    [(v["path"], v) for k, v in ALL_FILES.items()],
)


def test_file_from_remote_path(remote_path, expected):
    path = pathlib.PureWindowsPath(remote_path.lower())
    expected_kind = expected["kind"]
    asic_class = SUPPORTED_FILE_CLASSES[expected_kind]
    file = asic_class.from_remote_path(path)
    assert file.path == pathlib.PureWindowsPath(expected["path"].lower())
    assert file.kind == expected_kind
    assert file.visibility.value == expected["visibility"]
    assert file.year == expected["year"]
    assert file.month == expected["month"]
    assert file.day == expected["day"]
    assert file.extension == expected["extension"]
    assert file.version == expected["version"]
    assert file.agent == expected["agent"]
