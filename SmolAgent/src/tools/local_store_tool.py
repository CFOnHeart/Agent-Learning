import sqlite3
from smolagents import tool

# before using the receipt_query tool, you need to create the receipts table and insert data into it.
def create_receipts_table():
    print ("Creating receipts table and inserting prepared data...")
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('receipts.db')

    # Create a cursor object
    cursor = conn.cursor()

    # Create the table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS receipts (
        receipt_id INTEGER PRIMARY KEY,
        customer_name TEXT(16),
        price REAL,
        tip REAL
    )
    ''')

    # Define 20 rows of data
    data = [
        (1, 'Alice', 23.50, 3.50),
        (2, 'Bob', 45.00, 5.00),
        (3, 'Charlie', 12.75, 2.25),
        (4, 'David', 33.20, 4.80),
        (5, 'Eva', 27.30, 3.70),
        (6, 'Frank', 19.90, 2.10),
        (7, 'Grace', 50.00, 7.50),
        (8, 'Hannah', 22.40, 3.60),
        (9, 'Ivy', 18.60, 2.40),
        (10, 'Jack', 40.00, 6.00),
        (11, 'Karen', 29.50, 4.50),
        (12, 'Leo', 35.75, 5.25),
        (13, 'Mona', 15.80, 2.20),
        (14, 'Nina', 28.90, 3.10),
        (15, 'Oscar', 21.00, 3.00),
        (16, 'Paul', 37.40, 4.60),
        (17, 'Quinn', 26.30, 3.70),
        (18, 'Rachel', 32.50, 4.50),
        (19, 'Steve', 24.80, 3.20),
        (20, 'Tina', 30.60, 4.40)
    ]

    # Insert the data into the table
    cursor.executemany('''
    INSERT INTO receipts (receipt_id, customer_name, price, tip)
    VALUES (?, ?, ?, ?)
    ''', data)

    # Commit the transaction
    conn.commit()
    conn.close()

@tool
def receipt_query(query: str) -> str:
    """
    Help me user to query the receipt information from the local SQLite database.
    The table named `receipts` contains the following columns:
    - receipt_id INTEGER PRIMARY KEY,
    - customer_name TEXT(16),
    - price REAL,
    - tip REAL
    Please the query in SQL format, e.g., "SELECT * FROM receipts WHERE customer_name = 'Alice'".

    Args:
        query: The sqlite query

    Returns:
        Search results of receipts
    """
    # Connect to SQLite database (or create it if it doesn't exist)
    import os
    if not os.path.exists('receipts.db'):
        create_receipts_table()

    conn = sqlite3.connect('receipts.db')

    # Create a cursor object
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM receipts')
    rows = cursor.fetchall()
    info = ""
    for row in rows:
        info += row.__str__() + "\n"
    conn.close()
    return info

