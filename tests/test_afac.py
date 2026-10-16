import logging
import pathlib
from io import BytesIO

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


def _afac_bytes(header: list[str], row: list[str]) -> bytes:
    return (";".join(header) + "\r\n" + ";".join(row) + "\r\n").encode("cp1252")


def test_afac_validate_raw_known_concepts(afac_file: AFAC):
    header = ["AGENTE", "DEMANDA REAL (kWh)", "VENTAS EN BOLSA ($)"]
    assert afac_file.validate_raw(_afac_bytes(header, ["AAGG", "1", "2"]))


def test_afac_validate_raw_new_concept_logs_warning(afac_file: AFAC, caplog):
    header = ["AGENTE", "DEMANDA REAL (kWh)", "CONCEPTO NUEVO XM ($)"]
    with caplog.at_level(logging.WARNING, logger="asic.files.file"):
        assert afac_file.validate_raw(_afac_bytes(header, ["AAGG", "1", "2"]))
    assert "CONCEPTO NUEVO XM ($)" in caplog.text
    assert "DEMANDA REAL (kWh)" not in caplog.text


def test_afac_validate_raw_removed_concept(afac_file: AFAC, caplog):
    header = ["AGENTE", "DEMANDA REAL (kWh)"]
    with caplog.at_level(logging.WARNING, logger="asic.files.file"):
        assert afac_file.validate_raw(_afac_bytes(header, ["AAGG", "1"]))
    assert caplog.text == ""


def test_afac_validate_raw_missing_agente(afac_file: AFAC, caplog):
    header = ["DEMANDA REAL (kWh)", "VENTAS EN BOLSA ($)"]
    with caplog.at_level(logging.ERROR, logger="asic.files.file"):
        assert not afac_file.validate_raw(_afac_bytes(header, ["1", "2"]))
    assert "AGENTE" in caplog.text


def test_afac_preprocess_new_concept(afac_file: AFAC):
    header = ["AGENTE", "DEMANDA REAL (kWh)", " CONCEPTO NUEVO XM ($)"]
    raw = _afac_bytes(header, ["AAGG", "1", "2.5"])
    long_data = afac_file.preprocess(BytesIO(raw))
    assert list(long_data.columns) == ["AGENTE", "CONCEPTO", "VALOR"]
    assert set(long_data["CONCEPTO"]) == {"DEMANDA REAL (kWh)", "CONCEPTO NUEVO XM ($)"}
    assert long_data["VALOR"].dtype == float
    assert long_data.loc[long_data["CONCEPTO"] == "CONCEPTO NUEVO XM ($)", "VALOR"].item() == 2.5


@TESTFILES
def test_afac_validate_raw_local_file(afac_file: AFAC, local_afac_file):
    assert afac_file.validate_raw(local_afac_file.read_bytes())
