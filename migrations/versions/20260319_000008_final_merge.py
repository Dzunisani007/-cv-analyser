"""Final merge migration for CV analyser

Revision ID: 20260319_000008
Revises: 20260319_000005, 20260319_000006, 20260319_000007, 52f5afe21ced
Create Date: 2026-03-19 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260319_000008'
down_revision = ('20260319_000005', '20260319_000006', '20260319_000007', '52f5afe21ced')
branch_labels = None
depends_on = None


def upgrade() -> None:
    # This is a merge migration - no changes needed
    # Just update the alembic version to this merge
    pass


def downgrade() -> None:
    pass
