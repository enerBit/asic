"""Define test data files.

**DO NOT PUT PRIVATE AGENTE DATA HERE!!!**
Use the generic agents XXXC, XXXG, XXXD or XXXT for agent (private) test files.

Make sure that the path casing (UPPERCASE, lowerase, etc) is as the local file system.
"""
import pathlib

import pytest

FIXTURE_DIR = pathlib.Path(__file__).parent.resolve() / "INFORMACION_XM"

TESTFILES = pytest.mark.datafiles(
    FIXTURE_DIR,
    keep_top_dir=True,
)

ALL_FILES = {
    "adem": {
        "path": "/INFORMACION_XM/PUBLICOK/SIC/COMERCIA/2023-10/adem1001.Tx2",
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
        "path": "/INFORMACION_XM/USUARIOSK/XXXC/SIC/COMERCIA/2023-10/aenc1001.tx2",
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
        "path": "/INFORMACION_XM/USUARIOSK/XXXC/SIC/COMERCIA/2023-10/BalCttos1001.tx2",
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
