import pathlib

from asic.files.definitions.balcttos import BALCTTOS
from pytest import fixture

from .conftest import ALL_FILES, TESTFILES


@fixture
def balcttos_remote_path():
    balcttos_path = ALL_FILES["balcttos"]["path"]
    path = pathlib.PureWindowsPath(balcttos_path)
    return path


@fixture
def balcttos_file(balcttos_remote_path):
    path = balcttos_remote_path
    file = BALCTTOS.from_remote_path(path)
    return file


@fixture
def local_balcttos_file(
    balcttos_file: BALCTTOS, datafiles: pathlib.Path
) -> pathlib.Path:
    relative_path = balcttos_file.path.relative_to(balcttos_file.path.anchor)
    local_file = datafiles / relative_path
    assert local_file.is_file()
    return local_file


@TESTFILES
def test_balcttos_read(balcttos_file: BALCTTOS, local_balcttos_file):
    data = balcttos_file.read(local_balcttos_file)
    assert len(data) == 12


@TESTFILES
def test_balcttos_preprocess(balcttos_file: BALCTTOS, local_balcttos_file):
    long_data = balcttos_file.preprocess(local_balcttos_file)
    assert len(long_data) == 287
