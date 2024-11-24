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
    conn = sqlite3.connect(db_path, timeout=30)
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS boulder_archive')
    cursor.execute('DROP TABLE IF EXISTS slab')

    # Drop and recreate the boulder table
    cursor.execute('DROP TABLE IF EXISTS boulder')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS boulder (
            boulder_id TEXT PRIMARY KEY,
            date TEXT,
            boulder_description TEXT,
            color TEXT,
            good_boulder INTEGER,
            defect_line INTEGER,
            natural_cracks INTEGER,
            mining_cracks INTEGER,
            undersize INTEGER,
            total_boulders INTEGER
        )
    ''')

    # Drop and recreate the factory table
    cursor.execute('DROP TABLE IF EXISTS factory')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS factory (
            boulder_id TEXT PRIMARY KEY,
            boulder_description TEXT,
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
    cursor.execute('DROP TABLE IF EXISTS slabs')
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
    cursor.execute('DROP TABLE IF EXISTS cutting_machine_1')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cutting_machine_1 (
            machine_id INTEGER PRIMARY KEY AUTOINCREMENT,
            boulder_id TEXT,
            boulder_description TEXT,
            num_slabs_cut INTEGER,
            start_time TEXT,
            end_time TEXT,
            machine_hours REAL,
            FOREIGN KEY(boulder_id) REFERENCES boulder(boulder_id)
        )
    ''')

    # Cutting Machine 2
    cursor.execute('DROP TABLE IF EXISTS cutting_machine_2')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cutting_machine_2 (
            machine_id INTEGER PRIMARY KEY AUTOINCREMENT,
            boulder_id TEXT,
            boulder_description TEXT,
            num_slabs_cut INTEGER,
            start_time TEXT,
            end_time TEXT,
            machine_hours REAL,
            FOREIGN KEY(boulder_id) REFERENCES boulder(boulder_id)
        )
    ''')

    # Separation table
    cursor.execute('DROP TABLE IF EXISTS separation')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS separation (
            separation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            boulder_id TEXT,
            boulder_description TEXT,
            slab_id TEXT,
            slab_description TEXT,
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

    #Polishing table
    cursor.execute('DROP TABLE IF EXISTS polishing')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS polishing (
            polishing_id INTEGER PRIMARY KEY AUTOINCREMENT,
            slab_id TEXT,
            slab_description TEXT,
            original_status TEXT,
            polishing_description TEXT,
            good_slab INTEGER, 
            defect_line INTEGER,
            natural_cracks INTEGER, 
            cutting_cracks INTEGER, 
            thickness_issue INTEGER,
            polishing_time TEXT,                  
            FOREIGN KEY(slab_id) REFERENCES separation(slab_id) 
        ) 
    ''')
    
    # Edge Cutting Standard Table 
    cursor.execute('DROP TABLE IF EXISTS edge_cutting_standard')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS edge_cutting_standard ( 
            edge_cutting_id INTEGER PRIMARY KEY AUTOINCREMENT,
            slab_id TEXT, 
            polishing_description TEXT, 
            edge_cutting_description TEXT,
            good_slab INTEGER, 
            defect_line INTEGER, 
            natural_cracks INTEGER,
            cutting_cracks INTEGER, 
            thickness_issue INTEGER, 
            edge_cutting_time TEXT, 
            FOREIGN KEY(slab_id) REFERENCES polishing(slab_id)
        ) 
    ''')

    # Edge Cutting Special Orders Table 
    cursor.execute('DROP TABLE IF EXISTS edge_cutting_special_orders')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS edge_cutting_special_orders (
            edge_cutting_id INTEGER PRIMARY KEY AUTOINCREMENT,
            slab_id TEXT, 
            polishing_description TEXT, 
            edge_cutting_description TEXT, 
            special_order_details TEXT, 
            good_slab INTEGER,
            defect_line INTEGER, 
            natural_cracks INTEGER, 
            cutting_cracks INTEGER,
            thickness_issue INTEGER, 
            edge_cutting_time TEXT, 
            FOREIGN KEY(slab_id) REFERENCES polishing(slab_id)
        ) 
    ''')

    # Bullnose Table 
    cursor.execute('DROP TABLE IF EXISTS bullnose')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bullnose (
        bullnose_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        slab_id TEXT, 
        edge_cutting_description TEXT,
        bullnose_description TEXT, 
        good_slab INTEGER, 
        defect_line INTEGER,
        natural_cracks INTEGER, 
        cutting_cracks INTEGER, 
        thickness_issue INTEGER,
        bullnose_time TEXT,
        FOREIGN KEY(slab_id) REFERENCES edge_cutting_standard(slab_id) ON DELETE CASCADE, 
        FOREIGN KEY(slab_id) REFERENCES edge_cutting_special_orders(slab_id) ON DELETE CASCADE
        ) 
    ''')

   # Sealant Table 
    cursor.execute('DROP TABLE IF EXISTS sealant')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sealant (
            sealant_id INTEGER PRIMARY KEY AUTOINCREMENT,
            slab_id TEXT, 
            bullnose_description TEXT, 
            sealant_description TEXT,
            good_slab INTEGER, 
            defect_line INTEGER, 
            natural_cracks INTEGER,
            cutting_cracks INTEGER, 
            thickness_issue INTEGER, 
            sealant_time TEXT,
            FOREIGN KEY(slab_id) REFERENCES bullnose(slab_id)
        ) 
    ''')

    # Ready Slabs Table 
    cursor.execute('DROP TABLE IF EXISTS ready_slabs')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ready_slabs (
            ready_slab_id INTEGER PRIMARY KEY AUTOINCREMENT,
            slab_id TEXT,
            sealant_description TEXT,
            good_slab INTEGER, 
            defect_line INTEGER, 
            natural_cracks INTEGER,
            cutting_cracks INTEGER, 
            thickness_issue INTEGER, 
            ready_time TEXT,
            FOREIGN KEY(slab_id) REFERENCES sealant(slab_id)
        ) 
    ''')

    # Movement table
    cursor.execute('DROP TABLE IF EXISTS movement')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movement (
            movement_id INTEGER PRIMARY KEY AUTOINCREMENT,
            boulder_id TEXT,
            slab_id TEXT,
            stage TEXT,
            details TEXT,
            date TEXT,
            FOREIGN KEY(boulder_id) REFERENCES boulder(boulder_id)
            FOREIGN KEY(slab_id) REFERENCES separation(slab_id)
        )
    ''')

    # Inventory table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            slab_id TEXT PRIMARY KEY,
            slab_description TEXT,
            stage TEXT,
            good_slab INTEGER,
            defect_line INTEGER,
            natural_cracks INTEGER,
            cutting_cracks INTEGER,
            thickness_issue INTEGER,
            FOREIGN KEY(slab_id) REFERENCES separation(slab_id)
        )
    ''')

    # Archive table
    #cursor.execute('DROP TABLE IF EXISTS archived_boulder')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS archived_boulder (
            boulder_id TEXT PRIMARY KEY,
            date TEXT,
            boulder_description TEXT,
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
def log_movement(stage, details, boulder_id=None, slab_id=None):
    conn = sqlite3.connect(db_path, timeout=30)
    cursor = conn.cursor()
    date = datetime.datetime.now(pytz.utc).astimezone(eat).strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO movement (boulder_id, slab_id, stage, details, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (boulder_id, slab_id, stage, details, date))
    conn.commit()
    conn.close()

#Helper function to update inventory
def update_inventory(slab_id, description, stage, good_slab, defect_line, natural_cracks, cutting_cracks, thickness_issue):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO inventory (slab_id, slab_description, stage, good_slab, defect_line, natural_cracks, cutting_cracks, thickness_issue)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(slab_id) DO UPDATE SET
                slab_description=excluded.slab_description,
                stage=excluded.stage,
                good_slab=excluded.good_slab,
                defect_line=excluded.defect_line,
                natural_cracks=excluded.natural_cracks,
                cutting_cracks=excluded.cutting_cracks,
                thickness_issue=excluded.thickness_issue
        ''', (slab_id, description, stage, good_slab, defect_line, natural_cracks, cutting_cracks, thickness_issue))
        conn.commit()


