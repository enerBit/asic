import pathlib

from pytest import fixture

from asic.files.definitions.tserv import TSERV

from .conftest import ALL_FILES, TESTFILES


@fixture
def tserv_remote_path():
    tserv_path = ALL_FILES["tserv"]["path"]
    path = pathlib.PureWindowsPath(tserv_path)
    return path


@fixture
def tserv_file(tserv_remote_path):
    path = tserv_remote_path
    file = TSERV.from_remote_path(path)
    return file


@fixture
def local_tserv_file(tserv_file: TSERV, datafiles: pathlib.Path) -> pathlib.Path:
    relative_path = tserv_file.path.relative_to(tserv_file.path.anchor)
    local_file = datafiles / relative_path
    assert local_file.is_file()
    return local_file


@TESTFILES
def test_tserv_read(tserv_file: TSERV, local_tserv_file):
    data = tserv_file.read(local_tserv_file)
    assert len(data) == 4


@TESTFILES
def test_tserv_preprocess(tserv_file: TSERV, local_tserv_file):
    long_data = tserv_file.preprocess(local_tserv_file)
    assert len(long_data) == 4
