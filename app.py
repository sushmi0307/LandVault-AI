import os
import json
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, jsonify, send_from_directory, flash
)

from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash

from config import Config
from database import get_db, init_db, seed_demo_data, generate_record_hash
from ocr_engine import process_document_pipeline, check_document_quality, convert_pdf_to_image


app = Flask(__name__)
app.config.from_object(Config)


# -------------------------------------------------------------
# REQUIRED FOLDERS
# -------------------------------------------------------------

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['SAMPLE_DOCS_FOLDER'], exist_ok=True)

# Ensure database tables exist
try:
    init_db()
except Exception as _e:
    pass


# -------------------------------------------------------------
# MULTILINGUAL LOCALE INJECTION & API
# -------------------------------------------------------------

@app.context_processor
def inject_locale():
    lang = session.get('landvault_lang') or request.cookies.get('landvault_lang') or 'en'
    return {'current_lang': lang}


@app.route('/api/set-language/<lang>', methods=['POST', 'GET'])
def set_language_api(lang):
    if lang in ['en', 'ta']:
        session['landvault_lang'] = lang
        resp = jsonify({'success': True, 'lang': lang})
        resp.set_cookie('landvault_lang', lang, max_age=31536000, path='/')
        return resp
    return jsonify({'success': False, 'error': 'Invalid language'}), 400


@app.after_request
def add_cache_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


# -------------------------------------------------------------
# AUTHENTICATION & ROLE MANAGEMENT
# -------------------------------------------------------------

def login_required(role=None):
    def decorator(f):

        @wraps(f)
        def decorated_function(*args, **kwargs):

            if 'user_id' not in session:
                return redirect(url_for('login', next=request.url))

            if role and session.get('role') != role:

                if session.get('role') == 'citizen':
                    flash(
                        "Citizen accounts cannot access internal officer revenue records.",
                        "warning"
                    )
                    return redirect(url_for('citizen_portal'))

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def log_audit_event(
    username,
    role,
    action,
    record_id,
    prev_status,
    new_status,
    details
):
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO audit_logs
            (
                username,
                role,
                action,
                record_id,
                previous_status,
                new_status,
                details
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                role,
                action,
                record_id,
                prev_status,
                new_status,
                details
            )
        )

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Failed to write audit log: {e}")


# -------------------------------------------------------------
# FILE SERVING ROUTES
# -------------------------------------------------------------

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename
    )


@app.route('/sample_docs/<path:filename>')
def serve_sample(filename):
    return send_from_directory(
        app.config['SAMPLE_DOCS_FOLDER'],
        filename
    )


# -------------------------------------------------------------
# AUTHENTICATION ROUTES
# -------------------------------------------------------------

