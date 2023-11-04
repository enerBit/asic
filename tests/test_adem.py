import pathlib

from asic.files.definitions.adem import ADEM
from asic.files.file import AsicFileMetadata


def test_adem_from_remote_path():
    path = pathlib.PurePosixPath(
        "/informacion_xm/PublicoK/SIC/COMERCIA/2023-10/adem1001.Tx2"
    )
    file = ADEM.from_remote_path(path)
    assert file.path == path
    assert file.kind == "adem"
    assert file.year == 2023
    assert file.month == 10
    assert file.day == 1
    assert file.extension == ".tx2"
    assert file.version == "001"
    assert file.agent is None
    assert file.metadata == AsicFileMetadata(
        remote_path=path,
        kind="adem",
        year=2023,
        month=10,
        day=1,
        extension=".tx2",
        version="001",
    )

    # print(file)
    # data = file.read(path)
    # print(data.head(10))
    # prepro_data = file.preprocess(path)
    # print(prepro_data.head(10))
