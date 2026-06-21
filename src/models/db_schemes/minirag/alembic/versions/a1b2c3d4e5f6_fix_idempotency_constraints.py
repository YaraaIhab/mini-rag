"""
fix idempotency constraints - add unique on task_name+args_hash
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '5fcebe5d930a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    indexes = [i["name"] for i in inspector.get_indexes("celery_task_execution")]

    # SAFE DROP (only if exists)
    if "ixz_task_name_args_celery_hash" in indexes:
        op.drop_index(
            "ixz_task_name_args_celery_hash",
            table_name="celery_task_execution"
        )

    # Add unique constraint on (task_name, task_args_hash)
    op.create_unique_constraint(
        "uxz_task_name_args_hash_unique",
        "celery_task_execution",
        ["task_name", "task_args_hash"]
    )

    # Make celery_task_id unique separately
    op.create_unique_constraint(
        "uxz_celery_task_id_unique",
        "celery_task_execution",
        ["celery_task_id"]
    )


def downgrade() -> None:
    op.drop_constraint(
        "uxz_celery_task_id_unique",
        "celery_task_execution",
        type_="unique"
    )

    op.drop_constraint(
        "uxz_task_name_args_hash_unique",
        "celery_task_execution",
        type_="unique"
    )

    # SAFE RECREATE
    op.create_index(
        "ixz_task_name_args_celery_hash",
        "celery_task_execution",
        ["task_name", "task_args_hash", "celery_task_id"],
        unique=True
    )