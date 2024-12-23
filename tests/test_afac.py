import pathlib

from pytest import fixture

from asic.files.definitions.afac import AFAC

from .conftest import ALL_FILES, TESTFILES


@fixture
def afac_remote_path():
    afac_path = ALL_FILES["afac"]["path"]
    path = pathlib.PureWindowsPath(afac_path)
    return path


@fixture
def afac_file(afac_remote_path):
    path = afac_remote_path
    file = AFAC.from_remote_path(path)
    return file


@fixture
def local_afac_file(afac_file: AFAC, datafiles: pathlib.Path) -> pathlib.Path:
    relative_path = afac_file.path.relative_to(afac_file.path.anchor)
    local_file = datafiles / relative_path
    assert local_file.is_file()
    return local_file


@TESTFILES
def test_afac_read(afac_file: AFAC, local_afac_file):
    data = afac_file.read(local_afac_file)
    assert len(data) == 9


@TESTFILES
def test_afac_preprocess(afac_file: AFAC, local_afac_file):
    long_data = afac_file.preprocess(local_afac_file)
    assert len(long_data) == 1035
