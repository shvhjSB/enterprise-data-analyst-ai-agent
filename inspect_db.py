"""Quick script to inspect the SQLite database schema and contents."""

import sqlite3
import sys
from pathlib import Path

db_path = Path("example.db")

if not db_path.exists():
    print(f"Error: {db_path} does not exist!")
    sys.exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

print("=" * 60)
print("DATABASE INSPECTION: example.db")
print("=" * 60)

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

if not tables:
    print("\nNo tables found in database.")
    conn.close()
    sys.exit(0)

print(f"\nFound {len(tables)} table(s):")
for (table_name,) in tables:
    print(f"  - {table_name}")

# For each table, show schema and row count
for (table_name,) in tables:
    print(f"\n{'=' * 60}")
    print(f"TABLE: {table_name}")
    print(f"{'=' * 60}")
    
    # Get table schema
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    print("\nColumns:")
    for col in columns:
        col_id, name, col_type, not_null, default_val, pk = col
        pk_str = " (PRIMARY KEY)" if pk else ""
        null_str = " NOT NULL" if not_null else ""
        default_str = f" DEFAULT {default_val}" if default_val else ""
        print(f"  - {name}: {col_type}{null_str}{default_str}{pk_str}")
    
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    row_count = cursor.fetchone()[0]
    print(f"\nRow count: {row_count}")
    
    # Show sample data (first 5 rows)
    if row_count > 0:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
        rows = cursor.fetchall()
        print("\nSample data (first 5 rows):")
        for i, row in enumerate(rows, 1):
            print(f"  Row {i}: {row}")
        if row_count > 5:
            print(f"  ... and {row_count - 5} more rows")

conn.close()
print(f"\n{'=' * 60}")

