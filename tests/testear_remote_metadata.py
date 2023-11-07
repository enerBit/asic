# import pathlib

# import pytest
# from asic.files.metadata import FileItemInfo, extract_metadata_from_remote_path


# def test_xlsx_ext_path_without_as():
#     str_path = r"/informacion_xm/publicok/sic/comercia/Fronteras_en_proceso_de_registro/PUB_Registros/PubFC2023-05-01.xlsx"
#     path = pathlib.PurePath(str_path)
#     fii = FileItemInfo(
#         path=path,
#         year=2023,
#         month=5,
#         day=1,
#         extension=".xlsx",
#         code="pubfc",
#         version=None,
#         agent=None,
#     )
#     assert extract_metadata_from_remote_path(path).model_dump() == fii.model_dump()


# def test_monthly_path_without_as():
#     str_path = r"\informacion_xm\publicok\sic\comercia\2023-05\sntie05.txf"
#     path = pathlib.PurePath(str_path)
#     fii = FileItemInfo(
#         path=path,
#         year=2023,
#         month=5,
#         day=None,
#         extension=".txf",
#         code="sntie",
#         version="003",
#         agent=None,
#     )
#     assert extract_metadata_from_remote_path(path).model_dump() == fii.model_dump()


# def test_beyond_txf_path_without_as():
#     str_path = r"\informacion_xm\publicok\sic\comercia\2023-05\sntie05.tx3"
#     path = pathlib.PurePath(str_path)
#     fii = FileItemInfo(
#         path=path,
#         year=2023,
#         month=5,
#         day=None,
#         extension=".tx3",
#         code="sntie",
#         version="004",
#         agent=None,
#     )
#     assert extract_metadata_from_remote_path(path).model_dump() == fii.model_dump()


# def test_extension_txa_path_without_as():
#     str_path = r"\informacion_xm\publicok\sic\comercia\2023-05\afac05.txa"
#     path = pathlib.PurePath(str_path)

#     with pytest.raises(ValueError, match=r"Unsupported extension '.txa'"):
#         extract_metadata_from_remote_path(path)


# def test_adem_path_without_as():
#     str_path = r"\informacion_xm\publicok\sic\comercia\2023-05\adem0511.TxR"
#     path = pathlib.PurePath(str_path)
#     fii = FileItemInfo(
#         path=path,
#         year=2023,
#         month=5,
#         day=11,
#         extension=".txr",
#         code="adem",
#         version="002",
#         agent=None,
#     )
#     assert extract_metadata_from_remote_path(path).model_dump() == fii.model_dump()


# def test_trsd_path_without_as():
#     str_path = r"\informacion_xm\publicok\sic\comercia\2023-05\trsd0502.tx2"
#     path = pathlib.PurePath(str_path)
#     fii = FileItemInfo(
#         path=path,
#         year=2023,
#         month=5,
#         day=2,
#         extension=".tx2",
#         code="trsd",
#         version="001",
#         agent=None,
#     )
#     assert extract_metadata_from_remote_path(path).model_dump() == fii.model_dump()


# def test_tgrl_path_without_as():
#     str_path = r"\informacion_xm\publicok\sic\comercia\2023-05\tgrl0531.txf"
#     path = pathlib.PurePath(str_path)
#     fii = FileItemInfo(
#         path=path,
#         year=2023,
#         month=5,
#         day=31,
#         extension=".txf",
#         code="tgrl",
#         version="003",
#         agent=None,
#     )
#     assert extract_metadata_from_remote_path(path).model_dump() == fii.model_dump()


# def test_pep_path_without_as():
#     str_path = r"\informacion_xm\publicok\sic\comercia\2023-05\pep0501.tx1"
#     path = pathlib.PurePath(str_path)
#     fii = FileItemInfo(
#         path=path,
#         year=2023,
#         month=5,
#         day=1,
#         extension=".tx1",
#         code="pep",
#         version="000",
#         agent=None,
#     )
#     assert extract_metadata_from_remote_path(path).model_dump() == fii.model_dump()


# def test_sntie_path_without_as():
#     str_path = r"\informacion_xm\publicok\sic\comercia\2023-05\sntie05.txf"
#     path = pathlib.PurePath(str_path)
#     fii = FileItemInfo(
#         path=path,
#         year=2023,
#         month=5,
#         day=None,
#         extension=".txf",
#         code="sntie",
#         version="003",
#         agent=None,
#     )
#     assert extract_metadata_from_remote_path(path).model_dump() == fii.model_dump()


