import pathlib

from asic.files.definitions.aenc import AENC
from pytest import fixture

from .conftest import ALL_FILES, TESTFILES


@fixture
def aenc_remote_path():
    aenc_path = ALL_FILES["aenc"]["path"]
    path = pathlib.PureWindowsPath(aenc_path)
    return path


@fixture
def aenc_file(aenc_remote_path):
    path = aenc_remote_path
    file = AENC.from_remote_path(path)
    return file


@TESTFILES
def test_aenc_read(aenc_file, datafiles):
    relative_path = aenc_file.path.relative_to(aenc_file.path.anchor).lower()
    local_file = datafiles / relative_path
    print(local_file)
    data = aenc_file.read(local_file)
    assert len(data) == 2


@TESTFILES
def test_aenc_preprocess(aenc_file, datafiles):
    relative_path = aenc_file.path.relative_to(aenc_file.path.anchor).lower()
    local_file = datafiles / relative_path
    long_data = aenc_file.preprocess(local_file)
    assert len(long_data) == 48
