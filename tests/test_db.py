import os
import pytest
from app.db.session import query_db, execute_db
from app.db.init_db import init_database


def setup_module(module):
    """Initializes the database schema and seed data for tests."""
    init_database(force_reseed=True)


def test_database_initialization():
    """Verify that all core tables exist and are accessible."""
    orgs = query_db("SELECT COUNT(*) as count FROM organizations", one=True)
    assert orgs["count"] >= 5, "Organizations table should have seeded organizations"


def test_donations_table():
    """Verify that initial seeded donations exist."""
    donations = query_db("SELECT * FROM donations")
    assert len(donations) >= 3, "Donations table should have seeded donations"
    assert any(d["donation_id"] == "don_1001" for d in donations)


def test_dispatches_table():
    """Verify that seeded dispatches exist."""
    dispatches = query_db("SELECT * FROM dispatches")
    assert len(dispatches) >= 2, "Dispatches table should have seeded dispatches"


def test_custody_ledger_table():
    """Verify custody ledger has genesis and initial blocks."""
    blocks = query_db(
        "SELECT * FROM custody_ledger WHERE donation_id = 'don_1001'")
    assert len(
        blocks) >= 2, "Custody ledger should have seeded blocks for don_1001"