# Helper function to convert Yes/No to integers
def convert_to_int(value): 
    if value.lower() == 'yes': 
        return 1 
    elif value.lower() == 'no': 
        return 0 
    else: 
        try: 
            return int(value) 
        except ValueError: 
            return 0 # or handle error as needed

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
        date = request.form['date']
        boulder_description = request.form['boulder_description']

        # Extract color from the boulder description
        color = boulder_description.split()[0]
        color_prefix = color[0].upper()

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

        # Generate boulder_id
        cursor.execute("SELECT COUNT(*) FROM boulder WHERE color = ?", (color,))
        count = cursor.fetchone()[0] + 1
        boulder_id = f"M{color_prefix}{count:03d}"

        cursor.execute('''
            INSERT INTO boulder 
            (boulder_id, date, boulder_description, color, good_boulder, defect_line, natural_cracks, mining_cracks, undersize, total_boulders)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (boulder_id, date, boulder_description, color, good_boulder, defect_line, natural_cracks, mining_cracks, undersize, total_boulders))
        conn.commit()

        # Log movement
        log_movement(stage="Quarry", details=f"Boulder {boulder_id} added to the quarry.", boulder_id=boulder_id)

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
        SELECT boulder_id, boulder_description 
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

        good_boulder = convert_to_int(request.form.get('good_boulder', 'no'))
        defect_line = convert_to_int(request.form.get('defect_line', 'no'))
        natural_cracks = convert_to_int(request.form.get('natural_cracks', 'no'))
        mining_cracks = convert_to_int(request.form.get('mining_cracks', 'no'))
        undersize = convert_to_int(request.form.get('undersize', 'no'))
        total_boulders = good_boulder + defect_line + natural_cracks + mining_cracks + undersize
        received_timestamp = datetime.datetime.now(pytz.utc).astimezone(eat).strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute('''
            INSERT OR REPLACE INTO factory 
            (boulder_id, boulder_description, good_boulder, defect_line, natural_cracks, 
            mining_cracks, undersize, total_boulders, received_timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (boulder_id, description, good_boulder, defect_line, natural_cracks, 
              mining_cracks, undersize, total_boulders, received_timestamp))
        conn.commit()

        # Log movement
        log_movement(stage="Factory", details=f"Boulder {boulder_id} received at the factory.", boulder_id=boulder_id)
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
        SELECT boulder_id, boulder_description 
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
            (boulder_id, boulder_description, num_slabs_cut, start_time, end_time, machine_hours)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (boulder_id, description, num_slabs_cut, start_time, end_time, machine_hours))
        conn.commit()

        # Log movement
        log_movement(stage=f"Cutting Machine {machine_id}", details=f"Boulder {boulder_id} cut with {num_slabs_cut} slabs.", boulder_id=boulder_id)

        conn.close()
        return redirect(url_for('cutting_machine_1' if machine_id == 1 else 'cutting_machine_2'))

    cursor.execute(f'SELECT * FROM {table}')
    cuts = cursor.fetchall()
    conn.close()
    return render_template(f'cutting_machine_{machine_id}.html', cuts=cuts, machine_id=machine_id, boulder_ids=boulder_ids, boulder_dict=boulder_dict)

