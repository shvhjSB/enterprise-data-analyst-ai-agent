"""Schema models & semantic enrichment.

This is where we normalize SQLAlchemy-reflected metadata into a compact snapshot
used by agents. Also detects simple semantic properties.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple

from pydantic import BaseModel, Field
from sqlalchemy import MetaData


class ColumnInfo(BaseModel):
    name: str
    type: str
    nullable: bool
    is_pk: bool = False
    is_fk: bool = False


class ForeignKeyInfo(BaseModel):
    column: str
    referred_table: str
    referred_column: str


class TableInfo(BaseModel):
    name: str
    columns: List[ColumnInfo]
    foreign_keys: List[ForeignKeyInfo] = Field(default_factory=list)
    indexes: List[str] = Field(default_factory=list)

    # semantic hints
    is_fact: bool = False
    is_dimension: bool = False
    time_columns: List[str] = Field(default_factory=list)
    measures: List[str] = Field(default_factory=list)
    attributes: List[str] = Field(default_factory=list)


class SchemaSnapshot(BaseModel):
    tables: List[TableInfo]

    @property
    def table_count(self) -> int:
        return len(self.tables)

    @property
    def column_count(self) -> int:
        return sum(len(t.columns) for t in self.tables)

    def table_names(self) -> List[str]:
        return [t.name for t in self.tables]

    def all_column_names(self) -> List[str]:
        out: List[str] = []
        for t in self.tables:
            for c in t.columns:
                out.append(f"{t.name}.{c.name}")
        return out


_TIME_KEYWORDS = ("date", "time", "timestamp", "created", "updated")
_MEASURE_KEYWORDS = ("amount", "total", "price", "cost", "revenue", "qty", "quantity")


def build_schema_snapshot(md: MetaData) -> SchemaSnapshot:
    tables: List[TableInfo] = []

    # map pk->table heuristic for facts/dimensions
    for table_name, table in md.tables.items():
        cols: List[ColumnInfo] = []
        fks: List[ForeignKeyInfo] = []

        pk_cols = {c.name for c in table.primary_key.columns} if table.primary_key else set()

        for c in table.columns:
            is_fk = bool(c.foreign_keys)
            cols.append(
                ColumnInfo(
                    name=c.name,
                    type=str(c.type),
                    nullable=bool(c.nullable),
                    is_pk=c.name in pk_cols,
                    is_fk=is_fk,
                )
            )
            for fk in c.foreign_keys:
                fks.append(
                    ForeignKeyInfo(
                        column=c.name,
                        referred_table=fk.column.table.name,
                        referred_column=fk.column.name,
                    )
                )

        idx_names = [ix.name or "" for ix in getattr(table, "indexes", [])]

        tinfo = TableInfo(name=table_name, columns=cols, foreign_keys=fks, indexes=idx_names)

        # semantic enrichment
        col_names = [c.name.lower() for c in cols]
        tinfo.time_columns = [
            cols[i].name for i, n in enumerate(col_names) if any(k in n for k in _TIME_KEYWORDS)
        ]
        tinfo.measures = [
            cols[i].name for i, n in enumerate(col_names) if any(k in n for k in _MEASURE_KEYWORDS)
        ]
        tinfo.attributes = [c.name for c in cols if c.name not in tinfo.measures]

        # rough star-schema heuristics:
        fk_count = sum(1 for c in cols if c.is_fk)
        if fk_count >= 2 and any(m for m in tinfo.measures):
            tinfo.is_fact = True
        elif fk_count <= 1 and not any(m for m in tinfo.measures):
            tinfo.is_dimension = True

        tables.append(tinfo)

    return SchemaSnapshot(tables=tables)