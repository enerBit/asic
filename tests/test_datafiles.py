import pathlib

from .conftest import TESTFILES


@TESTFILES
def test_test_files(datafiles: pathlib.Path):
    for p in datafiles.rglob("*"):
        if p.is_file():
            print(p)
    assert True
