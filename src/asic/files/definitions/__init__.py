from typing import Type

from asic.files.definitions.adem import ADEM
from asic.files.definitions.aenc import AENC
from asic.files.definitions.balcttos import BALCTTOS
from asic.files.file import AsicFile, FileKind

SUPPORTED_FILE_CLASSES: dict[FileKind, Type[AsicFile]] = {
    FileKind.ADEM: ADEM,
    FileKind.AENC: AENC,
    FileKind.BALCTTOS: BALCTTOS,
}


__all__ = [str(c) for c in SUPPORTED_FILE_CLASSES]
