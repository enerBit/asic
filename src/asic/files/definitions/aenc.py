import logging
import pathlib

# Third party imports
import pandas as pd

# Local application imports
from asic.reader import FileReader

from ..metadata import FileItemInfo

logger = logging.getLogger(__name__)

aenc_format = {
    "type": "csv",
    "sep": ";",
    "encoding": "cp1252",
    "dt_fields": {},
    "dtype": {
        "CODIGO SIC": str,
        "CODIGO PROPIO": str,
        "TIPO DE AGRUPACIÓN": str,
        "IMPO - EXPO": str,
        "HORA 01": float,
        "HORA 02": float,
        "HORA 03": float,
        "HORA 04": float,
        "HORA 05": float,
        "HORA 06": float,
        "HORA 07": float,
        "HORA 08": float,
        "HORA 09": float,
        "HORA 10": float,
        "HORA 11": float,
        "HORA 12": float,
        "HORA 13": float,
        "HORA 14": float,
        "HORA 15": float,
        "HORA 16": float,
        "HORA 17": float,
        "HORA 18": float,
        "HORA 19": float,
        "HORA 20": float,
        "HORA 21": float,
        "HORA 22": float,
        "HORA 23": float,
        "HORA 24": float,
    },
}


class AENC(FileReader):
    def __init__(self):
        return super().__init__(aenc_format.copy())


def aenc_preprocess(filepath: pathlib.Path, item: FileItemInfo) -> pd.DataFrame:
    """
    AENC: es un archivo diario
    versiones: TX2, TXR, TXF
    VALOR: energia calculada por ASIC para frontera en cada periodo
    """
    ance_reader = AENC()
    total = ance_reader.read(filepath)
    total["FECHA"] = f"{item.year:04d}-{item.month:02d}-{item.day:02d}"
    total["AGENTE"] = item.agent

    total["FECHA"] = pd.to_datetime(
        total["FECHA"],
        format="%Y-%m-%d",
    )
    total = (
        total.set_index(
            [
                "FECHA",
                "AGENTE",
                "CODIGO SIC",
                "CODIGO PROPIO",
                "TIPO DE AGRUPACIÓN",
                "IMPO - EXPO",
            ]
        )
        .stack()
        .reset_index()
    )
    total = total.rename(columns={"level_6": "NOMBRE HORA", 0: "VALOR"})
    total["HORA"] = (total["NOMBRE HORA"].str.slice(start=-2)).astype(int) - 1
    total["HORA"] = pd.to_timedelta(total["HORA"], unit="h")
    total["FECHA_HORA"] = total["FECHA"] + total["HORA"]

    # total = (
    #     total[
    #         ["FECHA", "NOMBRE HORA", "HORA", "FECHA_HORA", "AGENTE", "CODIGO", "VALOR"]
    #     ]
    #     .set_index(["FECHA", "NOMBRE HORA", "HORA", "FECHA_HORA", "AGENTE", "CODIGO"])
    #     .unstack()
    #     .reset_index()
    # )
    # cols = [
    #     f"{l1}_{l0}" if l1 else l0
    #     for (l0, l1) in zip(
    #         total.columns.get_level_values(0), total.columns.get_level_values(1)
    #     )
    # ]
    # total.columns = cols
    return_cols = [
        "FECHA_HORA",
        "AGENTE",
        "CODIGO SIC",
        "CODIGO PROPIO",
        "TIPO DE AGRUPACIÓN",
        "IMPO - EXPO",
        "VALOR",
    ]
    return total[return_cols]


if __name__ == "__main__":
    import pathlib

    aenc_path = pathlib.Path(
        r"C:/Users/pablete/enerbit/enerbit.core.eds/files/aenc0703.Tx2"
    )
    data = AENC().read(aenc_path)
    print(data.head())
    info = FileItemInfo(
        path=aenc_path,
        code="aenc",
        year=2022,
        month=7,
        day=3,
        extension="tx2",
        version="002",
        agent="enbc",
    )
    data_proc = aenc_preprocess(aenc_path, info)
    print(data_proc.sample(5))
