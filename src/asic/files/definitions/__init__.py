from asic.files.definitions.adem import ADEM
from asic.files.file import FileKind

SUPPORTED_FILE_CLASSES = {FileKind.ADEM: ADEM}


__all__ = [c.__name__ for c in SUPPORTED_FILE_CLASSES]
