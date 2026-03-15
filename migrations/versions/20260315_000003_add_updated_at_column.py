"""add_updated_at_column

Revision ID: 20260315_000003
Revises: 20260315_000002
Create Date: 2026-03-15

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260315_000003'
down_revision = '20260315_000002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add updated_at column to cv_resume_scores
    op.add_column('cv_resume_scores', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))


def downgrade() -> None:
    # Remove updated_at column from cv_resume_scores
    op.drop_column('cv_resume_scores', 'updated_at')
