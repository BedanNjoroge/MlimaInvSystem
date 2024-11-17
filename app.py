from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import datetime
import pytz
import os

app = Flask(__name__)

# Define the path to your database folder and file
db_folder = 'database'
db_file = 'inventory.db'
db_path = os.path.join(db_folder, db_file)

# Create the folder if it doesn't exist
if not os.path.exists(db_folder):
    os.makedirs(db_folder)

# Define the East Africa Time timezone
eat = pytz.timezone('Africa/Nairobi')

# Initialize the database (creating tables if they don't exist)
def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Boulder table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS boulder (
            boulder_id TEXT PRIMARY KEY,
            date TEXT,
            description TEXT,
            good_boulder INTEGER,
            defect_line INTEGER,
            natural_cracks INTEGER,
            mining_cracks INTEGER,
            undersize INTEGER,
            total_boulders INTEGER
        )
    ''')

    # Drop the factory table if it exists
    #cursor.execute('DROP TABLE IF EXISTS factory')

    # Factory table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS factory (
            boulder_id TEXT PRIMARY KEY,
            description TEXT,
            good_boulder INTEGER,
            defect_line INTEGER,
            natural_cracks INTEGER,
            mining_cracks INTEGER,
            undersize INTEGER,
            total_boulders INTEGER,
            received_timestamp TEXT,
            FOREIGN KEY(boulder_id) REFERENCES boulder(boulder_id)
        )
    ''')

    # Slabs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS slabs (
            slab_id INTEGER PRIMARY KEY AUTOINCREMENT,
            boulder_id TEXT,
            description TEXT,
            good_slabs INTEGER,
            defect_line INTEGER,
            natural_cracks INTEGER,
            cutting_cracks INTEGER,
            thickness_issue INTEGER,
            total_slabs INTEGER,
            FOREIGN KEY(boulder_id) REFERENCES boulder(boulder_id)
        )
    ''')

    # Cutting Machine 1
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cutting_machine_1 (
            machine_id INTEGER PRIMARY KEY AUTOINCREMENT,
            boulder_id TEXT,
            description TEXT,
            num_slabs_cut INTEGER,
            start_time TEXT,
            end_time TEXT,
            machine_hours REAL,
            FOREIGN KEY(boulder_id) REFERENCES boulder(boulder_id)
        )
    ''')

    # Cutting Machine 2
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cutting_machine_2 (
            machine_id INTEGER PRIMARY KEY AUTOINCREMENT,
            boulder_id TEXT,
            description TEXT,
            num_slabs_cut INTEGER,
            start_time TEXT,
            end_time TEXT,
            machine_hours REAL,
            FOREIGN KEY(boulder_id) REFERENCES boulder(boulder_id)
        )
    ''')

    # Separation table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS separation (
            separation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            boulder_id TEXT,
            description TEXT,
            good_slabs INTEGER,
            defect_line INTEGER,
            natural_cracks INTEGER,
            cutting_cracks INTEGER,
            thickness_issue INTEGER,
            total_slabs INTEGER,
            separation_time TEXT,
            FOREIGN KEY(boulder_id) REFERENCES boulder(boulder_id)
        )
    ''')

    # Movement table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movement (
            movement_id INTEGER PRIMARY KEY AUTOINCREMENT,
            boulder_id TEXT,
            stage TEXT,
            details TEXT,
            date TEXT,
            FOREIGN KEY(boulder_id) REFERENCES boulder(boulder_id)
        )
    ''')

    # Archive table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS archived_boulder (
            boulder_id TEXT PRIMARY KEY,
            date TEXT,
            description TEXT,
            good_boulder TEXT,
            defect_line TEXT,
            natural_cracks TEXT,
            mining_cracks TEXT,
            undersize TEXT,
            total_boulders INTEGER
        )
    ''')

    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Helper function to log movements
