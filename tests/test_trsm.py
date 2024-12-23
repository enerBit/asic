import pathlib

from pytest import fixture

from asic.files.definitions.trsm import TRSM

from .conftest import ALL_FILES, TESTFILES


@fixture
def trsm_remote_path():
    trsm_path = ALL_FILES["trsm"]["path"]
    path = pathlib.PureWindowsPath(trsm_path)
    return path


@fixture
def trsm_file(trsm_remote_path):
    path = trsm_remote_path
    file = TRSM.from_remote_path(path)
    return file


@fixture
def local_trsm_file(trsm_file: TRSM, datafiles: pathlib.Path) -> pathlib.Path:
    relative_path = trsm_file.path.relative_to(trsm_file.path.anchor)
    local_file = datafiles / relative_path
    assert local_file.is_file()
    return local_file


@TESTFILES
def test_trsm_read(trsm_file: TRSM, local_trsm_file):
    data = trsm_file.read(local_trsm_file)
    assert len(data) == 43


@TESTFILES
def test_trsm_preprocess(trsm_file: TRSM, local_trsm_file):
    long_data = trsm_file.preprocess(local_trsm_file)
    assert len(long_data) == 43
