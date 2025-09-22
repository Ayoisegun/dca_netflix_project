#!/bin/bash

set -e

export PGPASSWORD=$POSTGRES_PASSWORD
python scripts/preprocessing.py

psql -d $POSTGRES_DB -U $POSTGRES_USER -h $POSTGRES_HOST -f sql/create_tables.sql
psql -d $POSTGRES_DB -U $POSTGRES_USER -h $POSTGRES_HOST -f sql/validation.sql


chmod 0644 /etc/cron.d/netflix-cron
crontab /etc/cron.d/netflix-cron
echo "📡 Starting cron in foreground..."
cron -f