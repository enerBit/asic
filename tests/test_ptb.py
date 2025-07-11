import pathlib

from pytest import fixture

from asic.files.definitions.ptb import PTB

from .conftest import ALL_FILES, TESTFILES


@fixture
def ptb_remote_path():
    ptb_path = ALL_FILES["PTB"]["path"]
    path = pathlib.PureWindowsPath(ptb_path)
    return path


@fixture
def ptb_file(ptb_remote_path):
    path = ptb_remote_path
    file = PTB.from_remote_path(path)
    return file


@fixture
def local_ptb_file(ptb_file: PTB, datafiles: pathlib.Path) -> pathlib.Path:
    relative_path = ptb_file.path.relative_to(ptb_file.path.anchor)
    local_file = datafiles / relative_path
    assert local_file.is_file()
    return local_file


@TESTFILES
def test_ptb_read(ptb_file: PTB, local_ptb_file):
    data = ptb_file.read(local_ptb_file)
    assert len(data) == 2


@TESTFILES
def test_ptb_preprocess(ptb_file: PTB, local_ptb_file):
    long_data = ptb_file.preprocess(local_ptb_file)
    assert len(long_data) == 24
