"""initial PostgreSQL schema

Revision ID: 0001_initial
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    json_type = sa.JSON().with_variant(sa.dialects.postgresql.JSONB(), "postgresql")
    op.create_table("brands", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(120), nullable=False, unique=True), sa.Column("official_domain", sa.String(253), nullable=False, unique=True), sa.Column("aliases", json_type, nullable=False), sa.Column("sector", sa.String(80)), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("scans", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("submitted_url", sa.Text(), nullable=False), sa.Column("normalized_domain", sa.String(253), nullable=False), sa.Column("brand_id", sa.Integer(), sa.ForeignKey("brands.id")), sa.Column("brand_confidence", sa.Float(), nullable=False), sa.Column("risk_score", sa.Float(), nullable=False), sa.Column("risk_level", sa.String(16), nullable=False), sa.Column("status", sa.String(20), nullable=False), sa.Column("model_version", sa.String(80), nullable=False), sa.Column("evidence", json_type, nullable=False), sa.Column("explanation", json_type, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_scans_risk_created", "scans", ["risk_score", "created_at"])
    op.create_table("audit_log", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("event_type", sa.String(80), nullable=False), sa.Column("scan_id", sa.Integer(), sa.ForeignKey("scans.id")), sa.Column("payload", json_type, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))


def downgrade():
    op.drop_table("audit_log")
    op.drop_index("ix_scans_risk_created", table_name="scans")
    op.drop_table("scans")
    op.drop_table("brands")
