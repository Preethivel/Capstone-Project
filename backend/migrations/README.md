# Database migrations

The active application uses SQLAlchemy models and creates missing tables on startup for the current MVP. Schema changes should be added here as versioned SQL or migrated to Alembic before production schema evolution.

Production deployments must use a managed `DATABASE_URL`; do not rely on SQLite migration scripts against MySQL.
