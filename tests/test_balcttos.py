import pathlib

from asic.files.definitions.balcttos import BALCTTOS
from asic.files.file import AsicFileMetadata, VisibilityEnum
from pytest import fixture


@fixture
def balcttos_remote_path():
    path = pathlib.PurePosixPath(
        "/INFORMACION_XM/USUARIOSK/enbc/SIC/COMERCIA/2023-10/BalCttos1001.tx2"
    )
    return path


@fixture
def local_asic_file_folder_root():
    return pathlib.Path("./borrar/")


def test_balcttos_from_remote_path(balcttos_remote_path):
    path = balcttos_remote_path
    file = BALCTTOS.from_remote_path(path)
    assert file.path == path
    assert file.kind == "balcttos"
    assert file.visibility == VisibilityEnum.AGENT
    assert file.year == 2023
    assert file.month == 10
    assert file.day == 1
    assert file.extension == ".tx2"
    assert file.version == "001"
    assert file.agent == "enbc"
    assert file.metadata == AsicFileMetadata(
        remote_path=path,
        kind="balcttos",
        year=2023,
        month=10,
        day=1,
        extension=".tx2",
        version="001",
        agent="enbc",
    )


def test_balcttos_read(balcttos_remote_path, local_asic_file_folder_root):
    path = balcttos_remote_path
    file = BALCTTOS.from_remote_path(path)
    local_file = (
        local_asic_file_folder_root / str(file.path)[1:]
    )  # hack to remove root anchor
    data = file.read(local_file)
    assert len(data) == 12
    # prepro_data = file.preprocess(path)
    # print(prepro_data.head(10))


def test_balcttos_preprocess(balcttos_remote_path, local_asic_file_folder_root):
    path = balcttos_remote_path
    file = BALCTTOS.from_remote_path(path)
    local_file = (
        local_asic_file_folder_root / str(file.path)[1:]
    )  # hack to remove root anchor
    long_data = file.preprocess(local_file)
    assert len(long_data) == 288
    # prepro_data = file.preprocess(path)
    # print(prepro_data.head(10))
