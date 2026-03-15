"""spec alignment

Revision ID: 20260315_000002
Revises: 20260310_000001
Create Date: 2026-03-15

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260315_000002"
down_revision = "20260310_000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add timestamps to analyses
    with op.batch_alter_table("cv_analyses") as batch:
        batch.add_column(sa.Column("started_at", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True))

    # Resume scores: add FK + keep nullable behavior conservative for existing data
    with op.batch_alter_table("cv_resume_scores") as batch:
        batch.create_foreign_key(
            "fk_cv_resume_scores_resume_id_cv_resumes",
            "cv_resumes",
            ["resume_id"],
            ["id"],
            ondelete="CASCADE",
        )

    # Indexes
    op.create_index("ix_cv_analyses_resume_id", "cv_analyses", ["resume_id"], unique=False)
    op.create_index("ix_cv_analyses_status", "cv_analyses", ["status"], unique=False)
    op.create_index("ix_cv_resumes_created_at", "cv_resumes", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_cv_resumes_created_at", table_name="cv_resumes")
    op.drop_index("ix_cv_analyses_status", table_name="cv_analyses")
    op.drop_index("ix_cv_analyses_resume_id", table_name="cv_analyses")

    with op.batch_alter_table("cv_resume_scores") as batch:
        batch.drop_constraint("fk_cv_resume_scores_resume_id_cv_resumes", type_="foreignkey")

    with op.batch_alter_table("cv_analyses") as batch:
        batch.drop_column("finished_at")
        batch.drop_column("started_at")