def log_movement(boulder_id, stage, details):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    date = datetime.datetime.now(pytz.utc).astimezone(eat).strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO movement (boulder_id, stage, details, date)
        VALUES (?, ?, ?, ?)
    ''', (boulder_id, stage, details, date))
    conn.commit()
    conn.close()

# Route: Index page
@app.route('/')
def index():
    return render_template('index.html')

# Route: Quarry
@app.route('/quarry', methods=['GET', 'POST'])
def quarry():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if request.method == 'POST':
        boulder_id = request.form['boulder_id']
        date = request.form['date']
        description = request.form['description']

        # Function to convert Yes/No to integers
        def convert_to_int(value):
            if value.lower() == 'yes':
                return 1
            elif value.lower() == 'no':
                return 0
            else:
                try:
                    return int(value)
                except ValueError:
                    return 0  # or handle error as needed

        good_boulder = convert_to_int(request.form['good_boulder'])
        defect_line = convert_to_int(request.form['defect_line'])
        natural_cracks = convert_to_int(request.form['natural_cracks'])
        mining_cracks = convert_to_int(request.form['mining_cracks'])
        undersize = convert_to_int(request.form['undersize'])
        total_boulders = good_boulder + defect_line + natural_cracks + mining_cracks + undersize

        cursor.execute('''
            INSERT INTO boulder 
            (boulder_id, date, description, good_boulder, defect_line, natural_cracks, mining_cracks, undersize, total_boulders)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (boulder_id, date, description, good_boulder, defect_line, natural_cracks, mining_cracks, undersize, total_boulders))
        conn.commit()

        # Log movement
        log_movement(boulder_id, "Quarry", f"Boulder {boulder_id} added to the quarry.")

        conn.close()
        return redirect(url_for('quarry'))

    cursor.execute('SELECT * FROM boulder')
    boulders = cursor.fetchall()
    conn.close()
    return render_template('quarry.html', boulders=boulders)

# Route: Factory
@app.route('/factory', methods=['GET', 'POST'])
def factory():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch only good boulders from the quarry that are not already in the factory
    cursor.execute('''
        SELECT boulder_id, description 
        FROM boulder 
        WHERE good_boulder = 1 
        AND boulder_id NOT IN (SELECT boulder_id FROM factory)
    ''')
    boulders = cursor.fetchall()
    boulder_ids = [row[0] for row in boulders]
    boulder_dict = {row[0]: row[1] for row in boulders}  # Dictionary to map boulder_id to description

    if request.method == 'POST':
        boulder_id = request.form['boulder_id']
        description = request.form.get('description', boulder_dict.get(boulder_id, ''))
        
        # Function to convert Yes/No to integers
        def convert_to_int(value):
            if value.lower() == 'yes':
                return 1
            elif value.lower() == 'no':
                return 0
            else:
                try:
                    return int(value)
                except ValueError:
                    return 0  # or handle error as needed

        good_boulder = convert_to_int(request.form.get('good_boulder', '0'))
        defect_line = convert_to_int(request.form.get('defect_line', '0'))
        natural_cracks = convert_to_int(request.form.get('natural_cracks', '0'))
        mining_cracks = convert_to_int(request.form.get('mining_cracks', '0'))
        undersize = convert_to_int(request.form.get('undersize', '0'))
        total_boulders = good_boulder + defect_line + natural_cracks + mining_cracks + undersize
        received_timestamp = datetime.datetime.now(pytz.utc).astimezone(eat).strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute('''
            INSERT OR REPLACE INTO factory 
            (boulder_id, description, good_boulder, defect_line, natural_cracks, 
            mining_cracks, undersize, total_boulders, received_timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (boulder_id, description, good_boulder, defect_line, natural_cracks, 
              mining_cracks, undersize, total_boulders, received_timestamp))
        conn.commit()

        # Log movement
        log_movement(boulder_id, "Factory", f"Boulder {boulder_id} received at the factory.")
        conn.close()
        return redirect(url_for('factory'))

    cursor.execute('SELECT * FROM factory')
    factories = cursor.fetchall()
    conn.close()
    return render_template('factory.html', factories=factories, boulder_ids=boulder_ids, boulder_dict=boulder_dict)


# Route: Cutting Machine 1
@app.route('/cutting_machine_1', methods=['GET', 'POST'])
def cutting_machine_1():
    return cutting_machine(machine_id=1)

# Route: Cutting Machine 2
@app.route('/cutting_machine_2', methods=['GET', 'POST'])
def cutting_machine_2():
    return cutting_machine(machine_id=2)

# Helper function to handle Cutting Machines
def cutting_machine(machine_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    table = f"cutting_machine_{machine_id}"  # Dynamic table selection

    # Fetch only boulders received in the factory that have not been cut yet
    cursor.execute('''
        SELECT boulder_id, description 
        FROM factory 
        WHERE boulder_id NOT IN (SELECT boulder_id FROM cutting_machine_1 UNION SELECT boulder_id FROM cutting_machine_2)
    ''')
    boulders = cursor.fetchall()
    boulder_ids = [row[0] for row in boulders]
    boulder_dict = {row[0]: row[1] for row in boulders}

    if request.method == 'POST':
        boulder_id = request.form['boulder_id']
        description = request.form.get('description', boulder_dict.get(boulder_id, ''))
        start_time = request.form['start_time']  # This will be set via JavaScript
        end_time = request.form['end_time']      # This will be set via JavaScript
        num_slabs_cut = int(request.form['num_slabs_cut'])

        # Calculate machine hours
        start_time_dt = datetime.datetime.fromisoformat(start_time)
        end_time_dt = datetime.datetime.fromisoformat(end_time)
        machine_hours = (end_time_dt - start_time_dt).total_seconds() / 3600

        cursor.execute(f'''
            INSERT INTO {table} 
            (boulder_id, description, num_slabs_cut, start_time, end_time, machine_hours)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (boulder_id, description, num_slabs_cut, start_time, end_time, machine_hours))
        conn.commit()

        # Log movement
        log_movement(boulder_id, f"Cutting Machine {machine_id}", f"Boulder {boulder_id} cut with {num_slabs_cut} slabs.")

        conn.close()
        return redirect(url_for('cutting_machine_1' if machine_id == 1 else 'cutting_machine_2'))

    cursor.execute(f'SELECT * FROM {table}')
    cuts = cursor.fetchall()
    conn.close()
    return render_template(f'cutting_machine_{machine_id}.html', cuts=cuts, machine_id=machine_id, boulder_ids=boulder_ids, boulder_dict=boulder_dict)


