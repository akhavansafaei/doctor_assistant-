"""Add fitness and nutrition profile fields

Revision ID: 001_fitness_nutrition
Revises:
Create Date: 2025-11-23

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_fitness_nutrition'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add fitness and nutrition specific columns to health_profiles table"""

    # Add fitness-specific columns
    op.add_column('health_profiles', sa.Column('fitness_level', sa.String(length=50), nullable=True))
    op.add_column('health_profiles', sa.Column('training_experience', sa.String(length=100), nullable=True))
    op.add_column('health_profiles', sa.Column('fitness_goals', sa.JSON(), nullable=True))

    # Add equipment and training schedule columns
    op.add_column('health_profiles', sa.Column('available_equipment', sa.JSON(), nullable=True))
    op.add_column('health_profiles', sa.Column('training_days_per_week', sa.Integer(), nullable=True))
    op.add_column('health_profiles', sa.Column('training_duration_minutes', sa.Integer(), nullable=True))

    # Add health and injury tracking columns
    op.add_column('health_profiles', sa.Column('current_injuries', sa.JSON(), nullable=True))
    op.add_column('health_profiles', sa.Column('health_conditions', sa.JSON(), nullable=True))

    # Add nutrition preference columns
    op.add_column('health_profiles', sa.Column('diet_preference', sa.String(length=100), nullable=True))
    op.add_column('health_profiles', sa.Column('dietary_restrictions', sa.JSON(), nullable=True))
    op.add_column('health_profiles', sa.Column('food_allergies', sa.JSON(), nullable=True))

    # Add body composition columns
    op.add_column('health_profiles', sa.Column('body_fat_percentage', sa.Float(), nullable=True))
    op.add_column('health_profiles', sa.Column('body_measurements', sa.JSON(), nullable=True))

    # Update KnowledgeDocument metadata column name
    # Rename 'metadata' to 'doc_metadata' to avoid SQLAlchemy reserved keyword
    op.alter_column('knowledge_documents', 'metadata',
                    new_column_name='doc_metadata',
                    existing_type=sa.JSON(),
                    nullable=True)


def downgrade() -> None:
    """Remove fitness and nutrition specific columns"""

    # Remove fitness-specific columns
    op.drop_column('health_profiles', 'body_measurements')
    op.drop_column('health_profiles', 'body_fat_percentage')
    op.drop_column('health_profiles', 'food_allergies')
    op.drop_column('health_profiles', 'dietary_restrictions')
    op.drop_column('health_profiles', 'diet_preference')
    op.drop_column('health_profiles', 'health_conditions')
    op.drop_column('health_profiles', 'current_injuries')
    op.drop_column('health_profiles', 'training_duration_minutes')
    op.drop_column('health_profiles', 'training_days_per_week')
    op.drop_column('health_profiles', 'available_equipment')
    op.drop_column('health_profiles', 'fitness_goals')
    op.drop_column('health_profiles', 'training_experience')
    op.drop_column('health_profiles', 'fitness_level')

    # Revert KnowledgeDocument column name
    op.alter_column('knowledge_documents', 'doc_metadata',
                    new_column_name='metadata',
                    existing_type=sa.JSON(),
                    nullable=True)
