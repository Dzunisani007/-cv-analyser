"""20260317_approval

Revision ID: 20260317_approval
Revises: 20260315_000003
Create Date: 2026-03-17

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260317_approval'
down_revision = '20260315_000003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # This migration was created for approval workflow but the file was lost
    # Adding workflow_logs relationship to CVAnalysis
    # The actual model change is already in app/models.py
    pass


def downgrade() -> None:
    pass
