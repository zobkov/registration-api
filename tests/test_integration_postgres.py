import os

import pytest
from sqlalchemy import text
from sqlalchemy.engine import create_engine


@pytest.mark.integration
def test_postgres_connection_and_table_exists() -> None:
    db_url = os.getenv("TEST_DATABASE_URL")
    if not db_url:
        pytest.skip("Set TEST_DATABASE_URL to run PostgreSQL integration tests")

    engine = create_engine(db_url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT to_regclass('public.site_registrations')"))
        table_name = result.scalar()
        assert table_name == "site_registrations"
