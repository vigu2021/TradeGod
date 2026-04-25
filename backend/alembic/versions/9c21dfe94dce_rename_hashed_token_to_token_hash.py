"""rename hashed_token to token_hash

Revision ID: 9c21dfe94dce
Revises: 59126aa48ee8
Create Date: 2026-04-25 17:17:53.499162

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "9c21dfe94dce"
down_revision: Union[str, Sequence[str], None] = "59126aa48ee8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("refresh_tokens", "hashed_token", new_column_name="token_hash")
    op.drop_constraint(op.f("uq_refresh_tokens_hashed_token"), "refresh_tokens", type_="unique")
    op.create_unique_constraint(op.f("uq_refresh_tokens_token_hash"), "refresh_tokens", ["token_hash"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f("uq_refresh_tokens_token_hash"), "refresh_tokens", type_="unique")
    op.alter_column("refresh_tokens", "token_hash", new_column_name="hashed_token")
    op.create_unique_constraint(op.f("uq_refresh_tokens_hashed_token"), "refresh_tokens", ["hashed_token"])