# Helper function to fetch the number of slabs cut for a boulder ID
def get_num_slabs_cut(boulder_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT SUM(num_slabs_cut) 
        FROM (
            SELECT num_slabs_cut FROM cutting_machine_1 WHERE boulder_id = ?
            UNION ALL
            SELECT num_slabs_cut FROM cutting_machine_2 WHERE boulder_id = ?
        )
    ''', (boulder_id, boulder_id))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result[0] else 0

# Route: Separation
@app.route('/separation', methods=['GET', 'POST'])
def separation():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch only cut boulders that have not been separated
    cursor.execute('''
        SELECT boulder_id, boulder_description 
        FROM (
            SELECT boulder_id, boulder_description FROM cutting_machine_1 
            UNION 
            SELECT boulder_id, boulder_description FROM cutting_machine_2
        )
        WHERE boulder_id NOT IN (SELECT boulder_id FROM separation)
    ''')
    boulders = cursor.fetchall()
    boulder_ids = [row[0] for row in boulders]
    boulder_dict = {row[0]: row[1] for row in boulders}

    # Fetch the number of slabs cut for each boulder
    slabs_cut = {boulder_id: get_num_slabs_cut(boulder_id) for boulder_id in boulder_ids}

    if request.method == 'POST':
        boulder_id = request.form['boulder_id']
        boulder_description = request.form.get('boulder_description', boulder_dict.get(boulder_id, ''))
        slab_description = request.form['slab_description']
        
        # Extract color from the slab description
        slab_color = slab_description.split()[0]
        slab_color_prefix = slab_color[0].upper()

        good_slabs = int(request.form['good_slabs'])
        defect_line = int(request.form['defect_line'])
        natural_cracks = int(request.form['natural_cracks'])
        cutting_cracks = int(request.form['cutting_cracks'])
        thickness_issue = int(request.form['thickness_issue'])
        total_slabs = good_slabs + defect_line + natural_cracks + cutting_cracks + thickness_issue
        separation_time = datetime.datetime.now(pytz.utc).astimezone(eat).strftime("%Y-%m-%d %H:%M:%S")

        for i in range(1, total_slabs + 1):
            slab_id = f"{boulder_id}_S{slab_color_prefix}{i:03d}"
            cursor.execute('''
                INSERT INTO separation 
                (boulder_id, boulder_description, slab_id, slab_description, good_slabs, defect_line, natural_cracks, cutting_cracks, 
                thickness_issue, total_slabs, separation_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (boulder_id, boulder_description, slab_id, slab_description, 1 if i <= good_slabs else 0, 1 if i > good_slabs and i <= good_slabs + defect_line else 0, 
                  1 if i > good_slabs + defect_line and i <= good_slabs + defect_line + natural_cracks else 0, 1 if i > good_slabs + defect_line + natural_cracks and i <= good_slabs + defect_line + natural_cracks + cutting_cracks else 0, 
                  1 if i > good_slabs + defect_line + natural_cracks + cutting_cracks and i <= total_slabs else 0, total_slabs, separation_time))
        
        conn.commit()

        # Log movement for each slab
        for i in range(1, total_slabs + 1):
            slab_id = f"{boulder_id}_S{slab_color_prefix}{i:03d}"
            #log_movement(boulder_id, "Separation", f"Slab {slab_id} from Boulder {boulder_id} separated.")
            log_movement(stage="Separation", details=f"Slab {slab_id} from Boulder {boulder_id} separated.", boulder_id=boulder_id, slab_id=slab_id)
        conn.close()
        return redirect(url_for('separation'))

    cursor.execute('SELECT * FROM separation')
    separations = cursor.fetchall()
    conn.close()
    return render_template('separation.html', separations=separations, boulder_ids=boulder_ids, boulder_dict=boulder_dict, slabs_cut=slabs_cut)


@app.route('/polishing', methods=['GET', 'POST'])
def polishing():
    if request.method == 'POST':
        try:
            slab_id = request.form['slab_id']
            with sqlite3.connect(db_path, timeout=30) as conn:
                cursor = conn.cursor()

                # Fetch slab description and original status from separation table
                cursor.execute('''
                    SELECT slab_description, 
                           CASE 
                               WHEN good_slabs = 1 THEN 'Good'
                               WHEN defect_line = 1 THEN 'Defect Line'
                               WHEN natural_cracks = 1 THEN 'Natural Cracks'
                               WHEN cutting_cracks = 1 THEN 'Cutting Cracks'
                               WHEN thickness_issue = 1 THEN 'Thickness Issue'
                               ELSE 'Unknown'
                           END as original_status
                    FROM separation WHERE slab_id = ?
                ''', (slab_id,))
                result = cursor.fetchone()
                slab_description = result[0]
                original_status = result[1]

                polishing_description = request.form['polishing_description']
                good_slab = convert_to_int(request.form['good_slab'])
                defect_line = convert_to_int(request.form['defect_line'])
                natural_cracks = convert_to_int(request.form['natural_cracks'])
                cutting_cracks = convert_to_int(request.form['cutting_cracks'])
                thickness_issue = convert_to_int(request.form['thickness_issue'])

                polishing_time = datetime.datetime.now(pytz.utc).astimezone(eat).strftime("%Y-%m-%d %H:%M:%S")

                cursor.execute('''
                    INSERT INTO polishing (slab_id, slab_description, original_status, polishing_description, 
                                           good_slab, defect_line, natural_cracks, cutting_cracks, 
                                           thickness_issue, polishing_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (slab_id, slab_description, original_status, polishing_description, good_slab, defect_line, natural_cracks, cutting_cracks, thickness_issue, polishing_time))
                conn.commit()

            # Log movement
            log_movement(stage="Polishing", details=f"Slab {slab_id} polished with description: {polishing_description}.", slab_id=slab_id)

        except sqlite3.OperationalError as e:
            print(f"Error: {e}")
            return "An error occurred during the transaction."

        return redirect(url_for('polishing'))

    # Fetch slabs that have been separated but not polished
    try:
        with sqlite3.connect(db_path, timeout=30) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT slab_id, slab_description, 
                       CASE 
                           WHEN good_slabs = 1 THEN 'Good'
                           WHEN defect_line = 1 THEN 'Defect Line'
                           WHEN natural_cracks = 1 THEN 'Natural Cracks'
                           WHEN cutting_cracks = 1 THEN 'Cutting Cracks'
                           WHEN thickness_issue = 1 THEN 'Thickness Issue'
                           ELSE 'Unknown'
                       END as original_status
                FROM separation 
                WHERE slab_id NOT IN (SELECT slab_id FROM polishing)
            ''')
            slabs = cursor.fetchall()
            
            # Fetch polished slabs
            cursor.execute('SELECT * FROM polishing')
            polished_slabs = cursor.fetchall()
    except sqlite3.OperationalError as e:
        print(f"Fetch Error: {e}")
        return "An error occurred during fetching data."

    return render_template('polishing.html', slabs=slabs, polished_slabs=polished_slabs)


#Route: Edge Cutting Standard
@app.route('/edge_cutting_standard', methods=['GET', 'POST'])
def edge_cutting_standard():
    if request.method == 'POST':
        try:
            slab_id = request.form['slab_id']
            with sqlite3.connect(db_path, timeout=30) as conn:
                cursor = conn.cursor()

                # Fetch polishing description from the polishing table
                cursor.execute('SELECT polishing_description FROM polishing WHERE slab_id = ?', (slab_id,))
                polishing_description = cursor.fetchone()[0]

                edge_cutting_description = request.form['edge_cutting_description']
                good_slab = convert_to_int(request.form['good_slab'])
                defect_line = convert_to_int(request.form['defect_line'])
                natural_cracks = convert_to_int(request.form['natural_cracks'])
                cutting_cracks = convert_to_int(request.form['cutting_cracks'])
                thickness_issue = convert_to_int(request.form['thickness_issue'])

                edge_cutting_time = datetime.datetime.now(pytz.utc).astimezone(eat).strftime("%Y-%m-%d %H:%M:%S")

                cursor.execute('''
                    INSERT INTO edge_cutting_standard (slab_id, polishing_description, edge_cutting_description, 
                                                       good_slab, defect_line, natural_cracks, cutting_cracks, 
                                                       thickness_issue, edge_cutting_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (slab_id, polishing_description, edge_cutting_description, good_slab, defect_line, natural_cracks, cutting_cracks, thickness_issue, edge_cutting_time))
                conn.commit()

            # Update inventory
            update_inventory(slab_id, edge_cutting_description, 'Awaiting Bullnose', good_slab, defect_line, natural_cracks, cutting_cracks, thickness_issue)

            # Log movement
            log_movement(stage="Edge Cutting Standard", details=f"Slab {slab_id} edge cut with description: {edge_cutting_description}.", slab_id=slab_id)

        except sqlite3.OperationalError as e:
            print(f"Error: {e}")
            return "An error occurred during the transaction."

        return redirect(url_for('edge_cutting_standard'))

    # Fetch slabs that have been polished but not edge cut
    try:
        with sqlite3.connect(db_path, timeout=30) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT slab_id, polishing_description 
                FROM polishing
                WHERE slab_id NOT IN (SELECT slab_id FROM edge_cutting_standard) 
                AND slab_id NOT IN (SELECT slab_id FROM edge_cutting_special_orders)
            ''')
            slabs = cursor.fetchall()
            
            # Fetch edge cut slabs
            cursor.execute('SELECT * FROM edge_cutting_standard')
            edge_cut_slabs = cursor.fetchall()
    except sqlite3.OperationalError as e:
        print(f"Fetch Error: {e}")
        return "An error occurred during fetching data."

    return render_template('edge_cutting_standard.html', slabs=slabs, edge_cut_slabs=edge_cut_slabs)


#Route: Edge Cutting Special Orders
@app.route('/edge_cutting_special_orders', methods=['GET', 'POST'])
def edge_cutting_special_orders():
    if request.method == 'POST':
        slab_id = request.form['slab_id']
        try:
            with sqlite3.connect(db_path, timeout=30) as conn:
                cursor = conn.cursor()

                # Fetch polishing description from the polishing table
                cursor.execute('SELECT polishing_description FROM polishing WHERE slab_id = ?', (slab_id,))
                polishing_description = cursor.fetchone()[0]
                conn.commit()

            slab_sizes = request.form.getlist('special_order_size[]')
            edge_cutting_descriptions = request.form.getlist('special_order_description[]')
            good_slab = convert_to_int(request.form['good_slab'])
            defect_line = convert_to_int(request.form['defect_line'])
            natural_cracks = convert_to_int(request.form['natural_cracks'])
            cutting_cracks = convert_to_int(request.form['cutting_cracks'])
            thickness_issue = convert_to_int(request.form['thickness_issue'])
            edge_cutting_time = datetime.datetime.now(pytz.utc).astimezone(eat).strftime("%Y-%m-%d %H:%M:%S")

            with sqlite3.connect(db_path, timeout=30) as conn:
                cursor = conn.cursor()
                for i, size in enumerate(slab_sizes):
                    special_order_id = f"OS{(i + 1):03d}"
                    special_slab_id = f"{slab_id}_{special_order_id}"
                    special_edge_cutting_description = edge_cutting_descriptions[i]
                    cursor.execute('''
                        INSERT INTO edge_cutting_special_orders (slab_id, polishing_description, edge_cutting_description, 
                                                                 special_order_details, good_slab, defect_line, natural_cracks, cutting_cracks, 
                                                                 thickness_issue, edge_cutting_time)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (special_slab_id, polishing_description, special_edge_cutting_description, 
                          size, good_slab, defect_line, natural_cracks, cutting_cracks, thickness_issue, edge_cutting_time))
                    # Log movement for each special slab
                    log_movement(stage="Edge Cutting Special Orders", details=f"Special Order Slab {special_slab_id} edge cut from {slab_id} with size: {size}.", slab_id=special_slab_id)
                conn.commit()

                # Update inventory for each special slab
                for i, size in enumerate(slab_sizes):
                    special_order_id = f"OS{(i + 1):03d}"
                    special_slab_id = f"{slab_id}_{special_order_id}"
                    special_edge_cutting_description = edge_cutting_descriptions[i]
                    update_inventory(special_slab_id, special_edge_cutting_description, 'Awaiting Bullnose', good_slab, defect_line, natural_cracks, cutting_cracks, thickness_issue)

        except sqlite3.OperationalError as e:
            print(f"Error: {e}")
            return "An error occurred during the transaction."

        return redirect(url_for('edge_cutting_special_orders'))

    # Fetch slabs that have been polished but not edge cut
    try:
        with sqlite3.connect(db_path, timeout=30) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT slab_id, polishing_description 
                FROM polishing
                WHERE slab_id NOT IN (SELECT slab_id FROM edge_cutting_special_orders) 
                AND slab_id NOT IN (SELECT slab_id FROM edge_cutting_standard)
            ''')
            slabs = cursor.fetchall()
            
            # Fetch edge cut slabs
            cursor.execute('SELECT * FROM edge_cutting_special_orders')
            edge_cut_slabs = cursor.fetchall()
    except sqlite3.OperationalError as e:
        print(f"Fetch Error: {e}")
        return "An error occurred during fetching data."

    return render_template('edge_cutting_special_orders.html', slabs=slabs, edge_cut_slabs=edge_cut_slabs)


#Route: Bullnose
@app.route('/bullnose', methods=['GET', 'POST'])
def bullnose():
    if request.method == 'POST':
        try:
            slab_id = request.form['slab_id']
            with sqlite3.connect(db_path, timeout=30) as conn:
                cursor = conn.cursor()

                # Fetch edge cutting description from edge cutting tables
                cursor.execute('''
                    SELECT edge_cutting_description 
                    FROM edge_cutting_standard 
                    WHERE slab_id = ? 
                    UNION 
                    SELECT edge_cutting_description 
                    FROM edge_cutting_special_orders 
                    WHERE slab_id = ?
                ''', (slab_id, slab_id))
                edge_cutting_description = cursor.fetchone()[0]

                bullnose_description = request.form['bullnose_description']
                good_slab = convert_to_int(request.form['good_slab'])
                defect_line = convert_to_int(request.form['defect_line'])
                natural_cracks = convert_to_int(request.form['natural_cracks'])
                cutting_cracks = convert_to_int(request.form['cutting_cracks'])
                thickness_issue = convert_to_int(request.form['thickness_issue'])

                bullnose_time = datetime.datetime.now(pytz.utc).astimezone(eat).strftime("%Y-%m-%d %H:%M:%S")

                cursor.execute('''
                    INSERT INTO bullnose (slab_id, edge_cutting_description, bullnose_description, 
                                          good_slab, defect_line, natural_cracks, cutting_cracks, 
                                          thickness_issue, bullnose_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (slab_id, edge_cutting_description, bullnose_description, good_slab, defect_line, natural_cracks, cutting_cracks, thickness_issue, bullnose_time))
                conn.commit()

            # Log movement
            log_movement(stage="Bullnose", details=f"Slab {slab_id} bullnosed with description: {bullnose_description}.", slab_id=slab_id)

        except sqlite3.OperationalError as e:
            print(f"Error: {e}")
            return "An error occurred during the transaction."

        return redirect(url_for('bullnose'))

    # Fetch slabs that have been edge cut but not bullnosed
    try:
        with sqlite3.connect(db_path, timeout=30) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT slab_id, edge_cutting_description 
                FROM edge_cutting_standard 
                WHERE slab_id NOT IN (SELECT slab_id FROM bullnose) 
                UNION 
                SELECT slab_id, edge_cutting_description 
                FROM edge_cutting_special_orders 
                WHERE slab_id NOT IN (SELECT slab_id FROM bullnose)
            ''')
            slabs = cursor.fetchall()
            
            # Fetch bullnosed slabs
            cursor.execute('SELECT * FROM bullnose')
            bullnosed_slabs = cursor.fetchall()
    except sqlite3.OperationalError as e:
        print(f"Fetch Error: {e}")
        return "An error occurred during fetching data."

    return render_template('bullnose.html', slabs=slabs, bullnosed_slabs=bullnosed_slabs)


#Route: Sealant Application
@app.route('/sealant', methods=['GET', 'POST'])
def sealant():
    if request.method == 'POST':
        try:
            slab_id = request.form['slab_id']
            with sqlite3.connect(db_path, timeout=30) as conn:
                cursor = conn.cursor()

                # Fetch bullnose description from bullnose table
                cursor.execute('SELECT bullnose_description FROM bullnose WHERE slab_id = ?', (slab_id,))
                bullnose_description = cursor.fetchone()[0]

                sealant_description = request.form['sealant_description']
                good_slab = convert_to_int(request.form['good_slab'])
                defect_line = convert_to_int(request.form['defect_line'])
                natural_cracks = convert_to_int(request.form['natural_cracks'])
                cutting_cracks = convert_to_int(request.form['cutting_cracks'])
                thickness_issue = convert_to_int(request.form['thickness_issue'])

                sealant_time = datetime.datetime.now(pytz.utc).astimezone(eat).strftime("%Y-%m-%d %H:%M:%S")

                cursor.execute('''
                    INSERT INTO sealant (slab_id, bullnose_description, sealant_description, 
                                         good_slab, defect_line, natural_cracks, cutting_cracks, 
                                         thickness_issue, sealant_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (slab_id, bullnose_description, sealant_description, good_slab, defect_line, natural_cracks, cutting_cracks, thickness_issue, sealant_time))
                conn.commit()

            # Log movement
            log_movement(stage="Sealant", details=f"Slab {slab_id} sealed with description: {sealant_description}.", slab_id=slab_id)

        except sqlite3.OperationalError as e:
            print(f"Error: {e}")
            return "An error occurred during the transaction."

        return redirect(url_for('sealant'))

    # Fetch slabs that have been bullnosed but not sealed
    try:
        with sqlite3.connect(db_path, timeout=30) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT slab_id, bullnose_description 
                FROM bullnose 
                WHERE slab_id NOT IN (SELECT slab_id FROM sealant)
            ''')
            slabs = cursor.fetchall()
            
            # Fetch sealed slabs
            cursor.execute('SELECT * FROM sealant')
            sealed_slabs = cursor.fetchall()
    except sqlite3.OperationalError as e:
        print(f"Fetch Error: {e}")
        return "An error occurred during fetching data."

    return render_template('sealant.html', slabs=slabs, sealed_slabs=sealed_slabs)


#Route: Ready Slabs
@app.route('/ready_slabs', methods=['GET', 'POST'])
def ready_slabs():
    if request.method == 'POST':
        try:
            slab_id = request.form['slab_id']
            with sqlite3.connect(db_path, timeout=30) as conn:
                cursor = conn.cursor()

                # Fetch sealant description from sealant table
                cursor.execute('SELECT sealant_description FROM sealant WHERE slab_id = ?', (slab_id,))
                sealant_description = cursor.fetchone()[0]

                good_slab = convert_to_int(request.form['good_slab'])
                defect_line = convert_to_int(request.form['defect_line'])
                natural_cracks = convert_to_int(request.form['natural_cracks'])
                cutting_cracks = convert_to_int(request.form['cutting_cracks'])
                thickness_issue = convert_to_int(request.form['thickness_issue'])

                ready_time = datetime.datetime.now(pytz.utc).astimezone(eat).strftime("%Y-%m-%d %H:%M:%S")

                cursor.execute('''
                    INSERT INTO ready_slabs (slab_id, sealant_description, 
                                             good_slab, defect_line, natural_cracks, cutting_cracks, 
                                             thickness_issue, ready_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (slab_id, sealant_description, good_slab, defect_line, natural_cracks, cutting_cracks, thickness_issue, ready_time))
                conn.commit()

            # Log movement
            log_movement(stage="Ready Slabs", details=f"Slab {slab_id} ready with description: {sealant_description}.", slab_id=slab_id)

        except sqlite3.OperationalError as e:
            print(f"Error: {e}")
            return "An error occurred during the transaction."

        return redirect(url_for('ready_slabs'))

    # Fetch slabs that have been sealed but not marked as ready
    try:
        with sqlite3.connect(db_path, timeout=30) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT slab_id, sealant_description 
                FROM sealant 
                WHERE slab_id NOT IN (SELECT slab_id FROM ready_slabs)
            ''')
            slabs = cursor.fetchall()
            
            # Fetch ready slabs
            cursor.execute('SELECT * FROM ready_slabs')
            ready_slabs_data = cursor.fetchall()
    except sqlite3.OperationalError as e:
        print(f"Fetch Error: {e}")
        return "An error occurred during fetching data."

    return render_template('ready_slabs.html', slabs=slabs, ready_slabs_data=ready_slabs_data)


if __name__ == '__main__':
    init_db()  # Call this to initialize the database schema
    app.run(debug=True)
