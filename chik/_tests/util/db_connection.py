from __future__ import annotations

import tempfile
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

import aiosqlite

from chik.util.db_wrapper import DBWrapper2, generate_in_memory_db_uri


@asynccontextmanager
async def DBConnection(
    db_version: int,
    foreign_keys: Optional[bool] = None,
    row_factory: Optional[type[aiosqlite.Row]] = None,
) -> AsyncIterator[DBWrapper2]:
    db_uri = generate_in_memory_db_uri()
    async with DBWrapper2.managed(
        database=db_uri,
        uri=True,
        reader_count=4,
        db_version=db_version,
        foreign_keys=foreign_keys,
        row_factory=row_factory,
    ) as _db_wrapper:
        yield _db_wrapper


@asynccontextmanager
async def PathDBConnection(db_version: int) -> AsyncIterator[DBWrapper2]:
    with tempfile.TemporaryDirectory() as directory:
        db_path = Path(directory).joinpath("db.sqlite")
        async with DBWrapper2.managed(database=db_path, reader_count=4, db_version=db_version) as _db_wrapper:
            yield _db_wrapper
