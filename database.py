import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

def get_db():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        full_name TEXT NOT NULL,
        designation TEXT,
        district TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 2. Documents Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        original_filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        mime_type TEXT NOT NULL,
        upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        uploaded_by TEXT NOT NULL,
        status TEXT DEFAULT 'uploaded'
    )
    ''')
    
    # 3. Land Records Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS land_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_number TEXT UNIQUE NOT NULL,
        document_id INTEGER,
        owner_name TEXT NOT NULL,
        survey_number TEXT NOT NULL,
        subdivision_number TEXT,
        patta_number TEXT NOT NULL,
        district TEXT NOT NULL,
        taluk TEXT NOT NULL,
        village TEXT NOT NULL,
        land_area TEXT NOT NULL,
        document_type TEXT NOT NULL,
        document_date TEXT,
        confidence_score REAL NOT NULL,
        status TEXT NOT NULL,
        priority TEXT NOT NULL DEFAULT 'MEDIUM',
        issue_description TEXT,
        anomaly_flags TEXT,
        duplicate_of_id TEXT,
        duplicate_similarity REAL,
        field_confidences TEXT,
        validation_checks TEXT,
        officer_remarks TEXT,
        verified_by TEXT,
        verified_at TIMESTAMP,
        qr_hash TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (document_id) REFERENCES documents (id)
    )
    ''')

    # Safe Schema Migrations for Land Records
    for col_name, col_type in [
        ("subdivision_number", "TEXT"),
        ("submitted_by", "TEXT"),
        ("latitude", "REAL"),
        ("longitude", "REAL"),
        ("is_approx_location", "INTEGER DEFAULT 1")
    ]:
        try:
            cursor.execute(f"ALTER TABLE land_records ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            pass
    
    # 4. Verification History Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS verification_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_id INTEGER NOT NULL,
        officer_name TEXT NOT NULL,
        action TEXT NOT NULL,
        remarks TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (record_id) REFERENCES land_records (id)
    )
    ''')
    
    # 5. Audit Logs Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        username TEXT NOT NULL,
        role TEXT NOT NULL,
        action TEXT NOT NULL,
        record_id TEXT,
        previous_status TEXT,
        new_status TEXT,
        details TEXT
    )
    ''')

    # 6. Ownership History Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ownership_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_id INTEGER,
        record_number TEXT NOT NULL,
        owner_name TEXT NOT NULL,
        ownership_type TEXT DEFAULT 'Individual',
        transfer_type TEXT NOT NULL,
        transfer_date TEXT NOT NULL,
        document_ref TEXT,
        verified_by TEXT,
        verified_at TIMESTAMP,
        is_current INTEGER DEFAULT 0,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (record_id) REFERENCES land_records (id)
    )
    ''')
    
    conn.commit()
    ensure_features_schema_and_data(conn)
    conn.close()

LOCATION_CENTROIDS = {
    ('Salem', 'Attur', 'Attur Rural'): (11.5977, 78.5968),
    ('Salem', 'Omalur', 'Karuppur'): (11.7283, 78.1067),
    ('Madurai', 'Vadipatti', 'Alanganallur'): (10.0468, 78.0967),
    ('Coimbatore', 'Pollachi', 'Anaimalai'): (10.5833, 76.9333),
    ('Coimbatore', 'Sulur', 'Irugur'): (11.0183, 77.0650),
    ('Thanjavur', 'Kumbakonam', 'Swamimalai'): (10.9567, 79.3283),
    ('Tiruchirappalli', 'Srirangam', 'Thiruvanaikoil'): (10.8522, 78.7047),
    ('Chennai', 'Guindy', 'Velachery'): (12.9815, 80.2180),
    ('Tirunelveli', 'Ambasamudram', 'Kallidaikurichi'): (8.6942, 77.4578),
    ('Erode', 'Perundurai', 'Vijayamangalam'): (11.2333, 77.5000),
    ('Dindigul', 'Palani', 'Ayakudi'): (10.4500, 77.5500),
    ('Salem', '', ''): (11.6643, 78.1460),
    ('Coimbatore', '', ''): (11.0168, 76.9558),
    ('Madurai', '', ''): (9.9252, 78.1198),
    ('Thanjavur', '', ''): (10.7870, 79.1378),
    ('Chennai', '', ''): (13.0827, 80.2707),
    ('Tiruchirappalli', '', ''): (10.7905, 78.7047),
    ('Tirunelveli', '', ''): (8.7139, 77.7567),
    ('Erode', '', ''): (11.3410, 77.7172),
    ('Dindigul', '', ''): (10.3673, 77.9803)
}

def ensure_features_schema_and_data(conn):
    """
    Ensures safe database updates for interactive map coordinates,
    ownership history, and citizen applications without erasing existing data.
    """
    cursor = conn.cursor()

    # 1. Update approximate centroid coordinates for records missing latitude/longitude
    cursor.execute("SELECT id, district, taluk, village FROM land_records WHERE latitude IS NULL")
    rows = cursor.fetchall()
    for row in rows:
        key = (row['district'], row['taluk'], row['village'])
        coords = LOCATION_CENTROIDS.get(key)
        if not coords:
            coords = LOCATION_CENTROIDS.get((row['district'], '', ''))
        if coords:
            cursor.execute(
                "UPDATE land_records SET latitude = ?, longitude = ?, is_approx_location = 1 WHERE id = ?",
                (coords[0], coords[1], row['id'])
            )

    # 2. Seed verified Ownership History if empty
    cursor.execute("SELECT COUNT(*) FROM ownership_history")
    if cursor.fetchone()[0] == 0:
        histories = [
            # LV-2026-00125 (Salem, Survey 123/4A)
            (
                'LV-2026-00125', 'K. Shanmugam Sundaram', 'Individual',
                'Registered Sale Deed', '1998-04-12', 'Doc #1042/1998 (Attur SRO)',
                'Sub-Registrar Attur', '1998-04-12 11:30:00', 0,
                'Initial recorded revenue title under Tamil Nadu Patta Pass Book Act 1983'
            ),
            (
                'LV-2026-00125', 'Ramesh Kumar', 'Individual',
                'Inheritance & Legal Heir Settlement', '2014-06-20', 'Settlement Deed #412/2014',
                'Ramesh V. Sundaram', '2014-06-20 14:15:00', 1,
                'Revenue Taluk mutation completed; verified and digitized in digital vault'
            ),
            # LV-2026-00128 (Coimbatore, Survey 78/1A)
            (
                'LV-2026-00128', 'Kandhasamy Natarajan', 'Individual',
                'Registered Partition Deed', '2005-09-14', 'Deed #892/2005 (Pollachi SRO)',
                'District Registrar Pollachi', '2005-09-14 10:45:00', 0,
                'Partition of ancestral agricultural holding with irrigation rights'
            ),
            (
                'LV-2026-00128', 'Senthil Nathan K.', 'Individual',
                'Family Settlement Deed', '2019-11-05', 'Settlement Deed #310/2019',
                'Priya K. Narayanan', '2019-11-05 16:20:00', 1,
                'Title mutated and verified under Patta #31045'
            ),
            # LV-2026-00131 (Chennai, Survey 99/2)
            (
                'LV-2026-00131', 'T. S. Anbarasan', 'Individual',
                'Sale Deed', '2011-02-18', 'CMDA Approved Purchase #1520/2011',
                'SRO Velachery', '2011-02-18 12:00:00', 0,
                'Urban property acquisition with building layout approval'
            ),
            (
                'LV-2026-00131', 'Revathi Anbarasan', 'Individual',
                'Survivorship & Title Mutation Deed', '2021-08-10', 'Legal Heir Deed #741/2021',
                'Ramesh V. Sundaram', '2021-08-10 11:30:00', 1,
                'Revenue patta mutated to spouse following succession certificate'
            )
        ]

        for h in histories:
            cursor.execute("SELECT id FROM land_records WHERE record_number = ?", (h[0],))
            rec_row = cursor.fetchone()
            rec_id = rec_row['id'] if rec_row else None
            cursor.execute('''
            INSERT INTO ownership_history (
                record_id, record_number, owner_name, ownership_type,
                transfer_type, transfer_date, document_ref,
                verified_by, verified_at, is_current, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (rec_id, h[0], h[1], h[2], h[3], h[4], h[5], h[6], h[7], h[8], h[9]))

    # 3. Ensure demo applications for citizen_ananya
    cursor.execute("SELECT COUNT(*) FROM land_records WHERE submitted_by = 'citizen_ananya'")
    if cursor.fetchone()[0] == 0:
        ananya_apps = [
            {
                'record_number': 'LV-APP-2026-001',
                'owner_name': 'Ananya R. Sharma',
                'survey_number': '54/1A',
                'patta_number': '78201',
                'district': 'Salem',
                'taluk': 'Attur',
                'village': 'Attur Rural',
                'land_area': '1.75 Acres',
                'document_type': 'Patta Passbook',
                'document_date': '2026-08-10',
                'confidence_score': 92.0,
                'status': 'PENDING',
                'priority': 'MEDIUM',
                'issue_description': 'Citizen application awaiting revenue field inspection',
                'officer_remarks': 'Application received. Pending appointment of Village Administrative Officer (VAO).',
                'submitted_by': 'citizen_ananya',
                'latitude': 11.5977,
                'longitude': 78.5968,
                'is_approx_location': 1
            },
            {
                'record_number': 'LV-APP-2026-002',
                'owner_name': 'Ananya R. Sharma',
                'survey_number': '54/1B',
                'patta_number': '78202',
                'district': 'Salem',
                'taluk': 'Attur',
                'village': 'Attur Rural',
                'land_area': '1.20 Acres',
                'document_type': 'Partition Deed',
                'document_date': '2026-07-28',
                'confidence_score': 88.0,
                'status': 'UNDER_REVIEW',
                'priority': 'HIGH',
                'issue_description': 'Tahsildar verification of partition deed boundaries in progress',
                'officer_remarks': 'Ground demarcation initiated. VAO report submitted; pending Sub-Collector approval.',
                'submitted_by': 'citizen_ananya',
                'latitude': 11.5977,
                'longitude': 78.5968,
                'is_approx_location': 1
            },
            {
                'record_number': 'LV-APP-2026-003',
                'owner_name': 'Ananya R. Sharma',
                'survey_number': '112/3',
                'patta_number': '89104',
                'district': 'Salem',
                'taluk': 'Attur',
                'village': 'Attur Rural',
                'land_area': '2.10 Acres',
                'document_type': 'Sale Deed Excerpt',
                'document_date': '2026-05-14',
                'confidence_score': 96.0,
                'status': 'APPROVED',
                'priority': 'LOW',
                'issue_description': 'Application verified and approved by Tahsildar desk',
                'officer_remarks': 'Revenue record verified against District Registry Form 1. Tamper-proof certificate generated.',
                'submitted_by': 'citizen_ananya',
                'latitude': 11.5977,
                'longitude': 78.5968,
                'is_approx_location': 1
            },
            {
                'record_number': 'LV-APP-2026-004',
                'owner_name': 'Ananya R. Sharma',
                'survey_number': '99/4C',
                'patta_number': '62015',
                'district': 'Salem',
                'taluk': 'Omalur',
                'village': 'Karuppur',
                'land_area': '0.80 Acres',
                'document_type': 'Settlement Deed',
                'document_date': '2026-04-02',
                'confidence_score': 64.0,
                'status': 'REJECTED',
                'priority': 'HIGH',
                'issue_description': 'Boundary discrepancy between partition schedule and revenue registry',
                'officer_remarks': 'Rejected: Boundary schedule in settlement deed conflicts with adjacent parcel survey #99/4B. Please resubmit with revised cadastral plan.',
                'submitted_by': 'citizen_ananya',
                'latitude': 11.7283,
                'longitude': 78.1067,
                'is_approx_location': 1
            }
        ]

        for app_rec in ananya_apps:
            qr = generate_record_hash(app_rec['record_number'], app_rec['owner_name'], app_rec['survey_number'], app_rec['patta_number'])
            cursor.execute('''
            INSERT INTO land_records (
                record_number, owner_name, survey_number, patta_number,
                district, taluk, village, land_area, document_type, document_date,
                confidence_score, status, priority, issue_description,
                officer_remarks, qr_hash, submitted_by, latitude, longitude, is_approx_location
            ) VALUES (
                :record_number, :owner_name, :survey_number, :patta_number,
                :district, :taluk, :village, :land_area, :document_type, :document_date,
                :confidence_score, :status, :priority, :issue_description,
                :officer_remarks, :qr_hash, :submitted_by, :latitude, :longitude, :is_approx_location
            )
            ''', {**app_rec, 'qr_hash': qr})
            
            cursor.execute("SELECT last_insert_rowid()")
            last_id = cursor.fetchone()[0]

            # Link status history
            cursor.execute('''
            INSERT INTO verification_history (record_id, officer_name, action, remarks, timestamp)
            VALUES (?, ?, ?, ?, ?)
            ''', (last_id, 'citizen_ananya', 'APPLICATION_SUBMITTED', 'Citizen submitted land record document for revenue verification', '2026-08-10 10:00:00'))

            if app_rec['status'] in ['UNDER_REVIEW', 'APPROVED', 'REJECTED']:
                cursor.execute('''
                INSERT INTO verification_history (record_id, officer_name, action, remarks, timestamp)
                VALUES (?, ?, ?, ?, ?)
                ''', (last_id, 'officer_ramesh', 'UNDER_REVIEW', 'Revenue Divisional Officer assigned application for field verification', '2026-08-12 11:30:00'))

            if app_rec['status'] == 'APPROVED':
                cursor.execute('''
                INSERT INTO verification_history (record_id, officer_name, action, remarks, timestamp)
                VALUES (?, ?, ?, ?, ?)
                ''', (last_id, 'officer_ramesh', 'APPROVED', app_rec['officer_remarks'], '2026-08-15 14:00:00'))

            elif app_rec['status'] == 'REJECTED':
                cursor.execute('''
                INSERT INTO verification_history (record_id, officer_name, action, remarks, timestamp)
                VALUES (?, ?, ?, ?, ?)
                ''', (last_id, 'officer_ramesh', 'REJECTED', app_rec['officer_remarks'], '2026-08-16 16:30:00'))

    conn.commit()