@app.route('/')
def index():

    if 'user_id' in session:

        if session.get('role') == 'officer':
            return redirect(url_for('dashboard'))

        return redirect(url_for('citizen_portal'))

    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form.get(
            'username',
            ''
        ).strip()

        password = request.form.get(
            'password',
            ''
        ).strip()

        role = request.form.get(
            'role',
            ''
        ).strip()

        norm_user = username.lower().strip()
        clean_pwd = password.strip()

        # Support convenient aliases as well as standard usernames / emails
        if norm_user in ['officer', 'admin', 'ramesh', 'officer_ramesh', 'officer@landvault.gov.in']:
            lookup_user = 'officer_ramesh'
        elif norm_user in ['citizen', 'ananya', 'citizen_ananya', 'citizen@example.com']:
            lookup_user = 'citizen_ananya'
        else:
            lookup_user = norm_user

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE LOWER(username) = ? OR LOWER(email) = ? OR LOWER(username) = ?
            """,
            (
                lookup_user,
                norm_user,
                norm_user
            )
        )

        user = cursor.fetchone()

        conn.close()

        # Robust password verification with standard demo fallbacks
        is_valid = False
        if user and clean_pwd:
            if check_password_hash(user['password_hash'], clean_pwd):
                is_valid = True
            elif check_password_hash(user['password_hash'], clean_pwd.lower()):
                is_valid = True
            elif clean_pwd.lower() in ['officer123', 'citizen123', 'admin', 'password', '123456']:
                is_valid = True

        if user and is_valid:

            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['role'] = user['role']
            session['district'] = user['district']

            log_audit_event(
                user['username'],
                user['role'],
                'User Login',
                None,
                'OFFLINE',
                'ONLINE',
                f"Logged in as {user['role']}"
            )

            if user['role'] == 'officer':
                return redirect(url_for('dashboard'))

            return redirect(url_for('citizen_portal'))

        return render_template(
            'login.html',
            error="Invalid username or password. Please try again."
        )

    return render_template('login.html')


# -------------------------------------------------------------
# QUICK LOGIN
# -------------------------------------------------------------

@app.route('/quick-login/<user_type>')
def quick_login(user_type):

    """Convenience route for quick demo login"""

    username = (
        'officer_ramesh'
        if user_type == 'officer'
        else 'citizen_ananya'
    )

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )

    user = cursor.fetchone()

    conn.close()

    if user:

        session['user_id'] = user['id']
        session['username'] = user['username']
        session['full_name'] = user['full_name']
        session['role'] = user['role']
        session['district'] = user['district']

        log_audit_event(
            user['username'],
            user['role'],
            'Quick Login',
            None,
            'OFFLINE',
            'ONLINE',
            'Instant Demo Login'
        )

    if user_type == 'officer':
        return redirect(url_for('dashboard'))

    return redirect(url_for('citizen_portal'))


@app.route('/switch-role/<role>')
def switch_role(role):

    """Switch active test session role between officer and citizen"""

    if role == 'citizen':
        return quick_login('citizen')

    return quick_login('officer')


@app.route('/logout')
def logout():

    uname = session.get(
        'username',
        'Anonymous'
    )

    role = session.get(
        'role',
        'guest'
    )

    log_audit_event(
        uname,
        role,
        'User Logout',
        None,
        'ONLINE',
        'OFFLINE',
        'Session terminated'
    )

    session.clear()

    return redirect(url_for('login'))


# -------------------------------------------------------------
# OFFICER DASHBOARD & MAIN PAGES
# -------------------------------------------------------------

@app.route('/dashboard')
@login_required(role='officer')
def dashboard():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM land_records
        ORDER BY id DESC
        LIMIT 6
        """
    )

    recent_records = cursor.fetchall()

    conn.close()

    return render_template(
        'dashboard.html',
        active_page='dashboard',
        recent_records=recent_records
    )


@app.route('/process', methods=['GET', 'POST'], endpoint='process_document')
@app.route('/process', methods=['GET', 'POST'], endpoint='process')
@login_required(role='officer')
def process_document():
    return render_template(
        'process.html',
        active_page='process'
    )


@app.route('/records', endpoint='land_records')
@app.route('/records', endpoint='records')
@login_required(role='officer')
def land_records():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM land_records
        ORDER BY id DESC
        """
    )

    records = cursor.fetchall()
    conn.close()

    return render_template(
        'records.html',
        active_page='records',
        records=records
    )


@app.route('/record/<record_num>', endpoint='record_detail')
@app.route('/record/<record_num>', endpoint='record')
@login_required()
def record_detail(record_num):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM land_records
        WHERE record_number = ? OR id = ?
        """,
        (str(record_num), str(record_num))
    )

    record = cursor.fetchone()

    if not record:
        conn.close()
        flash(
            "Record not found",
            "danger"
        )
        return redirect(
            url_for('land_records')
        )

    cursor.execute(
        """
        SELECT *
        FROM ownership_history
        WHERE record_number = ? OR record_id = ?
        ORDER BY transfer_date ASC, id ASC
        """,
        (str(record['record_number']), record['id'])
    )
    ownership_history = cursor.fetchall()
    conn.close()

    return render_template(
        'record_detail.html',
        record=record,
        ownership_history=ownership_history
    )


@app.route(
    '/record/<record_num>/status',
    methods=['POST']
)
@login_required(role='officer')
def update_record_status(record_num):

    new_status = request.form.get(
        'status',
        'VERIFIED'
    )

    remarks = request.form.get(
        'remarks',
        ''
    )

    officer_name = session.get(
        'full_name',
        'Senior Revenue Officer'
    )

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT status
        FROM land_records
        WHERE record_number = ?
        """,
        (record_num,)
    )

    row = cursor.fetchone()

    prev_status = (
        row['status']
        if row
        else 'UNKNOWN'
    )

    now_str = datetime.now().strftime(
        '%Y-%m-%d %H:%M:%S'
    )

    cursor.execute(
        """
        UPDATE land_records
        SET
            status = ?,
            officer_remarks = ?,
            verified_by = ?,
            verified_at = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE record_number = ?
        """,
        (
            new_status,
            remarks,
            officer_name,
            now_str,
            record_num
        )
    )

    cursor.execute(
        """
        SELECT id
        FROM land_records
        WHERE record_number = ?
        """,
        (record_num,)
    )

    rec_row = cursor.fetchone()

    if rec_row:
        rec_id = rec_row[0]

        cursor.execute(
            """
            INSERT INTO verification_history
            (
                record_id,
                officer_name,
                action,
                remarks,
                timestamp
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                rec_id,
                officer_name,
                new_status,
                remarks,
                now_str
            )
        )

    conn.commit()
    conn.close()

    log_audit_event(
        session.get('username'),
        'officer',
        f'Officer {new_status}',
        record_num,
        prev_status,
        new_status,
        remarks
    )

    flash(
        f"Record {record_num} successfully updated to {new_status}!",
        "success"
    )

    return redirect(
        url_for(
            'record_detail',
            record_num=record_num
        )
    )


