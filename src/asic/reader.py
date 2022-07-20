# Standard library imports
import logging
from io import StringIO
from pathlib import Path
from typing import Union

# Third party imports
import pandas as pd

# Local application imports
pass

logger = logging.getLogger(__name__)


class FileReader:
    """Base Class for file readers."""

    def __init__(self, file_def: dict) -> None:
        """Create FileReader with file definition."""
        logger.debug(f"Creating FileReader with file definition:\n{file_def}")
        self.file_def = file_def

    def read(self, target: Union[str, Path, StringIO]) -> pd.DataFrame:
        """Reads DataFrame from target."""
        _def = self.file_def
        file_type = _def.pop("type", None)
        dt_fields = _def.pop("dt_fields", None)

        logger.debug(f"Reading as {file_type}: {target}")

        if file_type in ["csv", "txt", "tsv"]:
            res = pd.read_csv(target, **_def)

        elif file_type in ["xls", "xlsx"]:
            if "sheet_name" in _def:
                res = pd.read_excel(str(target), **_def)
            else:
                raise ValueError(
                    "Missing 'sheet_name' in file_def. Can only read one Excel sheet structure per FileReader"
                )

        else:
            raise ValueError(f"Not supported 'type': '{file_type}'")

        if dt_fields is not None:
            res = self._date_converter(res, dt_fields)

        logger.info(f"Read {res.shape[0]} rows and {res.shape[1]} columns")
        # logger.debug(f"Dtypes of result DataFrame:\n{res.dtypes}")
        return res

    def _date_converter(self, df: pd.DataFrame, dt_fields: dict) -> pd.DataFrame:
        for c in dt_fields:
            df[c] = pd.to_datetime(df[c], format=dt_fields[c].get("format"))

        return df
