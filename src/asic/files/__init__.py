import enum
import pathlib

from ..metadata import FileItemInfo
from .adem import adem_preprocess
from .aenc import aenc_preprocess
from .afac import afac_preprocess
from .balcttos import balcttos_preprocess
from .cliq import cliq_preprocess
from .desbm import desbm_preprocess
from .desbmex import desbmex_preprocess
from .dspcttos import dspcttos_preprocess
from .fronteras import fronteras_preprocess
from .ldcbmr import ldcbmr_preprocess
from .oefagnch import oefagnch_preprocess
from .pep import pep_preprocess
from .pubfc import pubfc_preprocess
from .pubfc_falla_hurto import pubfc_falla_hurto_preprocess
from .sntie import sntie_preprocess
from .tfroc import tfroc_preprocess
from .tgrl import tgrl_preprocess
from .trsd import trsd_preprocess
from .trsm import trsm_preprocess

# from .undefined import undefined_preprocess


class SupportedFiles(str, enum.Enum):
    TGRL = "tgrl", tgrl_preprocess
    AENC = "aenc", aenc_preprocess
    ADEM = "adem", adem_preprocess
    TRSM = "trsm", trsm_preprocess
    LDCBMR = "ldcbmr", ldcbmr_preprocess
    PEP = "pep", pep_preprocess
    TRSD = "trsd", trsd_preprocess
    SNTIE = "sntie", sntie_preprocess
    AFAC = "afac", afac_preprocess
    DSPCTTOS = "dspcttos", dspcttos_preprocess
    PUBFC = "pubfc", pubfc_preprocess
    PUBFC_FALLA_HURTO = "pubfc_falla_hurto", pubfc_falla_hurto_preprocess
    TFROC = "tfroc", tfroc_preprocess
    CLIQ = "cliq", cliq_preprocess
    BALCTTOS = "balcttos", balcttos_preprocess
    DESBM = "desbm", desbm_preprocess
    DESBMEX = "desbmex", desbmex_preprocess
    OEFAGNCH = "oefagnch", oefagnch_preprocess
    FRONTERAS = "fronteras", fronteras_preprocess

    def __new__(cls, code, preprocessor):
        obj = str.__new__(cls, [code])
        obj._value_ = code
        obj.preprocessor = preprocessor
        return obj

    def preprocess(self, filepath: pathlib.Path, item: FileItemInfo):
        return self.preprocessor(filepath, item)


__all__ = ["SupportedFiles"]