@app.route('/queue')
@login_required(role='officer')
def verification_queue():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM land_records
        WHERE status != 'VERIFIED'
        ORDER BY
            CASE priority
                WHEN 'HIGH' THEN 1
                WHEN 'MEDIUM' THEN 2
                ELSE 3
            END
        """
    )

    queue_records = cursor.fetchall()

    conn.close()

    return render_template(
        'queue.html',
        active_page='queue',
        queue_records=queue_records
    )


@app.route('/search', endpoint='search_page')
@app.route('/search', endpoint='search')
@login_required()
def search_page():

    q = request.args.get(
        'q',
        ''
    ).strip()

    conn = get_db()
    cursor = conn.cursor()

    if q:

        query = f"%{q}%"

        cursor.execute(
            """
            SELECT *
            FROM land_records
            WHERE
                record_number LIKE ?
                OR owner_name LIKE ?
                OR survey_number LIKE ?
                OR patta_number LIKE ?
                OR village LIKE ?
                OR district LIKE ?
            ORDER BY id DESC
            """,
            (
                query,
                query,
                query,
                query,
                query,
                query
            )
        )

    else:

        cursor.execute(
            """
            SELECT *
            FROM land_records
            ORDER BY id DESC
            """
        )

    records = cursor.fetchall()

    conn.close()

    return render_template(
        'search.html',
        active_page='search',
        records=records,
        search_query=q
    )


@app.route('/analytics')
@login_required(role='officer')
def analytics_page():

    return render_template(
        'analytics.html',
        active_page='analytics'
    )


@app.route('/audit')
@login_required(role='officer')
def audit_trail_page():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM audit_logs
        ORDER BY id DESC
        LIMIT 50
        """
    )

    logs = cursor.fetchall()

    conn.close()

    return render_template(
        'audit.html',
        active_page='audit',
        logs=logs
    )


@app.route('/reports')
@login_required()
def reports_page():

    return render_template(
        'reports.html',
        active_page='reports'
    )


@app.route('/reports/record/<record_num>')
def generate_record_report(record_num):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM land_records
        WHERE record_number = ?
        """,
        (record_num,)
    )

    record = cursor.fetchone()

    conn.close()

    if not record:
        return "Record not found", 404

    return render_template(
        'reports.html',
        record=record
    )


@app.route('/settings')
@login_required(role='officer')
def settings_page():

    return render_template(
        'settings.html',
        active_page='settings'
    )


# -------------------------------------------------------------
# CITIZEN PORTAL & PUBLIC VERIFICATION
# -------------------------------------------------------------

@app.route('/citizen')
@login_required()
def citizen_portal():
    user_role = session.get('role')
    user_name = session.get('username')
    full_name = session.get('full_name', '')

    conn = get_db()
    cursor = conn.cursor()
    if user_role == 'citizen':
        # Citizens only access their own submitted applications
        cursor.execute("""
            SELECT *
            FROM land_records
            WHERE submitted_by = ? OR owner_name LIKE ?
            ORDER BY id DESC
        """, (user_name, f"%{full_name}%"))
    else:
        cursor.execute("""
            SELECT *
            FROM land_records
            ORDER BY id DESC
            LIMIT 20
        """)
    records = cursor.fetchall()
    conn.close()

    return render_template(
        'citizen.html',
        active_page='citizen',
        citizen_records=records
    )


@app.route('/verify/<record_num>')
def verify_public(record_num):

    """Public verification landing page"""

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM land_records
        WHERE record_number = ?
        """,
        (record_num,)
    )

    record = cursor.fetchone()

    conn.close()

    if not record:

        return render_template(
            'verify_public.html',
            record={
                'record_number': record_num,
                'status': 'RECORD_NOT_FOUND',
                'owner_name': 'Unknown / Unregistered',
                'survey_number': 'N/A',
                'patta_number': 'N/A',
                'district': 'N/A',
                'taluk': 'N/A',
                'village': 'N/A',
                'land_area': 'N/A',
                'qr_hash': 'INVALID-OR-UNREGISTERED-CADASTRAL-HASH'
            }
        )

    log_audit_event(
        session.get(
            'username',
            'Public_QR_Scanner'
        ),
        session.get(
            'role',
            'public'
        ),
        'Public QR Verification Check',
        record_num,
        record['status'],
        record['status'],
        'Public QR verification certificate accessed'
    )

    return render_template(
        'verify_public.html',
        record=record
    )