def generate_record_hash(record_number, owner_name, survey_no, patta_no):
    raw = f"{record_number}|{owner_name}|{survey_no}|{patta_no}|LANDVAULT-GOV-VERIFIED"
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()

def seed_demo_data():
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    # Seed Default Users
    users = [
        (
            'officer_ramesh',
            'officer@landvault.gov.in',
            generate_password_hash('officer123'),
            'officer',
            'Ramesh V. Sundaram',
            'Senior Revenue Divisional Officer',
            'Salem'
        ),
        (
            'officer_priya',
            'priya.officer@landvault.gov.in',
            generate_password_hash('officer123'),
            'officer',
            'Priya K. Narayanan',
            'Tahsildar / Verification Officer',
            'Coimbatore'
        ),
        (
            'citizen_ananya',
            'citizen@example.com',
            generate_password_hash('citizen123'),
            'citizen',
            'Ananya R. Sharma',
            'Land Owner / Citizen',
            'Salem'
        ),
        (
            'citizen_karthik',
            'karthik.p@example.com',
            generate_password_hash('citizen123'),
            'citizen',
            'Karthik P. Natarajan',
            'Citizen',
            'Madurai'
        )
    ]
    cursor.executemany('''
    INSERT INTO users (username, email, password_hash, role, full_name, designation, district)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', users)

    # Seed Demo Land Records
    # Diverse statuses: VERIFIED, PENDING, NEEDS_REVIEW, POTENTIAL_ANOMALY, DUPLICATE_CANDIDATE
    sample_records = [
        {
            'record_number': 'LV-2026-00125',
            'owner_name': 'Ramesh Kumar',
            'survey_number': '123/4A',
            'patta_number': '45892',
            'district': 'Salem',
            'taluk': 'Attur',
            'village': 'Attur Rural',
            'land_area': '2.5 Acres',
            'document_type': 'Patta Passbook',
            'document_date': '2026-08-14',
            'confidence_score': 91.0,
            'status': 'VERIFIED',
            'priority': 'LOW',
            'issue_description': 'Fully verified by Revenue Officer Ramesh',
            'anomaly_flags': json.dumps([]),
            'duplicate_of_id': None,
            'duplicate_similarity': None,
            'field_confidences': json.dumps({
                'owner_name': 92,
                'survey_number': 84,
                'patta_number': 95,
                'district': 97,
                'taluk': 89,
                'village': 76,
                'land_area': 91,
                'document_type': 96,
                'document_date': 90
            }),
            'validation_checks': json.dumps({
                'required_fields': True,
                'survey_format': True,
                'area_format': True,
                'district_valid': True,
                'village_confidence': True,
                'patta_format': True
            }),
            'officer_remarks': 'Physical revenue records cross-referenced with District Registry Form 1. All boundaries and owner identity validated.',
            'verified_by': 'Ramesh V. Sundaram',
            'verified_at': '2026-10-04 10:36:12',
            'qr_hash': generate_record_hash('LV-2026-00125', 'Ramesh Kumar', '123/4A', '45892')
        },
        {
            'record_number': 'LV-2026-00126',
            'owner_name': 'Meenakshi Sundaram',
            'survey_number': '45/2B1',
            'patta_number': '89201',
            'district': 'Madurai',
            'taluk': 'Vadipatti',
            'village': 'Alanganallur',
            'land_area': '3.75 Acres',
            'document_type': 'Sale Deed Excerpt',
            'document_date': '2026-07-22',
            'confidence_score': 68.0,
            'status': 'POTENTIAL_ANOMALY',
            'priority': 'HIGH',
            'issue_description': 'Survey number format variance & village confidence low (62%)',
            'anomaly_flags': json.dumps([
                'Survey number requires manual verification (complex sub-division format)',
                'Village name confidence is low (62%)',
                'Discrepancy in recorded boundary description vs revenue catalog'
            ]),
            'duplicate_of_id': None,
            'duplicate_similarity': None,
            'field_confidences': json.dumps({
                'owner_name': 88,
                'survey_number': 64,
                'patta_number': 90,
                'district': 94,
                'taluk': 82,
                'village': 62,
                'land_area': 85,
                'document_type': 91,
                'document_date': 87
            }),
            'validation_checks': json.dumps({
                'required_fields': True,
                'survey_format': False,
                'area_format': True,
                'district_valid': True,
                'village_confidence': False,
                'patta_format': True
            }),
            'officer_remarks': None,
            'verified_by': None,
            'verified_at': None,
            'qr_hash': generate_record_hash('LV-2026-00126', 'Meenakshi Sundaram', '45/2B1', '89201')
        },
        {
            'record_number': 'LV-2026-00127',
            'owner_name': 'Ramesh Kumar S.',
            'survey_number': '123/4A',
            'patta_number': '45892',
            'district': 'Salem',
            'taluk': 'Attur',
            'village': 'Attur Rural',
            'land_area': '2.5 Acres',
            'document_type': 'Partition Deed',
            'document_date': '2026-09-02',
            'confidence_score': 89.0,
            'status': 'DUPLICATE_CANDIDATE',
            'priority': 'HIGH',
            'issue_description': 'High similarity (94%) with verified record LV-2026-00125',
            'anomaly_flags': json.dumps([
                'Possible duplicate entry detected against record LV-2026-00125',
                'Identical Survey Number and Patta Number already registered'
            ]),
            'duplicate_of_id': 'LV-2026-00125',
            'duplicate_similarity': 94.0,
            'field_confidences': json.dumps({
                'owner_name': 91,
                'survey_number': 92,
                'patta_number': 96,
                'district': 95,
                'taluk': 90,
                'village': 88,
                'land_area': 89,
                'document_type': 92,
                'document_date': 88
            }),
            'validation_checks': json.dumps({
                'required_fields': True,
                'survey_format': True,
                'area_format': True,
                'district_valid': True,
                'village_confidence': True,
                'patta_format': True
            }),
            'officer_remarks': None,
            'verified_by': None,
            'verified_at': None,
            'qr_hash': generate_record_hash('LV-2026-00127', 'Ramesh Kumar S.', '123/4A', '45892')
        },
        {
            'record_number': 'LV-2026-00128',
            'owner_name': 'Senthil Nathan K.',
            'survey_number': '78/1A',
            'patta_number': '31045',
            'district': 'Coimbatore',
            'taluk': 'Pollachi',
            'village': 'Anaimalai',
            'land_area': '5.20 Acres',
            'document_type': 'Patta Passbook',
            'document_date': '2026-06-19',
            'confidence_score': 94.0,
            'status': 'VERIFIED',
            'priority': 'LOW',
            'issue_description': 'Approved without discrepancies',
            'anomaly_flags': json.dumps([]),
            'duplicate_of_id': None,
            'duplicate_similarity': None,
            'field_confidences': json.dumps({
                'owner_name': 96,
                'survey_number': 94,
                'patta_number': 98,
                'district': 99,
                'taluk': 95,
                'village': 92,
                'land_area': 94,
                'document_type': 98,
                'document_date': 95
            }),
            'validation_checks': json.dumps({
                'required_fields': True,
                'survey_format': True,
                'area_format': True,
                'district_valid': True,
                'village_confidence': True,
                'patta_format': True
            }),
            'officer_remarks': 'High quality digitized scan. Clean land register cross-check.',
            'verified_by': 'Priya K. Narayanan',
            'verified_at': '2026-10-02 14:15:30',
            'qr_hash': generate_record_hash('LV-2026-00128', 'Senthil Nathan K.', '78/1A', '31045')
        },
        {
            'record_number': 'LV-2026-00129',
            'owner_name': 'Muthuvel Karunanidhi',
            'survey_number': '204/3C',
            'patta_number': '19402',
            'district': 'Thanjavur',
            'taluk': 'Kumbakonam',
            'village': 'Swamimalai',
            'land_area': '1.80 Hectares',
            'document_type': 'Chitta Extract',
            'document_date': '2026-08-30',
            'confidence_score': 81.0,
            'status': 'PENDING',
            'priority': 'MEDIUM',
            'issue_description': 'Awaiting revenue officer assignment and signature check',
            'anomaly_flags': json.dumps([]),
            'duplicate_of_id': None,
            'duplicate_similarity': None,
            'field_confidences': json.dumps({
                'owner_name': 82,
                'survey_number': 80,
                'patta_number': 86,
                'district': 91,
                'taluk': 84,
                'village': 78,
                'land_area': 80,
                'document_type': 88,
                'document_date': 82
            }),
            'validation_checks': json.dumps({
                'required_fields': True,
                'survey_format': True,
                'area_format': True,
                'district_valid': True,
                'village_confidence': True,
                'patta_format': True
            }),
            'officer_remarks': None,
            'verified_by': None,
            'verified_at': None,
            'qr_hash': generate_record_hash('LV-2026-00129', 'Muthuvel Karunanidhi', '204/3C', '19402')
        },
        {
            'record_number': 'LV-2026-00130',
            'owner_name': 'Balasubramaniam V.',
            'survey_number': '312/5',
            'patta_number': '58120',
            'district': 'Tiruchirappalli',
            'taluk': 'Srirangam',
            'village': 'Thiruvanaikoil',
            'land_area': '0.95 Acres',
            'document_type': 'Settlement Deed',
            'document_date': '2026-05-11',
            'confidence_score': 74.0,
            'status': 'NEEDS_REVIEW',
            'priority': 'MEDIUM',
            'issue_description': 'Stamp duty seal partially occluded; field confidence review required',
            'anomaly_flags': json.dumps([
                'Partial seal occlusion near document date section',
                'Manual verification recommended for owner spelling check'
            ]),
            'duplicate_of_id': None,
            'duplicate_similarity': None,
            'field_confidences': json.dumps({
                'owner_name': 72,
                'survey_number': 81,
                'patta_number': 79,
                'district': 92,
                'taluk': 83,
                'village': 75,
                'land_area': 77,
                'document_type': 85,
                'document_date': 65
            }),
            'validation_checks': json.dumps({
                'required_fields': True,
                'survey_format': True,
                'area_format': True,
                'district_valid': True,
                'village_confidence': True,
                'patta_format': True
            }),
            'officer_remarks': None,
            'verified_by': None,
            'verified_at': None,
            'qr_hash': generate_record_hash('LV-2026-00130', 'Balasubramaniam V.', '312/5', '58120')
        },
        {
            'record_number': 'LV-2026-00131',
            'owner_name': 'Revathi Anbarasan',
            'survey_number': '99/2',
            'patta_number': '66412',
            'district': 'Chennai',
            'taluk': 'Guindy',
            'village': 'Velachery',
            'land_area': '2,400 Sq.Ft',
            'document_type': 'Patta Passbook',
            'document_date': '2026-09-15',
            'confidence_score': 95.0,
            'status': 'VERIFIED',
            'priority': 'LOW',
            'issue_description': 'Urban land record verified via CMDA integration check',
            'anomaly_flags': json.dumps([]),
            'duplicate_of_id': None,
            'duplicate_similarity': None,
            'field_confidences': json.dumps({
                'owner_name': 98,
                'survey_number': 95,
                'patta_number': 99,
                'district': 99,
                'taluk': 96,
                'village': 94,
                'land_area': 96,
                'document_type': 99,
                'document_date': 97
            }),
            'validation_checks': json.dumps({
                'required_fields': True,
                'survey_format': True,
                'area_format': True,
                'district_valid': True,
                'village_confidence': True,
                'patta_format': True
            }),
            'officer_remarks': 'Urban land records cleared. Building plan sketch and town survey number match.',
            'verified_by': 'Ramesh V. Sundaram',
            'verified_at': '2026-10-01 11:40:00',
            'qr_hash': generate_record_hash('LV-2026-00131', 'Revathi Anbarasan', '99/2', '66412')
        },
        {
            'record_number': 'LV-2026-00132',
            'owner_name': 'Subramanian Natarajan',
            'survey_number': '156/8B',
            'patta_number': '73921',
            'district': 'Tirunelveli',
            'taluk': 'Ambasamudram',
            'village': 'Kallidaikurichi',
            'land_area': '4.10 Acres',
            'document_type': 'Patta Passbook',
            'document_date': '2026-04-18',
            'confidence_score': 93.0,
            'status': 'VERIFIED',
            'priority': 'LOW',
            'issue_description': 'Verified by Revenue Divisional Officer',
            'anomaly_flags': json.dumps([]),
            'duplicate_of_id': None,
            'duplicate_similarity': None,
            'field_confidences': json.dumps({
                'owner_name': 94,
                'survey_number': 91,
                'patta_number': 97,
                'district': 98,
                'taluk': 93,
                'village': 90,
                'land_area': 92,
                'document_type': 97,
                'document_date': 92
            }),
            'validation_checks': json.dumps({
                'required_fields': True,
                'survey_format': True,
                'area_format': True,
                'district_valid': True,
                'village_confidence': True,
                'patta_format': True
            }),
            'officer_remarks': 'Wetland classification confirmed. Irrigation channel boundaries aligned.',
            'verified_by': 'Priya K. Narayanan',
            'verified_at': '2026-09-28 16:20:45',
            'qr_hash': generate_record_hash('LV-2026-00132', 'Subramanian Natarajan', '156/8B', '73921')
        },
        {
            'record_number': 'LV-2026-00133',
            'owner_name': 'Kavitha Dharmaraj',
            'survey_number': '512/1C',
            'patta_number': '84019',
            'district': 'Erode',
            'taluk': 'Perundurai',
            'village': 'Vijayamangalam',
            'land_area': '3.25 Acres',
            'document_type': 'Sale Deed Excerpt',
            'document_date': '2026-09-25',
            'confidence_score': 65.0,
            'status': 'POTENTIAL_ANOMALY',
            'priority': 'HIGH',
            'issue_description': 'Land area format discrepancy between words and figures',
            'anomaly_flags': json.dumps([
                'Potential anomaly detected: Area written in text differs slightly from numeric figure',
                'Manual verification recommended by Tahsildar desk'
            ]),
            'duplicate_of_id': None,
            'duplicate_similarity': None,
            'field_confidences': json.dumps({
                'owner_name': 84,
                'survey_number': 78,
                'patta_number': 82,
                'district': 94,
                'taluk': 81,
                'village': 79,
                'land_area': 58,
                'document_type': 89,
                'document_date': 83
            }),
            'validation_checks': json.dumps({
                'required_fields': True,
                'survey_format': True,
                'area_format': False,
                'district_valid': True,
                'village_confidence': True,
                'patta_format': True
            }),
            'officer_remarks': None,
            'verified_by': None,
            'verified_at': None,
            'qr_hash': generate_record_hash('LV-2026-00133', 'Kavitha Dharmaraj', '512/1C', '84019')
        },
        {
            'record_number': 'LV-2026-00134',
            'owner_name': 'Dharmalingam P.',
            'survey_number': '88/4',
            'patta_number': '92314',
            'district': 'Salem',
            'taluk': 'Omalur',
            'village': 'Karuppur',
            'land_area': '1.60 Acres',
            'document_type': 'Patta Passbook',
            'document_date': '2026-09-10',
            'confidence_score': 87.0,
            'status': 'PENDING',
            'priority': 'MEDIUM',
            'issue_description': 'Field extraction complete; pending officer signoff',
            'anomaly_flags': json.dumps([]),
            'duplicate_of_id': None,
            'duplicate_similarity': None,
            'field_confidences': json.dumps({
                'owner_name': 89,
                'survey_number': 86,
                'patta_number': 92,
                'district': 95,
                'taluk': 88,
                'village': 84,
                'land_area': 87,
                'document_type': 94,
                'document_date': 86
            }),
            'validation_checks': json.dumps({
                'required_fields': True,
                'survey_format': True,
                'area_format': True,
                'district_valid': True,
                'village_confidence': True,
                'patta_format': True
            }),
            'officer_remarks': None,
            'verified_by': None,
            'verified_at': None,
            'qr_hash': generate_record_hash('LV-2026-00134', 'Dharmalingam P.', '88/4', '92314')
        },
        {
            'record_number': 'LV-2026-00135',
            'owner_name': 'Gopalakrishnan S.',
            'survey_number': '301/2A',
            'patta_number': '11209',
            'district': 'Dindigul',
            'taluk': 'Palani',
            'village': 'Ayakudi',
            'land_area': '4.50 Acres',
            'document_type': 'Patta Passbook',
            'document_date': '2026-07-04',
            'confidence_score': 92.0,
            'status': 'VERIFIED',
            'priority': 'LOW',
            'issue_description': 'Verified and archived in digital vault',
            'anomaly_flags': json.dumps([]),
            'duplicate_of_id': None,
            'duplicate_similarity': None,
            'field_confidences': json.dumps({
                'owner_name': 93,
                'survey_number': 90,
                'patta_number': 96,
                'district': 98,
                'taluk': 92,
                'village': 91,
                'land_area': 93,
                'document_type': 96,
                'document_date': 91
            }),
            'validation_checks': json.dumps({
                'required_fields': True,
                'survey_format': True,
                'area_format': True,
                'district_valid': True,
                'village_confidence': True,
                'patta_format': True
            }),
            'officer_remarks': 'Fruit plantation parcel. Patta chitta matching verified.',
            'verified_by': 'Ramesh V. Sundaram',
            'verified_at': '2026-09-20 09:30:15',
            'qr_hash': generate_record_hash('LV-2026-00135', 'Gopalakrishnan S.', '301/2A', '11209')
        },
        {
            'record_number': 'LV-2026-00136',
            'owner_name': 'Lakshmi Narayanan',
            'survey_number': '62/3B',
            'patta_number': '47182',
            'district': 'Coimbatore',
            'taluk': 'Sulur',
            'village': 'Irugur',
            'land_area': '1.15 Acres',
            'document_type': 'Partition Deed',
            'document_date': '2026-08-05',
            'confidence_score': 79.0,
            'status': 'NEEDS_REVIEW',
            'priority': 'HIGH',
            'issue_description': 'Co-sharer signature watermark low contrast',
            'anomaly_flags': json.dumps([
                'Manual verification recommended for partition share schedule',
                'Document contrast enhanced via OpenCV adaptive threshold'
            ]),
            'duplicate_of_id': None,
            'duplicate_similarity': None,
            'field_confidences': json.dumps({
                'owner_name': 81,
                'survey_number': 79,
                'patta_number': 85,
                'district': 95,
                'taluk': 86,
                'village': 82,
                'land_area': 80,
                'document_type': 88,
                'document_date': 78
            }),
            'validation_checks': json.dumps({
                'required_fields': True,
                'survey_format': True,
                'area_format': True,
                'district_valid': True,
                'village_confidence': True,
                'patta_format': True
            }),
            'officer_remarks': None,
            'verified_by': None,
            'verified_at': None,
            'qr_hash': generate_record_hash('LV-2026-00136', 'Lakshmi Narayanan', '62/3B', '47182')
        }
    ]

    for rec in sample_records:
        cursor.execute('''
        INSERT INTO land_records (
            record_number, owner_name, survey_number, patta_number,
            district, taluk, village, land_area, document_type, document_date,
            confidence_score, status, priority, issue_description, anomaly_flags,
            duplicate_of_id, duplicate_similarity, field_confidences, validation_checks,
            officer_remarks, verified_by, verified_at, qr_hash
        ) VALUES (
            :record_number, :owner_name, :survey_number, :patta_number,
            :district, :taluk, :village, :land_area, :document_type, :document_date,
            :confidence_score, :status, :priority, :issue_description, :anomaly_flags,
            :duplicate_of_id, :duplicate_similarity, :field_confidences, :validation_checks,
            :officer_remarks, :verified_by, :verified_at, :qr_hash
        )
        ''', rec)
        
        # Link verification history for verified ones
        if rec['status'] == 'VERIFIED':
            cursor.execute("SELECT last_insert_rowid()")
            last_id = cursor.fetchone()[0]
            cursor.execute('''
            INSERT INTO verification_history (record_id, officer_name, action, remarks, timestamp)
            VALUES (?, ?, ?, ?, ?)
            ''', (last_id, rec['verified_by'], 'APPROVED', rec['officer_remarks'], rec['verified_at']))

    # Seed Sample Audit Logs
    logs = [
        ('2026-10-04 10:32:00', 'officer_ramesh', 'officer', 'Document Uploaded', 'LV-2026-00125', 'None', 'UPLOADED', 'Scanned Patta Passbook uploaded (PDF 2.4MB)'),
        ('2026-10-04 10:34:15', 'SYSTEM_AI', 'system', 'AI Processing Completed', 'LV-2026-00125', 'UPLOADED', 'PENDING', 'OCR Extraction (91% confidence), 0 critical anomalies'),
        ('2026-10-04 10:36:12', 'officer_ramesh', 'officer', 'Officer Approved', 'LV-2026-00125', 'PENDING', 'VERIFIED', 'Revenue Officer Ramesh verified all land parcel coordinates'),
        ('2026-10-04 11:05:40', 'officer_priya', 'officer', 'Anomaly Flagged', 'LV-2026-00126', 'PENDING', 'POTENTIAL_ANOMALY', 'Survey number format variance & village name confidence low (62%)'),
        ('2026-10-04 11:20:10', 'SYSTEM_AI', 'system', 'Duplicate Flagged', 'LV-2026-00127', 'UPLOADED', 'DUPLICATE_CANDIDATE', '94% similarity detected with existing record LV-2026-00125'),
        ('2026-10-04 12:15:00', 'officer_ramesh', 'officer', 'Verification Report Generated', 'LV-2026-00125', 'VERIFIED', 'VERIFIED', 'Official tamper-evident LandVault verification certificate generated with QR hash'),
        ('2026-10-04 13:45:22', 'citizen_ananya', 'citizen', 'Citizen Patta Search', 'LV-2026-00125', 'VERIFIED', 'VERIFIED', 'Public verification lookup performed for Patta #45892')
    ]
    cursor.executemany('''
    INSERT INTO audit_logs (timestamp, username, role, action, record_id, previous_status, new_status, details)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', logs)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    seed_demo_data()
    print("Database initialized and demo data successfully seeded.")
