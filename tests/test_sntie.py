import pathlib

from pytest import fixture

from asic.files.definitions.sntie import SNTIE

from .conftest import ALL_FILES, TESTFILES


@fixture
def sntie_remote_path():
    sntie_path = ALL_FILES["sntie"]["path"]
    path = pathlib.PureWindowsPath(sntie_path)
    return path


@fixture
def sntie_file(sntie_remote_path):
    path = sntie_remote_path
    file = SNTIE.from_remote_path(path)
    return file


@fixture
def local_sntie_file(sntie_file: SNTIE, datafiles: pathlib.Path) -> pathlib.Path:
    relative_path = sntie_file.path.relative_to(sntie_file.path.anchor)
    local_file = datafiles / relative_path
    assert local_file.is_file()
    return local_file


@TESTFILES
def test_sntie_read(sntie_file: SNTIE, local_sntie_file):
    data = sntie_file.read(local_sntie_file)
    assert len(data) == 766


@TESTFILES
def test_sntie_preprocess(sntie_file: SNTIE, local_sntie_file):
    long_data = sntie_file.preprocess(local_sntie_file)
    assert len(long_data) == 3302
