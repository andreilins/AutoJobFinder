# app.py
from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Database helper function
def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'jobs.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enables dictionary-like access for rows
    return conn

# Routes

@app.route('/jobs', methods=['GET'])
def get_easy_apply_null_jobs():
    # Connect to the database
    conn = get_db_connection()
    # Query to get all job IDs where easy_apply = 1 and application_status is NULL
    query = '''
        SELECT id
        FROM jobs
        WHERE easy_apply = 1 AND application_status IS NULL
    '''
    
    # Execute the query
    cursor = conn.execute(query)
    jobs = cursor.fetchall()
    # Extract the job IDs from the result
    job_ids = [job['id'] for job in jobs]
    # Close the connection
    conn.close()
    # Return the job IDs as a JSON response
    return jsonify(job_ids)

# Get a job by ID
@app.route('/jobs/<int:id>', methods=['GET'])
def get_job(id):
    conn = get_db_connection()
    job = conn.execute('SELECT * FROM jobs WHERE id = ?', (id,)).fetchone()
    conn.close()
    if job is None:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(dict(job))

# Update application status for a job by ID
@app.route('/jobs/<int:id>', methods=['PUT'])
def update_job(id):
    conn = get_db_connection()

    # Check if the job exists
    job = conn.execute('SELECT * FROM jobs WHERE id = ?', (id,)).fetchone()
    if job is None:
        conn.close()
        return jsonify({"error": "Job not found"}), 404

    # Get the updated application status from the request
    updated_data = request.get_json()
    new_status = updated_data.get('application_status', job['application_status'])  # Default to current status if not provided

    # Update the application status
    conn.execute(
        'UPDATE jobs SET application_status = ? WHERE id = ?',
        (new_status, id)
    )
    conn.commit()
    conn.close()

    # Return the updated job data as a response
    return jsonify({
        "id": id,
        "application_status": new_status
    })


if __name__ == '__main__':
    app.run(debug=True)
