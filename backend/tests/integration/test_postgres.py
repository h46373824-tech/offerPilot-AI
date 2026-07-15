import os
from uuid import uuid4

import pytest
from sqlalchemy import JSON, Column, Integer, MetaData, String, Table, create_engine, select

pytestmark = pytest.mark.integration


def test_postgresql_round_trip_and_json() -> None:
    url = os.getenv("TEST_POSTGRES_URL")
    if not url:
        pytest.skip("TEST_POSTGRES_URL is not configured")
    engine = create_engine(url, pool_pre_ping=True)
    metadata = MetaData()
    table_name = f"phase2_integration_{uuid4().hex[:10]}"
    sample = Table(
        table_name,
        metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String(100), nullable=False),
        Column("criteria", JSON, nullable=False),
    )
    try:
        metadata.create_all(engine)
        with engine.begin() as connection:
            connection.execute(sample.insert().values(name="上海技术岗", criteria={"city": "上海"}))
            row = connection.execute(select(sample.c.name, sample.c.criteria)).one()
            assert row.name == "上海技术岗"
            assert row.criteria == {"city": "上海"}
    finally:
        metadata.drop_all(engine)
        engine.dispose()
