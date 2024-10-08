import sqlite3

def create_database(db_name):
    # Step 2: Connect to SQLite database
    conn = sqlite3.connect(db_name)
    
    # Step 3: Create a cursor object
    cursor = conn.cursor()

    # Step 4: Create table if it doesn't already exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        location TEXT NOT NULL,
        description TEXT,
        url TEXT NOT NULL,
        application_status TEXT,
        easy_apply BOOLEAN
    )
    ''')

    # Step 5: Commit and close the connection
    conn.commit()
    conn.close()

    print(f"Database '{db_name}' created with 'jobs' table.")

# Example usage
create_database('jobs.db')