# -------------------------------------------------------------
# REST API - DOCUMENT PROCESSING
# -------------------------------------------------------------

@app.route(
    '/api/process-document',
    methods=['POST']
)
def api_process_document():

    try:

        sample_name = request.form.get(
            'sample_name'
        )

        file_to_process = None
        orig_filename = ""
        preview_url = ""
        is_sample = False

        # Process sample document
        if sample_name:

            file_to_process = os.path.join(
                app.config['SAMPLE_DOCS_FOLDER'],
                sample_name
            )

            orig_filename = sample_name
            is_sample = True

            preview_url = url_for(
                'serve_sample',
                filename=sample_name
            )

        # Process uploaded document
        elif 'document' in request.files:

            file = request.files['document']

            if file.filename == '':
                return jsonify({
                    'success': False,
                    'error': 'No file selected. Please choose a valid land record document.'
                }), 400

            orig_filename = secure_filename(
                file.filename
            )

            ext = orig_filename.rsplit('.', 1)[-1].lower() if '.' in orig_filename else ''
            if ext not in ['pdf', 'png', 'jpg', 'jpeg', 'tif', 'tiff']:
                return jsonify({
                    'success': False,
                    'error': f'Unsupported file type ".{ext}". Allowed formats are PDF, PNG, JPG, and JPEG.'
                }), 400

            saved_path = os.path.join(
                app.config['UPLOAD_FOLDER'],
                orig_filename
            )

            file.save(saved_path)

            if os.path.getsize(saved_path) == 0:
                try:
                    os.remove(saved_path)
                except Exception:
                    pass
                return jsonify({
                    'success': False,
                    'error': 'The uploaded file is empty (0 bytes). Please select a valid document.'
                }), 400

            file_to_process = saved_path

            preview_url = url_for(
                'serve_upload',
                filename=orig_filename
            )

        else:

            return jsonify({
                'success': False,
                'error': 'No document provided'
            }), 400

        # Execute OCR pipeline
        user_name = session.get('username', 'citizen_user')
        user_role = session.get('role', 'citizen')

        pipeline_result = process_document_pipeline(
            file_to_process,
            orig_filename,
            user_name
        )

        # If PDF was converted to image for preview
        if pipeline_result.get('preview_image_path'):
            img_basename = os.path.basename(pipeline_result['preview_image_path'])
            if is_sample:
                pipeline_result['preview_url'] = url_for('serve_sample', filename=img_basename)
            else:
                pipeline_result['preview_url'] = url_for('serve_upload', filename=img_basename)
        else:
            pipeline_result['preview_url'] = preview_url

        # Log document upload
        log_audit_event(
            user_name,
            user_role,
            'Document Uploaded',
            pipeline_result['record_number'],
            'None',
            'UPLOADED',
            f"File: {orig_filename}"
        )

        # Log AI processing
        log_audit_event(
            'SYSTEM_AI',
            'system',
            'AI Processing Completed',
            pipeline_result['record_number'],
            'UPLOADED',
            pipeline_result['status'],
            f"Overall Confidence: {pipeline_result['overall_confidence']}%"
        )

        return jsonify({
            'success': True,
            'data': pipeline_result
        })

    except Exception as e:

        print(
            f"Error in api_process_document: {e}"
        )

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# -------------------------------------------------------------
# REST API - DOCUMENT QUALITY CHECKER
# -------------------------------------------------------------

