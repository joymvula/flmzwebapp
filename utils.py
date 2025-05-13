# flask_legacy_app/utils.py

import csv
import os
from io import StringIO
from flask import current_app

def eliminate_redundant_fields(form_data: dict, form_type: str) -> dict:
    """
    Example: if last visit <30 days ago, drop 'findings' from data.
    Expand with more business rules as needed.
    """
    data = form_data.copy()
    if form_type == 'home_visit':
        # front‐end JS already hides the field, but double‐check here
        last_date = form_data.get('last_date')
        if last_date:
            from datetime import datetime
            diff = datetime.utcnow().date() - datetime.strptime(last_date, '%Y-%m-%d').date()
            if diff.days < 30 and 'findings' in data:
                data.pop('findings')
    return data

def generate_csv(records, report_type: str) -> str:
    """
    Generate a CSV file for the given SQLAlchemy model instances.
    Returns the path to the saved file.
    """
    # infer columns from first record
    if not records:
        raise ValueError("No data to export")

    # dynamically pull attributes
    headers = []
    first = records[0]
    if report_type == 'home_visit':
        headers = ['Date', 'Child Name', 'Findings']
        rows = [(r.date.strftime('%Y-%m-%d'), r.child.name, r.findings) for r in records]
    elif report_type == 'vulnerability':
        headers = ['Date', 'Child Name', 'Score']
        rows = [(r.date.strftime('%Y-%m-%d'), r.child.name, r.score) for r in records]
    elif report_type == 'literacy':
        headers = ['Date', 'Child Name', 'Ticks', 'Level']
        rows = [(r.date.strftime('%Y-%m-%d'), r.child.name, r.ticks, r.level) for r in records]
    else:
        # fallback: use __dict__, skipping private attrs
        headers = [k for k in first.__dict__.keys() if not k.startswith('_')]
        rows = [[getattr(r, h) for h in headers] for r in records]

    # write to a temp CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    content = output.getvalue().encode('utf-8')

    # tmp_dir = current_app.config.get('TMP_DIR', '/tmp')
    temp_dir = "/Users/amukoma/Documents/github.io/devsbranch/simaata_data_webapp/volumes/tmp"
    tmp_dir = current_app.config.get('TMP_DIR', temp_dir)
    os.makedirs(tmp_dir, exist_ok=True)
    file_path = os.path.join(tmp_dir, f'{report_type}_report.csv')
    with open(file_path, 'wb') as f:
        f.write(content)
    return file_path


