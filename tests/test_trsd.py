import pathlib

from asic.files.definitions.trsd import TRSD
from pytest import fixture

from .conftest import ALL_FILES, TESTFILES


@fixture
def trsd_remote_path():
    trsd_path = ALL_FILES["trsd"]["path"]
    path = pathlib.PureWindowsPath(trsd_path)
    return path


@fixture
def trsd_file(trsd_remote_path):
    path = trsd_remote_path
    file = TRSD.from_remote_path(path)
    return file


@fixture
def local_trsd_file(trsd_file: TRSD, datafiles: pathlib.Path) -> pathlib.Path:
    relative_path = trsd_file.path.relative_to(trsd_file.path.anchor)
    local_file = datafiles / relative_path
    assert local_file.is_file()
    return local_file


@TESTFILES
def test_trsd_read(trsd_file: TRSD, local_trsd_file):
    data = trsd_file.read(local_trsd_file)
    assert len(data) == 33


@TESTFILES
def test_trsd_preprocess(trsd_file: TRSD, local_trsd_file):
    long_data = trsd_file.preprocess(local_trsd_file)
    assert len(long_data) == 720