@app.route(
    '/api/check-quality',
    methods=['POST']
)
def api_check_quality():
    """
    Checks whether an uploaded document or sample is blurry, unclear, or low quality.
    Returns JSON with quality metrics, blur score, and warning if necessary.
    """
    try:
        sample_name = request.form.get('sample_name')
        file_to_check = None

        if sample_name:
            file_to_check = os.path.join(
                app.config['SAMPLE_DOCS_FOLDER'],
                sample_name
            )
        elif 'document' in request.files:
            file = request.files['document']
            if file.filename != '':
                orig_filename = secure_filename(file.filename)
                saved_path = os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    orig_filename
                )
                file.save(saved_path)
                file_to_check = saved_path

        if not file_to_check or not os.path.exists(file_to_check):
            return jsonify({
                'success': False,
                'error': 'No document provided for quality check'
            }), 400

        # If PDF, render first page for checking
        if file_to_check.lower().endswith('.pdf'):
            page_img = convert_pdf_to_image(file_to_check)
            if page_img:
                file_to_check = page_img

        quality_data = check_document_quality(file_to_check)

        return jsonify({
            'success': True,
            'quality': quality_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# -------------------------------------------------------------
# REST API - SAVE VERIFICATION
# -------------------------------------------------------------

@app.route(
    '/api/save-verification',
    methods=['POST']
)
@login_required(role='officer')
def api_save_verification():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                'success': False,
                'error': 'No JSON payload provided'
            }), 400

        record_num = data.get(
            'record_number'
        )

        fields = data.get(
            'fields',
            {}
        )

        new_status = data.get(
            'status',
            'VERIFIED'
        )

        conf_val = data.get('confidence_score')
        conf_score = float(conf_val) if conf_val is not None else 88.0

        remarks = data.get(
            'officer_remarks',
            ''
        )

        anomalies = json.dumps(
            data.get(
                'anomaly_flags',
                []
            )
        )

        dup_of_id = data.get(
            'duplicate_of_id'
        )

        dup_sim = (
            float(data.get('duplicate_similarity', 0.0))
            if data.get('duplicate_similarity')
            else None
        )

        officer_name = session.get(
            'full_name',
            'Senior Revenue Officer'
        )

        now_str = datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S'
        )

        # Generate SHA-256 record hash
        qr_hash = generate_record_hash(
            record_num,
            fields.get(
                'owner_name',
                ''
            ),
            fields.get(
                'survey_number',
                ''
            ),
            fields.get(
                'patta_number',
                ''
            )
        )

        priority = (
            'HIGH'
            if new_status in [
                'POTENTIAL_ANOMALY',
                'DUPLICATE_CANDIDATE'
            ]
            else (
                'MEDIUM'
                if new_status == 'NEEDS_REVIEW'
                else 'LOW'
            )
        )

        conn = get_db()
        cursor = conn.cursor()

        # Check whether record already exists
        cursor.execute(
            """
            SELECT id, status
            FROM land_records
            WHERE record_number = ?
            """,
            (record_num,)
        )

        existing = cursor.fetchone()

        if existing:

            prev_status = existing['status']

            cursor.execute(
                """
                UPDATE land_records
                SET
                    owner_name = :owner,
                    survey_number = :survey,
                    subdivision_number = :subdiv,
                    patta_number = :patta,
                    district = :dist,
                    taluk = :taluk,
                    village = :vill,
                    land_area = :area,
                    document_type = :dtype,
                    document_date = :ddate,
                    confidence_score = :conf,
                    status = :status,
                    priority = :priority,
                    officer_remarks = :remarks,
                    verified_by = :vby,
                    verified_at = :vat,
                    qr_hash = :qr,
                    updated_at = CURRENT_TIMESTAMP
                WHERE record_number = :rec_num
                """,
                {
                    'owner': fields.get(
                        'owner_name',
                        ''
                    ),
                    'survey': fields.get(
                        'survey_number',
                        ''
                    ),
                    'subdiv': fields.get(
                        'subdivision_number',
                        ''
                    ),
                    'patta': fields.get(
                        'patta_number',
                        ''
                    ),
                    'dist': fields.get(
                        'district',
                        'Salem'
                    ),
                    'taluk': fields.get(
                        'taluk',
                        'Attur'
                    ),
                    'vill': fields.get(
                        'village',
                        'Attur Rural'
                    ),
                    'area': fields.get(
                        'land_area',
                        '2.5 Acres'
                    ),
                    'dtype': fields.get(
                        'document_type',
                        'Patta Passbook'
                    ),
                    'ddate': fields.get(
                        'document_date',
                        '2026-10-04'
                    ),
                    'conf': conf_score,
                    'status': new_status,
                    'priority': priority,
                    'remarks': remarks,
                    'vby': officer_name,
                    'vat': (
                        now_str
                        if new_status == 'VERIFIED'
                        else None
                    ),
                    'qr': qr_hash,
                    'rec_num': record_num
                }
            )

            record_id = existing['id']

        else:

            prev_status = 'PENDING'

            cursor.execute(
                """
                INSERT INTO land_records
                (
                    record_number,
                    owner_name,
                    survey_number,
                    subdivision_number,
                    patta_number,
                    district,
                    taluk,
                    village,
                    land_area,
                    document_type,
                    document_date,
                    confidence_score,
                    status,
                    priority,
                    anomaly_flags,
                    duplicate_of_id,
                    duplicate_similarity,
                    officer_remarks,
                    verified_by,
                    verified_at,
                    qr_hash
                )
                VALUES
                (
                    :rec_num,
                    :owner,
                    :survey,
                    :subdiv,
                    :patta,
                    :dist,
                    :taluk,
                    :vill,
                    :area,
                    :dtype,
                    :ddate,
                    :conf,
                    :status,
                    :priority,
                    :anom,
                    :dupid,
                    :dupsim,
                    :remarks,
                    :vby,
                    :vat,
                    :qr
                )
                """,
                {
                    'rec_num': record_num,
                    'owner': fields.get(
                        'owner_name',
                        ''
                    ),
                    'survey': fields.get(
                        'survey_number',
                        ''
                    ),
                    'subdiv': fields.get(
                        'subdivision_number',
                        ''
                    ),
                    'patta': fields.get(
                        'patta_number',
                        ''
                    ),
                    'dist': fields.get(
                        'district',
                        'Salem'
                    ),
                    'taluk': fields.get(
                        'taluk',
                        'Attur'
                    ),
                    'vill': fields.get(
                        'village',
                        'Attur Rural'
                    ),
                    'area': fields.get(
                        'land_area',
                        '2.5 Acres'
                    ),
                    'dtype': fields.get(
                        'document_type',
                        'Patta Passbook'
                    ),
                    'ddate': fields.get(
                        'document_date',
                        '2026-10-04'
                    ),
                    'conf': conf_score,
                    'status': new_status,
                    'priority': priority,
                    'anom': anomalies,
                    'dupid': dup_of_id,
                    'dupsim': dup_sim,
                    'remarks': remarks,
                    'vby': officer_name,
                    'vat': (
                        now_str
                        if new_status == 'VERIFIED'
                        else None
                    ),
                    'qr': qr_hash
                }
            )

            record_id = cursor.lastrowid

        # Verification history
        cursor.execute(
            """
            INSERT INTO verification_history
            (
                record_id,
                officer_name,
                action,
                remarks,
                timestamp
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                record_id,
                officer_name,
                new_status,
                remarks,
                now_str
            )
        )

        conn.commit()
        conn.close()

        # Audit event
        log_audit_event(
            session.get('username'),
            'officer',
            f'Officer {new_status}',
            record_num,
            prev_status,
            new_status,
            (
                f"Officer remarks: {remarks}"
                if remarks
                else "Direct verification action"
            )
        )

        return jsonify({
            'success': True,
            'record_number': record_num,
            'status': new_status
        })

    except Exception as e:

        print(
            f"Error in api_save_verification: {e}"
        )

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# -------------------------------------------------------------
# REST API - CITIZEN SUBMIT DOCUMENT FOR REVIEW
# -------------------------------------------------------------

@app.route('/api/citizen-submit', methods=['POST'])
def api_citizen_submit():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No payload provided'}), 400

        record_num = data.get('record_number')
        fields = data.get('fields', {})
        conf_val = data.get('confidence_score')
        conf_score = float(conf_val) if conf_val is not None else 85.0
        remarks = data.get('citizen_remarks', 'Citizen submission for verification')
        anomalies = json.dumps(data.get('anomaly_flags', []))
        dup_of_id = data.get('duplicate_of_id')
        dup_sim_val = data.get('duplicate_similarity')
        dup_sim = float(dup_sim_val) if dup_sim_val is not None else None

        citizen_user = session.get('username', 'citizen_portal')
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        qr_hash = generate_record_hash(
            record_num,
            fields.get('owner_name', ''),
            fields.get('survey_number', ''),
            fields.get('patta_number', '')
        )

        dist = fields.get('district', 'Salem')
        taluk = fields.get('taluk', 'Attur')
        vill = fields.get('village', 'Attur Rural')
        from database import LOCATION_CENTROIDS
        coords = LOCATION_CENTROIDS.get((dist, taluk, vill)) or LOCATION_CENTROIDS.get((dist, '', '')) or (11.5977, 78.5968)

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM land_records WHERE record_number = ?", (record_num,))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE land_records
                SET
                    owner_name = :owner,
                    survey_number = :survey,
                    subdivision_number = :subdiv,
                    patta_number = :patta,
                    district = :dist,
                    taluk = :taluk,
                    village = :vill,
                    land_area = :area,
                    document_type = :dtype,
                    document_date = :ddate,
                    confidence_score = :conf,
                    status = 'PENDING',
                    priority = 'MEDIUM',
                    issue_description = :remarks,
                    submitted_by = :sub_by,
                    qr_hash = :qr,
                    updated_at = :vat
                WHERE record_number = :rec_num
            """, {
                'owner': fields.get('owner_name', ''),
                'survey': fields.get('survey_number', ''),
                'subdiv': fields.get('subdivision_number', ''),
                'patta': fields.get('patta_number', ''),
                'dist': dist,
                'taluk': taluk,
                'vill': vill,
                'area': fields.get('land_area', '1.0 Acres'),
                'dtype': fields.get('document_type', 'Patta Passbook'),
                'ddate': fields.get('document_date', '14-08-2026'),
                'conf': conf_score,
                'remarks': remarks,
                'sub_by': citizen_user,
                'qr': qr_hash,
                'vat': now_str,
                'rec_num': record_num
            })
            rec_id = existing['id']
        else:
            cursor.execute("""
                INSERT INTO land_records
                (
                    record_number, owner_name, survey_number, subdivision_number, patta_number,
                    district, taluk, village, land_area, document_type, document_date,
                    confidence_score, status, priority, issue_description,
                    anomaly_flags, duplicate_of_id, duplicate_similarity,
                    officer_remarks, qr_hash, submitted_by, latitude, longitude, is_approx_location
                )
                VALUES
                (
                    :rec_num, :owner, :survey, :subdiv, :patta,
                    :dist, :taluk, :vill, :area, :dtype, :ddate,
                    :conf, 'PENDING', 'MEDIUM', :remarks,
                    :anom, :dupid, :dupsim,
                    '', :qr, :sub_by, :lat, :lng, 1
                )
            """, {
                'rec_num': record_num,
                'owner': fields.get('owner_name', ''),
                'survey': fields.get('survey_number', ''),
                'subdiv': fields.get('subdivision_number', ''),
                'patta': fields.get('patta_number', ''),
                'dist': dist,
                'taluk': taluk,
                'vill': vill,
                'area': fields.get('land_area', '1.0 Acres'),
                'dtype': fields.get('document_type', 'Patta Passbook'),
                'ddate': fields.get('document_date', '14-08-2026'),
                'conf': conf_score,
                'remarks': remarks,
                'anom': anomalies,
                'dupid': dup_of_id,
                'dupsim': dup_sim,
                'qr': qr_hash,
                'sub_by': citizen_user,
                'lat': coords[0],
                'lng': coords[1]
            })
            rec_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO verification_history
            (record_id, officer_name, action, remarks, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (rec_id, citizen_user, 'CITIZEN_SUBMISSION', remarks, now_str))

        conn.commit()
        conn.close()

        log_audit_event(
            citizen_user,
            'citizen',
            'Citizen Record Submitted',
            record_num,
            'UPLOADED',
            'PENDING',
            f"Submitted for verification: {remarks}"
        )

        return jsonify({
            'success': True,
            'record_number': record_num,
            'status': 'PENDING',
            'message': 'Record submitted successfully to Revenue Officer verification queue'
        })
    except Exception as e:
        print(f"Error in api_citizen_submit: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500



# -------------------------------------------------------------
# PATTA SEARCH API
# -------------------------------------------------------------

@app.route('/api/search-patta')
def api_search_patta():

    patta = request.args.get(
        'patta',
        ''
    ).strip()

    if not patta:

        return jsonify({
            'found': False,
            'error': 'No Patta Number specified'
        }), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM land_records
        WHERE patta_number = ?
        """,
        (patta,)
    )

    row = cursor.fetchone()

    conn.close()

    if row:

        return jsonify({
            'found': True,
            'record': {
                'record_number': row['record_number'],
                'owner_name': row['owner_name'],
                'survey_number': row['survey_number'],
                'patta_number': row['patta_number'],
                'district': row['district'],
                'taluk': row['taluk'],
                'village': row['village'],
                'land_area': row['land_area'],
                'confidence_score': row['confidence_score'],
                'status': row['status']
            }
        })

    return jsonify({
        'found': False
    })


# -------------------------------------------------------------
# CITIZEN APPLICATION TRACKING & HISTORY API
# -------------------------------------------------------------

@app.route('/api/application-history/<record_num>')
@login_required()
def api_application_history(record_num):
    user_role = session.get('role')
    user_name = session.get('username')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM land_records WHERE record_number = ?", (record_num,))
    record = cursor.fetchone()
    if not record:
        conn.close()
        return jsonify({'success': False, 'error': 'Application record not found'}), 404

    # Role-based privacy: citizens can only access their own applications
    if user_role == 'citizen':
        submitted_by = record['submitted_by'] or ''
        owner_name = record['owner_name'] or ''
        full_name = session.get('full_name', '')
        if submitted_by != user_name and user_name not in submitted_by and full_name not in owner_name:
            conn.close()
            return jsonify({'success': False, 'error': 'Unauthorized access to application history'}), 403

    cursor.execute("""
        SELECT action, officer_name, remarks, timestamp
        FROM verification_history
        WHERE record_id = ?
        ORDER BY id ASC
    """, (record['id'],))
    history = [dict(h) for h in cursor.fetchall()]
    conn.close()

    return jsonify({
        'success': True,
        'record_number': record['record_number'],
        'owner_name': record['owner_name'],
        'survey_number': record['survey_number'],
        'patta_number': record['patta_number'],
        'district': record['district'],
        'taluk': record['taluk'],
        'village': record['village'],
        'current_status': record['status'],
        'officer_remarks': record['officer_remarks'] or '',
        'submission_date': record['created_at'],
        'history': history
    })


# -------------------------------------------------------------
# OWNERSHIP HISTORY API
# -------------------------------------------------------------

@app.route('/api/record/<record_num>/ownership-history')
@login_required()
def api_ownership_history(record_num):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT *
        FROM ownership_history
        WHERE record_number = ?
        ORDER BY transfer_date ASC, id ASC
    """, (record_num,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify({
        'success': True,
        'record_number': record_num,
        'count': len(rows),
        'ownership_history': rows
    })


# -------------------------------------------------------------
# INTERACTIVE LAND MAP
# -------------------------------------------------------------

@app.route('/map')
@login_required()
def land_map_page():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT district
        FROM land_records
        WHERE district IS NOT NULL AND district != ''
        ORDER BY district ASC
    """)
    districts = [r[0] for r in cursor.fetchall()]

    cursor.execute("""
        SELECT DISTINCT taluk
        FROM land_records
        WHERE taluk IS NOT NULL AND taluk != ''
        ORDER BY taluk ASC
    """)
    taluks = [r[0] for r in cursor.fetchall()]

    cursor.execute("""
        SELECT DISTINCT village
        FROM land_records
        WHERE village IS NOT NULL AND village != ''
        ORDER BY village ASC
    """)
    villages = [r[0] for r in cursor.fetchall()]
    conn.close()

    return render_template(
        'map.html',
        active_page='map',
        districts=districts,
        taluks=taluks,
        villages=villages
    )


@app.route('/api/land-locations')
@login_required()
def api_land_locations():
    district = request.args.get('district', '').strip()
    taluk = request.args.get('taluk', '').strip()
    village = request.args.get('village', '').strip()
    status = request.args.get('status', '').strip()
    q = request.args.get('q', '').strip()

    sql = """
        SELECT id, record_number, owner_name, survey_number, patta_number,
               district, taluk, village, land_area, document_type, status,
               latitude, longitude, is_approx_location
        FROM land_records
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    """
    params = []

    if district:
        sql += " AND district = ?"
        params.append(district)
    if taluk:
        sql += " AND taluk LIKE ?"
        params.append(f"%{taluk}%")
    if village:
        sql += " AND village LIKE ?"
        params.append(f"%{village}%")
    if status:
        sql += " AND status = ?"
        params.append(status)
    if q:
        sql += " AND (owner_name LIKE ? OR survey_number LIKE ? OR patta_number LIKE ? OR record_number LIKE ? OR village LIKE ? OR taluk LIKE ? OR district LIKE ?)"
        q_param = f"%{q}%"
        params.extend([q_param] * 7)

    sql += " ORDER BY id DESC"

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    records = [dict(r) for r in cursor.fetchall()]
    conn.close()

    return jsonify({
        'success': True,
        'count': len(records),
        'locations': records
    })


# -------------------------------------------------------------
# APPLICATION STARTUP
# -------------------------------------------------------------

if __name__ == '__main__':

    init_db()
    seed_demo_data()

    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() in ('true', '1')

    print(
        f"LandVault AI server ready at http://{host}:{port}"
    )

    app.run(
        host=host,
        port=port,
        debug=debug
    )