# def test_afac_path_without_as():
#     str_path = r"\informacion_xm\publicok\sic\comercia\2023-05\afac05.txf"
#     path = pathlib.PurePath(str_path)
#     fii = FileItemInfo(
#         path=path,
#         year=2023,
#         month=5,
#         day=None,
#         extension=".txf",
#         code="afac",
#         version="003",
#         agent=None,
#     )
#     assert extract_metadata_from_remote_path(path).model_dump() == fii.model_dump()


# def test_trsm_path_without_as():
#     str_path = r"\informacion_xm\publicok\sic\comercia\2023-05\trsm05.txf"
#     path = pathlib.PurePath(str_path)
#     fii = FileItemInfo(
#         path=path,
#         year=2023,
#         month=5,
#         day=None,
#         extension=".txf",
#         code="trsm",
#         version="003",
#         agent=None,
#     )
#     assert extract_metadata_from_remote_path(path).model_dump() == fii.model_dump()


# def test_ldcbmr_path_without_as():
#     str_path = r"\informacion_xm\publicok\sic\comercia\2023-05\ldcbmr05.txf"
#     path = pathlib.PurePath(str_path)
#     fii = FileItemInfo(
#         path=path,
#         year=2023,
#         month=5,
#         day=None,
#         extension=".txf",
#         code="ldcbmr",
#         version="003",
#         agent=None,
#     )
#     assert extract_metadata_from_remote_path(path).model_dump() == fii.model_dump()


# def test_dspcttos_path_without_as():
#     str_path = r"\informacion_xm\usuariosk\enbc\sic\comercia\2023-05\dspcttos0501.tx2"
#     path = pathlib.PurePath(str_path)
#     fii = FileItemInfo(
#         path=path,
#         year=2023,
#         month=5,
#         day=1,
#         extension=".tx2",
#         code="dspcttos",
#         version="001",
#         agent="enbc",
#     )
#     assert extract_metadata_from_remote_path(path).model_dump() == fii.model_dump()


# def test_aenc_path_without_as():
#     str_path = r"\informacion_xm\usuariosk\enbc\sic\comercia\2023-05\aenc0501.Tx2"
#     path = pathlib.PurePath(str_path)
#     fii = FileItemInfo(
#         path=path,
#         year=2023,
#         month=5,
#         day=1,
#         extension=".tx2",
#         code="aenc",
#         version="001",
#         agent="enbc",
#     )
#     assert extract_metadata_from_remote_path(path).model_dump() == fii.model_dump()


# def test_pubfc_path_without_as():
#     str_path = r"/informacion_xm/publicok/sic/comercia/Fronteras_en_proceso_de_registro/PUB_Registros/PubFC2023-05-01.xlsx"
#     path = pathlib.PurePath(str_path)
#     fii = FileItemInfo(
#         path=path,
#         year=2023,
#         month=5,
#         day=1,
#         extension=".xlsx",
#         code="pubfc",
#         version=None,
#         agent=None,
#     )
#     assert extract_metadata_from_remote_path(path).model_dump() == fii.model_dump()


# def test_pubfc_falla_hurto_path_without_as():
#     str_path = r"/informacion_xm/publicok/sic/comercia/Fronteras_en_proceso_de_registro/PUB_Falla_Hurto/PubFC_Falla-Hurto2023-05-01.xlsx"
#     path = pathlib.PurePath(str_path)
#     fii = FileItemInfo(
#         path=path,
#         year=2023,
#         month=5,
#         day=1,
#         extension=".xlsx",
#         code="pubfc_falla-hurto",
#         version=None,
#         agent=None,
#     )
#     assert extract_metadata_from_remote_path(path).model_dump() == fii.model_dump()


# def test_fronteras_path_without_as():
#     str_path = r"/informacion_xm/usuariosk/enbc/SIC/Fronteras/2023-05/ENBC_FronterasComerciales_02-05-2023.xlsx"
#     path = pathlib.PurePath(str_path)
#     fii = FileItemInfo(
#         path=path,
#         year=2023,
#         month=5,
#         day=2,
#         extension=".xlsx",
#         code="fronterascomerciales",
#         version=None,
#         agent="enbc",
#     )
#     assert extract_metadata_from_remote_path(path).model_dump() == fii.model_dump()