# Route: Separation
@app.route('/separation', methods=['GET', 'POST'])
def separation():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch only cut boulders that have not been separated
    cursor.execute('''
        SELECT boulder_id, description 
        FROM (
            SELECT boulder_id, description FROM cutting_machine_1 
            UNION 
            SELECT boulder_id, description FROM cutting_machine_2
        )
        WHERE boulder_id NOT IN (SELECT boulder_id FROM separation)
    ''')
    boulders = cursor.fetchall()
    boulder_ids = [row[0] for row in boulders]
    boulder_dict = {row[0]: row[1] for row in boulders}

    if request.method == 'POST':
        boulder_id = request.form['boulder_id']
        description = request.form.get('description', boulder_dict.get(boulder_id, ''))
        good_slabs = int(request.form['good_slabs'])
        defect_line = int(request.form['defect_line'])
        natural_cracks = int(request.form['natural_cracks'])
        cutting_cracks = int(request.form['cutting_cracks'])
        thickness_issue = int(request.form['thickness_issue'])
        total_slabs = good_slabs + defect_line + natural_cracks + cutting_cracks + thickness_issue
        separation_time = datetime.datetime.now(pytz.utc).astimezone(eat).strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute('''
            INSERT INTO separation 
            (boulder_id, description, good_slabs, defect_line, natural_cracks, cutting_cracks, 
            thickness_issue, total_slabs, separation_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (boulder_id, description, good_slabs, defect_line, natural_cracks, cutting_cracks, thickness_issue, total_slabs, separation_time))
        conn.commit()

        # Log movement
        log_movement(boulder_id, "Separation", f"Boulder {boulder_id} separated into slabs.")
        conn.close()
        return redirect(url_for('separation'))

    cursor.execute('SELECT * FROM separation')
    separations = cursor.fetchall()
    conn.close()
    return render_template('separation.html', separations=separations, boulder_ids=boulder_ids, boulder_dict=boulder_dict)

if __name__ == '__main__':
    app.run(debug=True)
