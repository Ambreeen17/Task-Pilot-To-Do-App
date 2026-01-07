import os

import pytest


@pytest.mark.skipif(
    not os.getenv("DATABASE_URL") or not os.getenv("DATABASE_URL").startswith("postgres"),
    reason="DATABASE_URL not set to a Postgres URL",
)
def test_postgres_smoke_database_url_is_postgres():
    # This is intentionally a minimal, env-gated smoke check.
    # A full Postgres integration test would require a running Postgres instance.
    assert os.getenv("DATABASE_URL", "").startswith("postgres")
