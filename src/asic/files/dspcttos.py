import logging
import pathlib

# Third party imports
import pandas as pd

# Local application imports
from asic.reader import FileReader

from ..metadata import FileItemInfo

logger = logging.getLogger(__name__)

dspcttos_format = {
    "type": "csv",
    "sep": ";",
    "encoding": "cp1252",
    "dt_fields": {},
    "dtype": {
        "CONTRATO": str,
        "VENDEDOR": str,
        "COMPRADOR": str,
        "TIPO": str,
        "TIPOMERC": str,
        "DESP_HORA 01": float,
        "DESP_HORA 02": float,
        "DESP_HORA 03": float,
        "DESP_HORA 04": float,
        "DESP_HORA 05": float,
        "DESP_HORA 06": float,
        "DESP_HORA 07": float,
        "DESP_HORA 08": float,
        "DESP_HORA 09": float,
        "DESP_HORA 10": float,
        "DESP_HORA 11": float,
        "DESP_HORA 12": float,
        "DESP_HORA 13": float,
        "DESP_HORA 14": float,
        "DESP_HORA 15": float,
        "DESP_HORA 16": float,
        "DESP_HORA 17": float,
        "DESP_HORA 18": float,
        "DESP_HORA 19": float,
        "DESP_HORA 20": float,
        "DESP_HORA 21": float,
        "DESP_HORA 22": float,
        "DESP_HORA 23": float,
        "DESP_HORA 24": float,
        "TRF_HORA 01": float,
        "TRF_HORA 02": float,
        "TRF_HORA 03": float,
        "TRF_HORA 04": float,
        "TRF_HORA 05": float,
        "TRF_HORA 06": float,
        "TRF_HORA 07": float,
        "TRF_HORA 08": float,
        "TRF_HORA 09": float,
        "TRF_HORA 10": float,
        "TRF_HORA 11": float,
        "TRF_HORA 12": float,
        "TRF_HORA 13": float,
        "TRF_HORA 14": float,
        "TRF_HORA 15": float,
        "TRF_HORA 16": float,
        "TRF_HORA 17": float,
        "TRF_HORA 18": float,
        "TRF_HORA 19": float,
        "TRF_HORA 20": float,
        "TRF_HORA 21": float,
        "TRF_HORA 22": float,
        "TRF_HORA 23": float,
        "TRF_HORA 24": float,
    },
}


class DSPCTTOS(FileReader):
    def __init__(self):
        return super().__init__(dspcttos_format.copy())


def dspcttos_preprocess(filepath: pathlib.Path, item: FileItemInfo) -> pd.DataFrame:
    """
    DSPCTTOS: se publica un archivo por dia.
    versiones: TX2, TXR, TXF
    COMPRADOR:
        EPSC: aqui despues va enerbit
    TIPOMERC:
        R: Regulada
    """
    dspcttos_reader = DSPCTTOS()
    total = dspcttos_reader.read(filepath)
    total["FECHA"] = f"{item.year:04d}-{item.month:02d}-{item.day:02d}"

    total = total[(total["COMPRADOR"] == item.agent) & (total["TIPOMERC"] == "R")]

    total["FECHA"] = pd.to_datetime(
        total["FECHA"],
        format="%Y-%m-%d",
    )
    total = (
        total.set_index(
            ["FECHA", "CONTRATO", "VENDEDOR", "COMPRADOR", "TIPO", "TIPOMERC"]
        )
        .stack()
        .reset_index()
    )

    total = total.rename(columns={"level_6": "NOMBRE HORA", 0: "VALOR"})
    total["CONCEPTO"] = total["NOMBRE HORA"].apply(lambda x: x.split("_")[0])
    total["HORA"] = (total["NOMBRE HORA"].str.slice(start=-2)).astype(int) - 1
    total["HORA"] = pd.to_timedelta(total["HORA"], unit="h")
    total["FECHA_HORA"] = total["FECHA"] + total["HORA"]

    total = (
        total[
            [
                "FECHA",
                "HORA",
                "FECHA_HORA",
                "CONTRATO",
                "VENDEDOR",
                "COMPRADOR",
                "TIPO",
                "TIPOMERC",
                "CONCEPTO",
                "VALOR",
            ]
        ]
        .set_index(
            [
                "FECHA",
                "HORA",
                "FECHA_HORA",
                "CONTRATO",
                "VENDEDOR",
                "COMPRADOR",
                "TIPO",
                "TIPOMERC",
                "CONCEPTO",
            ]
        )
        .unstack()
        .reset_index()
    )
    cols = [
        f"{l1}_{l0}" if l1 else l0
        for (l0, l1) in zip(
            total.columns.get_level_values(0), total.columns.get_level_values(1)
        )
    ]
    total.columns = cols

    ret_cols = [
        "FECHA_HORA",
        "CONTRATO",
        "VENDEDOR",
        "COMPRADOR",
        "TIPO",
        "TIPOMERC",
        "DESP_VALOR",
        "TRF_VALOR",
    ]
    return total[ret_cols]
