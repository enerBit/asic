import datetime as dt
import logging
import typing

import pandas as pd
import pydantic
import requests

from asic import ASIC_FILE_EXTENSION_MAP

logger = logging.getLogger(__name__)

SUPPORTED_ASIC_EXTENSIONS = frozenset(
    [ext.replace(".", "") for ext in ASIC_FILE_EXTENSION_MAP.keys()]
)


class ASICVersionPublication(pydantic.BaseModel):
    month: dt.datetime
    version: pydantic.constr(regex=r"^[a-z0-9]*$")  # type: ignore # noqa: F722
    published_at: dt.datetime


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/80.0.3987.149 Safari/537.36"
)
ASIC_MONTHLY_VERSION_PUBLICATION_SERVICE: dict[str, typing.Any] = {
    "url": "http://sv01.xm.com.co/gmem/Admon_Mcdo/Liquidacion/versionesliq.htm",
    "table-index": 1,
    "encoding": "cp1252",
    "month_settlement_format": r"%b %Y",
    "headers": {"User-Agent": USER_AGENT},
    "table_cols": {
        "month": "MES LIQUIDADO",
        "version": "ULTIMA VERSION LIQUIDADA",
        "published_at": "FECHA DE EMISIÓN/PUBLICACIÓN",
    },
}


def get_daily_versions() -> list[ASICVersionPublication]:
    daily_versions = []
    # TX1
    daily_versions.append(
        ASICVersionPublication(
            month=dt.datetime.combine(dt.date.today(), dt.datetime.min.time())
            + dt.timedelta(days=-1),
            version="tx1",
            published_at=dt.datetime.combine(dt.date.today(), dt.datetime.min.time()),
        )
    )
    # TX2
    daily_versions.append(
        ASICVersionPublication(
            month=dt.datetime.combine(dt.date.today(), dt.datetime.min.time())
            + dt.timedelta(days=-3),
            version="tx2",
            published_at=dt.datetime.combine(dt.date.today(), dt.datetime.min.time()),
        )
    )
    return daily_versions


def get_monthly_pubs_table() -> pd.DataFrame:
    headers: dict[str, str] = ASIC_MONTHLY_VERSION_PUBLICATION_SERVICE["headers"]
    url: str = ASIC_MONTHLY_VERSION_PUBLICATION_SERVICE["url"]
    source_encoding: str = ASIC_MONTHLY_VERSION_PUBLICATION_SERVICE["encoding"]
    table_index: int = ASIC_MONTHLY_VERSION_PUBLICATION_SERVICE["table-index"]

    logger.debug(f"Getting content from '{url}'")
    res = requests.get(url, headers=headers)
    res.raise_for_status()

    html_text = typing.cast(str, res.content)
    logger.debug("Parsing content as HTML table")
    tables = pd.read_html(html_text, flavor="html5lib", encoding=source_encoding)
    versions_table = tables[table_index].dropna().T.drop_duplicates().T
    table_headers = versions_table.iloc[0]
    versions_table = pd.DataFrame(versions_table.values[1:], columns=table_headers)
    versions_table = versions_table.drop(versions_table.index[0])
    return versions_table


def prepare_published_versions_to_objects(
    versions_table: pd.DataFrame,
) -> list[ASICVersionPublication]:
    month_settlement_format = ASIC_MONTHLY_VERSION_PUBLICATION_SERVICE[
        "month_settlement_format"
    ]
    table_cols = ASIC_MONTHLY_VERSION_PUBLICATION_SERVICE["table_cols"]

    # Make sure parsed table has expected structure
    assert list(table_cols.values()) == list(versions_table)

    versions_table[table_cols["month"]] = pd.to_datetime(
        versions_table[table_cols["month"]], format=month_settlement_format
    )

    versions_table[table_cols["published_at"]] = pd.to_datetime(
        versions_table[table_cols["published_at"]], format=r"%Y-%m-%d"
    )

    versions_table[table_cols["version"]] = versions_table[
        table_cols["version"]
    ].str.lower()

    ignored_versions = versions_table[
        ~versions_table[table_cols["version"]].isin(SUPPORTED_ASIC_EXTENSIONS)
    ].copy()

    included_versions = versions_table[
        versions_table[table_cols["version"]].isin(SUPPORTED_ASIC_EXTENSIONS)
    ].copy()

    for row in ignored_versions.iterrows():
        logger.warning(
            f"Published version NOT considered: {row[table_cols['version']]} on {row[table_cols['published_at']]}"
        )

    latest_version_pub = (
        included_versions.sort_values([table_cols["published_at"]], ascending=False)
        .groupby([table_cols["month"]])
        .first()
    ).reset_index()

    latest_version_pub[table_cols["month"]] = (
        latest_version_pub[table_cols["month"]].dt.to_period("M").dt.to_timestamp()
    )
    inv_map = {v: k for k, v in table_cols.items()}
    latest_version_pub = latest_version_pub.rename(columns=inv_map)
    latest_version_pub = latest_version_pub.to_dict(orient="records")
    latest_version_pub_objects = [
        ASICVersionPublication.parse_obj(i) for i in latest_version_pub
    ]
    logger.debug(f"Latest versions len: {len(latest_version_pub_objects)}")
    return latest_version_pub_objects


def list_latest_published_versions(
    published_after: dt.datetime | None = None, include_daily: bool = False
) -> list[ASICVersionPublication]:
    versions_table = get_monthly_pubs_table()
    versions = prepare_published_versions_to_objects(versions_table)
    if include_daily:
        daily_versions = get_daily_versions()
        versions.extend(daily_versions)
    if published_after:
        versions = [v for v in versions if (v.published_at >= published_after)]
    versions = sorted(versions, key=lambda p: (p.published_at, p.month), reverse=True)

    return versions


if __name__ == "__main__":
    published_after = dt.datetime.today() - dt.timedelta(days=90)
    print(f"Keeping settlements published after {published_after}")
    newest_versions = list_latest_published_versions(published_after, True)
    for i in newest_versions:
        print(i)
