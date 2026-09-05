"""add lawyer analysis results

Revision ID: 20260822_01
Revises:
Create Date: 2026-08-22
"""

from alembic import op
import sqlalchemy as sa

revision = "20260822_01"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "lawyer_analysis_results",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("case_id", sa.String(), nullable=True),
        sa.Column("analysis_type", sa.Enum("ADVANCED_RESEARCH", "ARGUMENT_RESEARCH", "CITATION_FINDER", "CASE_BRIEF", name="lawyeranalysistype"), nullable=False),
        sa.Column("query", sa.Text(), nullable=True),
        sa.Column("result_json", sa.Text(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_lawyer_analysis_results_user_id", "lawyer_analysis_results", ["user_id"])
    op.create_index("ix_lawyer_analysis_results_case_id", "lawyer_analysis_results", ["case_id"])
    op.create_index("ix_lawyer_analysis_results_analysis_type", "lawyer_analysis_results", ["analysis_type"])


def downgrade():
    op.drop_index("ix_lawyer_analysis_results_analysis_type", table_name="lawyer_analysis_results")
    op.drop_index("ix_lawyer_analysis_results_case_id", table_name="lawyer_analysis_results")
    op.drop_index("ix_lawyer_analysis_results_user_id", table_name="lawyer_analysis_results")
    op.drop_table("lawyer_analysis_results")
