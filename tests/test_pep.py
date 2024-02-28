import pathlib

from asic.files.definitions.pep import PEP
from pytest import fixture

from .conftest import ALL_FILES, TESTFILES


@fixture
def pep_remote_path():
    pep_path = ALL_FILES["pep"]["path"]
    path = pathlib.PureWindowsPath(pep_path)
    return path


@fixture
def pep_file(pep_remote_path):
    path = pep_remote_path
    file = PEP.from_remote_path(path)
    return file


@fixture
def local_pep_file(pep_file: PEP, datafiles: pathlib.Path) -> pathlib.Path:
    relative_path = pep_file.path.relative_to(pep_file.path.anchor)
    local_file = datafiles / relative_path
    assert local_file.is_file()
    return local_file


@TESTFILES
def test_pep_read(pep_file: PEP, local_pep_file):
    data = pep_file.read(local_pep_file)
    assert len(data) == 23


@TESTFILES
def test_pep_preprocess(pep_file: PEP, local_pep_file):
    long_data = pep_file.preprocess(local_pep_file)
    assert len(long_data) == 23
