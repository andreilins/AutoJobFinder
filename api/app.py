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

# Get all jobs
@app.route('/jobs', methods=['GET'])
def get_jobs():
    conn = get_db_connection()
    jobs = conn.execute('SELECT * FROM jobs').fetchall()
    conn.close()
    return jsonify([dict(job) for job in jobs])

# Get a job by ID
@app.route('/jobs/<int:id>', methods=['GET'])
def get_job(id):
    conn = get_db_connection()
    job = conn.execute('SELECT * FROM jobs WHERE id = ?', (id,)).fetchone()
    conn.close()
    if job is None:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(dict(job))

# Update a job by ID
@app.route('/jobs/<int:id>', methods=['PUT'])
def update_job(id):
    conn = get_db_connection()
    job = conn.execute('SELECT * FROM jobs WHERE id = ?', (id,)).fetchone()
    if job is None:
        conn.close()
        return jsonify({"error": "Job not found"}), 404

    updated_job = request.get_json()
    job_title = updated_job.get('job_title', job['job_title'])
    company = updated_job.get('company', job['company'])
    location = updated_job.get('location', job['location'])
    description = updated_job.get('description', job['description'])

    conn.execute(
        'UPDATE jobs SET job_title = ?, company = ?, location = ?, description = ? WHERE id = ?',
        (job_title, company, location, description, id)
    )
    conn.commit()
    conn.close()

    return jsonify({"id": id, "job_title": job_title, "company": company, "location": location, "description": description})

if __name__ == '__main__':
    app.run(debug=True)
