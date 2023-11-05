import pathlib

from asic.files.definitions.adem import ADEM
from asic.files.file import AsicFileMetadata, VisibilityEnum
from pytest import fixture


@fixture
def adem_remote_path():
    path = pathlib.PurePosixPath(
        "/informacion_xm/PublicoK/SIC/COMERCIA/2023-10/adem1001.Tx2"
    )
    return path


@fixture
def local_asic_file_folder_root():
    return pathlib.Path("./borrar/")


def test_adem_from_remote_path(adem_remote_path):
    path = adem_remote_path
    file = ADEM.from_remote_path(path)
    assert file.path == path
    assert file.kind == "adem"
    assert file.visibility == VisibilityEnum.PUBLIC
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


def test_adem_read(adem_remote_path, local_asic_file_folder_root):
    path = adem_remote_path
    file = ADEM.from_remote_path(path)
    local_file = (
        local_asic_file_folder_root / str(file.path)[1:]
    )  # hack to remove root anchor
    data = file.read(local_file)
    assert len(data) == 232
    # prepro_data = file.preprocess(path)
    # print(prepro_data.head(10))


def test_adem_preprocess(adem_remote_path, local_asic_file_folder_root):
    path = adem_remote_path
    file = ADEM.from_remote_path(path)
    local_file = (
        local_asic_file_folder_root / str(file.path)[1:]
    )  # hack to remove root anchor
    long_data = file.preprocess(local_file)
    assert len(long_data) == 1128
    # prepro_data = file.preprocess(path)
    # print(prepro_data.head(10))
