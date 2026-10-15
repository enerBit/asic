from io import BytesIO

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
