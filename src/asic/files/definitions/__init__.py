from typing import Type

from asic.files.definitions.adem import ADEM
from asic.files.definitions.aenc import AENC
from asic.files.definitions.balcttos import BALCTTOS
from asic.files.definitions.pep import PEP
from asic.files.definitions.pme import PME
from asic.files.definitions.ptb import PTB
from asic.files.definitions.trsd import TRSD
from asic.files.definitions.tfroc import TFROC
from asic.files.definitions.tgrl import TGRL
from asic.files.definitions.tserv import TSERV
from asic.files.definitions.trsm import TRSM
from asic.files.definitions.sntie import SNTIE
from asic.files.definitions.afac import AFAC
from asic.files.definitions.dspcttos import DSPCTTOS
from asic.files.file import AsicFile, FileKind

SUPPORTED_FILE_CLASSES: dict[FileKind, Type[AsicFile]] = {
    FileKind.ADEM: ADEM,
    FileKind.AENC: AENC,
    FileKind.BALCTTOS: BALCTTOS,
    FileKind.PEP: PEP,
    FileKind.PME: PME,
    FileKind.TRSD: TRSD,
    FileKind.TFROC: TFROC,
    FileKind.TGRL: TGRL,
    FileKind.TSERV: TSERV,
    FileKind.TRSM: TRSM,
    FileKind.SNTIE: SNTIE,
    FileKind.AFAC: AFAC,
    FileKind.DSPCTTOS: DSPCTTOS,
    FileKind.PTB: PTB,
}


__all__ = [str(c) for c in SUPPORTED_FILE_CLASSES]
