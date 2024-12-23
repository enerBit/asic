import pathlib

from pytest import fixture

from asic.files.definitions.tgrl import TGRL

from .conftest import ALL_FILES, TESTFILES


@fixture
def tgrl_remote_path():
    tgrl_path = ALL_FILES["tgrl"]["path"]
    path = pathlib.PureWindowsPath(tgrl_path)
    return path


@fixture
def tgrl_file(tgrl_remote_path):
    path = tgrl_remote_path
    file = TGRL.from_remote_path(path)
    return file


@fixture
def local_tgrl_file(tgrl_file: TGRL, datafiles: pathlib.Path) -> pathlib.Path:
    relative_path = tgrl_file.path.relative_to(tgrl_file.path.anchor)
    local_file = datafiles / relative_path
    assert local_file.is_file()
    return local_file


@TESTFILES
def test_tgrl_read(tgrl_file: TGRL, local_tgrl_file):
    data = tgrl_file.read(local_tgrl_file)
    assert len(data) == 3812


@TESTFILES
def test_tgrl_preprocess(tgrl_file: TGRL, local_tgrl_file):
    long_data = tgrl_file.preprocess(local_tgrl_file)
    assert len(long_data) == 91488
