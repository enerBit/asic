from io import BytesIO

import pandas as pd

from asic.reader import FileReader


def test_read_fallback_encoding_with_bytesio():
    # byte 0x80 = € en cp1252, inválido en utf-8 — reproduce el bug del cursor no reseteado
    csv_bytes = b"CODIGO;VALOR\nA\x80B;1.0\n"
    target = BytesIO(csv_bytes)

    reader = FileReader({
        "type": "csv",
        "sep": ";",
        "encoding": "utf-8-sig",
        "dtype": {"CODIGO": str, "VALOR": float},
    })
    df = reader.read(target)

    assert len(df) == 1
    assert df["CODIGO"].iloc[0] == "A€B"
    assert df["VALOR"].iloc[0] == 1.0


def test_read_primary_encoding_cp1252():
    # Verifica que cp1252 es el camino primario y no necesita fallback
    csv_bytes = "CODIGO;VALOR\nA€B;1.0\n".encode("cp1252")
    target = BytesIO(csv_bytes)

    reader = FileReader({
        "type": "csv",
        "sep": ";",
        "encoding": "cp1252",
        "dtype": {"CODIGO": str, "VALOR": float},
    })
    df = reader.read(target)

    assert len(df) == 1
    assert df["CODIGO"].iloc[0] == "A€B"
    assert df["VALOR"].iloc[0] == 1.0


def test_read_excel_from_bytesio_and_path(tmp_path):
    data = pd.DataFrame({"CODIGO": ["0012", "0034"], "VALOR": [1.5, 2.0]})
    local_file = tmp_path / "data.xlsx"
    data.to_excel(local_file, sheet_name="Datos", index=False)

    reader = FileReader({
        "type": "xlsx",
        "sheet_name": "Datos",
        "dtype": {"CODIGO": str},
    })
    from_path = reader.read(local_file)
    from_bytes = reader.read(BytesIO(local_file.read_bytes()))

    assert from_bytes.equals(from_path)
    assert from_bytes["CODIGO"].tolist() == ["0012", "0034"]
