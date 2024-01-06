"""Added route column to pokemon model

Revision ID: d12f30d45f18
Revises: 3552c894f374
Create Date: 2024-01-01 14:00:15.076079

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd12f30d45f18'
down_revision = '3552c894f374'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('pokemon', schema=None) as batch_op:
        batch_op.add_column(sa.Column('route', sa.String(length=50), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('pokemon', schema=None) as batch_op:
        batch_op.drop_column('route')

    # ### end Alembic commands ###
