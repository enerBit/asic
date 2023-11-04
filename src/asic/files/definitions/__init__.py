from asic.files.definitions.adem import ADEM
from asic.files.definitions.aenc import AENC
from asic.files.file import FileKind

SUPPORTED_FILE_CLASSES = {FileKind.ADEM: ADEM, FileKind.AENC: AENC}


__all__ = [c.__name__ for c in SUPPORTED_FILE_CLASSES]
