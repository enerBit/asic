"""Example: re-use file selection.

If all (or many) of your tests rely on the same files it can be easier to
define one decorator beforehand and apply it to every test.
"""
import pathlib

import pytest

FIXTURE_DIR = pathlib.Path(__file__).parent.resolve() / "informacion_xm"

TESTFILES = pytest.mark.datafiles(
    FIXTURE_DIR,
    keep_top_dir=True,
)

ALL_FILES = {
    "adem": {
        "path": "/INFORMACION_XM/PublicoK/SIC/COMERCIA/2023-10/adem1001.Tx2",
        "kind": "adem",
        "visibility": "public",
        "year": 2023,
        "month": 10,
        "day": 1,
        "extension": ".tx2",
        "version": "001",
        "agent": None,
    },
    "aenc": {
        "path": "/INFORMACION_XM/USUARIOSK/XXXC/SIC/COMERCIA/2023-10/AENC1001.tx2",
        "kind": "aenc",
        "visibility": "agent",
        "year": 2023,
        "month": 10,
        "day": 1,
        "extension": ".tx2",
        "version": "001",
        "agent": "xxxc",
    },
    "balcttos": {
        "path": "/informacion_xm/usuariosk/xxxc/sic/comercia/2023-10/BalCttos1001.tx2",
        "kind": "balcttos",
        "visibility": "agent",
        "year": 2023,
        "month": 10,
        "day": 1,
        "extension": ".tx2",
        "version": "001",
        "agent": "xxxc",
    },
}


@TESTFILES
def test_test_files(datafiles: pathlib.Path):
    for p in datafiles.rglob("*"):
        if p.is_file():
            print(p)
    assert 0