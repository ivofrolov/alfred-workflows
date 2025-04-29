#!/usr/bin/python3

import re
from pathlib import Path
import plistlib
import sqlite3


APPS_PATHS = ("/Applications", "/System/Applications")

ALFRED_FILECACHE_PATH = "~/Library/Application Support/Alfred/Databases/filecache.alfdb"


def iter_apps(path):
    for child in path.iterdir():
        if child.is_dir():
            if child.suffix == ".app":
                yield child
            else:
                yield from iter_apps(child)


def get_app_data(path):
    info_plist_path = path / "Contents" / "Info.plist"
    with info_plist_path.open("rb") as file:
        info = plistlib.load(file)
    return {
        "path": str(path),
        "file_name": path.name,
        "name": path.stem,
        "name_search": " " + path.stem,
        "name_split": " " + " ".join(re.findall(r"[A-Z][a-z]+", path.stem)).lower(),
        "name_chars": "".join(re.findall(r"[A-Z]", path.stem)),
        "altnames": " " + ", ".join(info.get("CFBundleAlternateNames", "")),
    }


def update_record(connection, app_data):
    cursor = connection.execute(
        "SELECT 1 FROM files WHERE fileName = :file_name",
        app_data,
    )
    if cursor.fetchone():
        return

    connection.execute(
        "INSERT INTO files (path, fileName, name, nameSearch, nameSplit, nameChars, altnames, filetype) "
        "VALUES (:path, :file_name, :name, :name_search, :name_split, :name_chars, :altnames, 1)",
        app_data,
    )
    connection.commit()


def update_filecache():
    connection = sqlite3.connect(Path(ALFRED_FILECACHE_PATH).expanduser())
    try:
        for path in APPS_PATHS:
            for app in iter_apps(Path(path).expanduser()):
                app_data = get_app_data(app)
                update_record(connection, app_data)
    finally:
        connection.close()


if __name__ == "__main__":
    update_filecache()
