import pathlib

from pytest import fixture

from asic.files.definitions.dspcttos import DSPCTTOS

from .conftest import ALL_FILES, TESTFILES


@fixture
def dspcttos_remote_path():
    dspcttos_path = ALL_FILES["dspcttos"]["path"]
    path = pathlib.PureWindowsPath(dspcttos_path)
    return path


@fixture
def dspcttos_file(dspcttos_remote_path):
    path = dspcttos_remote_path
    file = DSPCTTOS.from_remote_path(path)
    return file


@fixture
def local_dspcttos_file(dspcttos_file: DSPCTTOS, datafiles: pathlib.Path) -> pathlib.Path:
    relative_path = dspcttos_file.path.relative_to(dspcttos_file.path.anchor)
    local_file = datafiles / relative_path
    assert local_file.is_file()
    return local_file


@TESTFILES
def test_dspcttos_read(dspcttos_file: DSPCTTOS, local_dspcttos_file):
    data = dspcttos_file.read(local_dspcttos_file)
    assert len(data) == 2


@TESTFILES
def test_dspcttos_preprocess(dspcttos_file: DSPCTTOS, local_dspcttos_file):
    long_data = dspcttos_file.preprocess(local_dspcttos_file)
    print(len(long_data))
    assert len(long_data) == 48
