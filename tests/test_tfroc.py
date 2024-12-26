import pathlib

from pytest import fixture

from asic.files.definitions.tfroc import TFROC

from .conftest import ALL_FILES, TESTFILES


@fixture
def tfroc_remote_path():
    tfroc_path = ALL_FILES["tfroc"]["path"]
    path = pathlib.PureWindowsPath(tfroc_path)
    return path


@fixture
def tfroc_file(tfroc_remote_path):
    path = tfroc_remote_path
    file = TFROC.from_remote_path(path)
    return file


@fixture
def local_tfroc_file(tfroc_file: TFROC, datafiles: pathlib.Path) -> pathlib.Path:
    relative_path = tfroc_file.path.relative_to(tfroc_file.path.anchor)
    local_file = datafiles / relative_path
    assert local_file.is_file()
    return local_file


@TESTFILES
def test_tfroc_read(tfroc_file: TFROC, local_tfroc_file):
    data = tfroc_file.read(local_tfroc_file)
    assert len(data) == 1


@TESTFILES
def test_tfroc_preprocess(tfroc_file: TFROC, local_tfroc_file):
    long_data = tfroc_file.preprocess(local_tfroc_file)
    assert len(long_data) == 1
