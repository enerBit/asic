import pathlib

from ..metadata import FileItemInfo


def undefined_preprocess(
    filepath: pathlib.Path, item: FileItemInfo | None = None
) -> None:
    raise NotImplementedError
