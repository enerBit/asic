import pathlib

from asic.files.definitions.adem import ADEM
from pytest import fixture

from .conftest import ALL_FILES, TESTFILES


@fixture
def adem_remote_path():
    adem_path = ALL_FILES["adem"]["path"]
    path = pathlib.PureWindowsPath(adem_path)
    return path


@fixture
def adem_file(adem_remote_path):
    path = adem_remote_path
    file = ADEM.from_remote_path(path)
    return file


@fixture
def local_adem_file(adem_file: ADEM, datafiles: pathlib.Path) -> pathlib.Path:
    relative_path = adem_file.path.relative_to(adem_file.path.anchor)
    local_file = datafiles / relative_path
    assert local_file.is_file()
    return local_file


@TESTFILES
def test_adem_read(adem_file: ADEM, local_adem_file):
    data = adem_file.read(local_adem_file)
    assert len(data) == 232


@TESTFILES
def test_adem_preprocess(adem_file: ADEM, local_adem_file):
    long_data = adem_file.preprocess(local_adem_file)
    assert len(long_data) == 1128
