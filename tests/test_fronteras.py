import logging
import pathlib
from io import BytesIO

import pandas as pd
from pytest import fixture

from asic.files.definitions.fronteras import FRONTERAS

from .conftest import ALL_FILES, TESTFILES


@fixture
def fronteras_remote_path():
    fronteras_path = ALL_FILES["fronteras"]["path"]
    path = pathlib.PureWindowsPath(fronteras_path)
    return path


@fixture
def fronteras_file(fronteras_remote_path):
    path = fronteras_remote_path
    file = FRONTERAS.from_remote_path(path)
    return file


@fixture
def local_fronteras_file(fronteras_file: FRONTERAS, datafiles: pathlib.Path) -> pathlib.Path:
    relative_path = fronteras_file.path.relative_to(fronteras_file.path.anchor)
    local_file = datafiles / relative_path
    assert local_file.is_file()
    return local_file


@TESTFILES
def test_fronteras_read(fronteras_file: FRONTERAS, local_fronteras_file):
    data = fronteras_file.read(local_fronteras_file)
    assert data.shape == (3, 74)
    assert data["Código Propio"].tolist() == ["0012345678", "0022345678", "0032345678"]
    assert pd.api.types.is_datetime64_any_dtype(data["Registrada por primera vez el"])


def test_fronteras_preprocess_empty_sheet(fronteras_file: FRONTERAS, tmp_path: pathlib.Path):
    local_file = tmp_path / fronteras_file.path.name
    with pd.ExcelWriter(local_file) as writer:
        pd.DataFrame().to_excel(writer, sheet_name="Fronteras Comerciales", index=False)
    data = fronteras_file.preprocess(local_file)
    assert data.empty
    assert list(data.columns) == ["FECHA"]


@TESTFILES
def test_fronteras_preprocess(fronteras_file: FRONTERAS, local_fronteras_file):
    data = fronteras_file.preprocess(local_fronteras_file)
    assert data.shape == (3, 75)
    assert data.columns[0] == "FECHA"
    assert (data["FECHA"] == pd.Timestamp("2026-09-01")).all()


def _xlsx(df: pd.DataFrame, sheet: str = "Fronteras Comerciales") -> bytes:
    buf = BytesIO()
    df.to_excel(buf, sheet_name=sheet, index=False)
    return buf.getvalue()


def _fronteras_data(local_file: pathlib.Path) -> pd.DataFrame:
    return pd.read_excel(local_file, sheet_name="Fronteras Comerciales", dtype=str)


@TESTFILES
def test_fronteras_validate_raw_local_file(fronteras_file: FRONTERAS, local_fronteras_file, caplog):
    with caplog.at_level(logging.WARNING, logger="asic.files.file"):
        assert fronteras_file.validate_raw(local_fronteras_file.read_bytes())
    assert caplog.text == ""


@TESTFILES
def test_fronteras_validate_raw_missing_required(
    fronteras_file: FRONTERAS, local_fronteras_file, caplog
):
    data = _fronteras_data(local_fronteras_file).drop(columns=["Código SIC"])
    with caplog.at_level(logging.ERROR, logger="asic.files.file"):
        assert not fronteras_file.validate_raw(_xlsx(data))
    assert "Código SIC" in caplog.text


@TESTFILES
def test_fronteras_validate_raw_extra_column(
    fronteras_file: FRONTERAS, local_fronteras_file, caplog
):
    data = _fronteras_data(local_fronteras_file).assign(**{"Columna Nueva XM": "x"})
    with caplog.at_level(logging.WARNING, logger="asic.files.file"):
        assert fronteras_file.validate_raw(_xlsx(data))
    assert "Columna Nueva XM" in caplog.text


@TESTFILES
def test_fronteras_validate_raw_wrong_sheet(fronteras_file: FRONTERAS, local_fronteras_file):
    data = _fronteras_data(local_fronteras_file)
    assert not fronteras_file.validate_raw(_xlsx(data, sheet="Hoja1"))


def test_fronteras_validate_raw_not_excel(fronteras_file: FRONTERAS):
    assert not fronteras_file.validate_raw(b"Codigo SIC;NIU\nFRT00001;123\n")


def test_fronteras_validate_raw_empty_sheet(fronteras_file: FRONTERAS):
    assert not fronteras_file.validate_raw(_xlsx(pd.DataFrame()))


@TESTFILES
def test_fronteras_validate_raw_header_only(fronteras_file: FRONTERAS, local_fronteras_file):
    data = _fronteras_data(local_fronteras_file).iloc[0:0]
    assert fronteras_file.validate_raw(_xlsx(data))


@TESTFILES
def test_fronteras_preprocess_bytesio(fronteras_file: FRONTERAS, local_fronteras_file):
    from_path = fronteras_file.preprocess(local_fronteras_file)
    from_bytes = fronteras_file.preprocess(BytesIO(local_fronteras_file.read_bytes()))
    assert from_bytes.equals(from_path)
