#!/bin/bash
# start.sh

echo "Checking database status..."

# Check if the alembic_version table exists (indicates migrations have been applied)
if python -c "
import asyncio
import os
from app.config.sql_session import get_db_url
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def check_alembic_version():
    engine = create_async_engine(get_db_url())
    async with engine.connect() as conn:
        try:
            result = await conn.execute(text('SELECT * FROM alembic_version LIMIT 1'))
            return True
        except:
            return False
        finally:
            await engine.dispose()

result = asyncio.run(check_alembic_version())
exit(0 if result else 1)
"; then
    echo "Migrations already applied."
else
    echo "Migrating database..."
    alembic upgrade head
    if [ $? -eq 0 ]; then
        echo " Migrations applied successfully."
    else
        echo "Error while applying migrations, stamping the database..."
        alembic stamp head
    fi
fi

echo "Initing FastAPI application..."
exec python main.py
