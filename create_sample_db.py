"""Create a sample database with example tables for testing."""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

db_path = Path("example.db")

# Remove existing database if you want to start fresh
if db_path.exists():
    print(f"Removing existing {db_path}...")
    db_path.unlink()

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

print("Creating sample database...")

# Create sales table
cursor.execute("""
    CREATE TABLE sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_date DATE NOT NULL,
        revenue DECIMAL(10, 2) NOT NULL,
        product_id INTEGER,
        customer_id INTEGER,
        quantity INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Create products table
cursor.execute("""
    CREATE TABLE products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        price DECIMAL(10, 2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Create customers table
cursor.execute("""
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        city TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Insert sample products
products = [
    ("Laptop", "Electronics", 999.99),
    ("Mouse", "Electronics", 29.99),
    ("Desk Chair", "Furniture", 199.99),
    ("Monitor", "Electronics", 299.99),
    ("Keyboard", "Electronics", 79.99),
]
cursor.executemany("INSERT INTO products (name, category, price) VALUES (?, ?, ?)", products)

# Insert sample customers
customers = [
    ("Alice Johnson", "alice@example.com", "New York"),
    ("Bob Smith", "bob@example.com", "Los Angeles"),
    ("Charlie Brown", "charlie@example.com", "Chicago"),
    ("Diana Prince", "diana@example.com", "Seattle"),
    ("Eve Wilson", "eve@example.com", "Boston"),
]
cursor.executemany("INSERT INTO customers (name, email, city) VALUES (?, ?, ?)", customers)

# Insert sample sales data (last 6 months)
base_date = datetime.now()
sales_data = []
for i in range(180):  # 6 months of daily data
    sale_date = base_date - timedelta(days=i)
    product_id = (i % 5) + 1
    customer_id = (i % 5) + 1
    quantity = (i % 3) + 1
    # Get product price
    cursor.execute("SELECT price FROM products WHERE id = ?", (product_id,))
    price = cursor.fetchone()[0]
    revenue = price * quantity
    
    sales_data.append((
        sale_date.strftime("%Y-%m-%d"),
        float(revenue),
        product_id,
        customer_id,
        quantity
    ))

cursor.executemany(
    "INSERT INTO sales (sale_date, revenue, product_id, customer_id, quantity) VALUES (?, ?, ?, ?, ?)",
    sales_data
)

conn.commit()
print(f"\n[OK] Created {db_path}")
print("[OK] Created tables: sales, products, customers")
print(f"[OK] Inserted {len(products)} products")
print(f"[OK] Inserted {len(customers)} customers")
print(f"[OK] Inserted {len(sales_data)} sales records")

# Show summary
cursor.execute("SELECT COUNT(*) FROM sales")
sales_count = cursor.fetchone()[0]
cursor.execute("SELECT SUM(revenue) FROM sales")
total_revenue = cursor.fetchone()[0]

print(f"\nDatabase Summary:")
print(f"  Total sales: {sales_count}")
print(f"  Total revenue: ${total_revenue:,.2f}")

conn.close()
print("\n[OK] Sample database created successfully!")
print("\nYou can now:")
print("  1. Run /introspect to refresh the schema cache")
print("  2. Ask questions like 'Total revenue by month'")

