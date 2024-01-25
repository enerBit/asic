import pathlib

from asic.files.definitions.pme import PME
from pytest import fixture

from .conftest import ALL_FILES, TESTFILES


@fixture
def PME_remote_path():
    PME_path = ALL_FILES["PME"]["path"]
    path = pathlib.PureWindowsPath(PME_path)
    return path


@fixture
def PME_file(PME_remote_path):
    path = PME_remote_path
    file = PME.from_remote_path(path)
    return file


@fixture
def local_PME_file(PME_file: PME, datafiles: pathlib.Path) -> pathlib.Path:
    relative_path = PME_file.path.relative_to(PME_file.path.anchor)
    local_file = datafiles / relative_path
    assert local_file.is_file()
    return local_file


@TESTFILES
def test_PME_read(PME_file: PME, local_PME_file):
    data = PME_file.read(local_PME_file)
    assert len(data) == 59


@TESTFILES
def test_PME_preprocess(PME_file: PME, local_PME_file):
    long_data = PME_file.preprocess(local_PME_file)
    assert len(long_data) == 59
