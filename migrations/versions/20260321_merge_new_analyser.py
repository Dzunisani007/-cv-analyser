"""Merge migration for new analyser setup

Revision ID: 20260321_merge_new_analyser
Revises: 20260319_000008, 20260321_new_analyser
Create Date: 2026-03-21

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '20260321_merge_new_analyser'
down_revision = ('20260319_000008', '20260321_new_analyser')
branch_labels = None
depends_on = None


def upgrade() -> None:
    # This is a merge migration - no changes needed
    # Just update alembic version to this merge
    pass


def downgrade() -> None:
    pass
