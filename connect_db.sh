#!/bin/bash
# Opens an interactive psql session against DATABASE_URL from .env.
# Avoids `source .env`, which breaks on the special characters in the password.
set -e
cd "$(dirname "$0")"
DATABASE_URL=$(.venv/bin/python3 -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.environ['DATABASE_URL'])")
exec psql "$DATABASE_URL" "$@"
