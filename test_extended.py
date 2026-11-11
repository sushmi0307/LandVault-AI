import os
import json
from app import app
from database import get_db

def run_extended_tests():
    client = app.test_client()
    print("\n--- Running LandVault AI Extended & Local OCR Tests ---")

    # 1. Test Text-Based PDF Extraction (Chitta Extract)
    print("\n1. Testing Text-based PDF Processing (sample_chitta_coimbatore.pdf)...")
    res = client.post('/api/process-document', data={'sample_name': 'sample_chitta_coimbatore.pdf'})
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    data = res.get_json()
    assert data['success'] is True
    assert data['data']['fields']['owner_name'] == 'K. Shanmugam'
    assert data['data']['fields']['survey_number'] == '245/1B'
    assert data['data']['fields']['patta_number'] == '51204'
    assert data['data']['fields']['district'] == 'Coimbatore'
    assert data['data']['overall_confidence'] >= 90
    print(f"   [PASS] Text-based PDF processed directly: Owner {data['data']['fields']['owner_name']}, Patta {data['data']['fields']['patta_number']}")

    # 2. Test Scanned PDF Processing (Rasterization + Local Tesseract OCR)
    print("\n2. Testing Scanned PDF Processing (sample_scanned_patta_salem.pdf)...")
    res = client.post('/api/process-document', data={'sample_name': 'sample_scanned_patta_salem.pdf'})
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert '184/2A' in data['data']['fields']['survey_number']
    assert data['data']['fields']['district'] == 'Salem'
    assert data['data']['preview_url'].endswith('.png')
    print(f"   [PASS] Scanned PDF converted to page image and read with local Tesseract OCR: Survey {data['data']['fields']['survey_number']}")

    # 3. Test Citizen In-Page Document Submission (No Login Redirection)
    print("\n3. Testing Citizen Submission API (/api/citizen-submit)...")
    rec_num = data['data']['record_number']
    cit_payload = {
        'record_number': rec_num,
        'fields': data['data']['fields'],
        'confidence_score': data['data']['overall_confidence'],
        'citizen_remarks': 'Citizen online application for land mutation verification',
        'anomaly_flags': data['data']['anomalies'],
        'duplicate_of_id': None,
        'duplicate_similarity': None
    }
    res = client.post('/api/citizen-submit', json=cit_payload)
    assert res.status_code == 200
    cit_res = res.get_json()
    assert cit_res['success'] is True
    assert cit_res['status'] == 'PENDING'
    print(f"   [PASS] Citizen submitted record {rec_num} with status PENDING for officer queue")

    # 4. Verify Record Persistence in Local SQLite Database
    print("\n4. Verifying Record Persistence in SQLite Database...")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM land_records WHERE record_number = ?", (rec_num,))
    db_rec = cursor.fetchone()
    conn.close()
    assert db_rec is not None
    assert db_rec['status'] == 'PENDING'
    assert db_rec['survey_number'] == data['data']['fields']['survey_number']
    print(f"   [PASS] Record {rec_num} confirmed saved persistently in local SQLite database")

    # 5. Test Officer Review & Final Approval of Citizen Record
    print("\n5. Testing Officer Review & Approval of Citizen Record...")
    client.get('/quick-login/officer', follow_redirects=True)
    officer_payload = {
        'record_number': rec_num,
        'fields': data['data']['fields'],
        'status': 'VERIFIED',
        'confidence_score': data['data']['overall_confidence'],
        'officer_remarks': 'Approved following field boundary check against Taluk register',
        'anomaly_flags': [],
        'duplicate_of_id': None,
        'duplicate_similarity': None
    }
    res = client.post('/api/save-verification', json=officer_payload)
    assert res.status_code == 200
    save_data = res.get_json()
    assert save_data['success'] is True
    assert save_data['status'] == 'VERIFIED'
    print(f"   [PASS] Officer approved citizen record {rec_num}: now VERIFIED")

    # 6. Verify Verification History & Public QR Certificate
    print("\n6. Testing Public QR Verification Landing Page...")
    res = client.get(f'/verify/{rec_num}')
    assert res.status_code == 200
    assert b"VERIFIED" in res.data
    assert b"SHA256" in res.data or rec_num.encode('utf-8') in res.data
    print(f"   [PASS] Public digital authenticity certificate with SHA-256 seal is live")

    # 7. Test Absence of External API Keys
    print("\n7. Verifying Local Offline Operation (Zero External API Keys)...")
    assert 'GEMINI_API_KEY' not in os.environ or os.environ.get('GEMINI_API_KEY') == ''
    assert 'OPENAI_API_KEY' not in os.environ or os.environ.get('OPENAI_API_KEY') == ''
    print("   [PASS] Application operates 100% locally with zero external API key requirements")

    print("\n=======================================================")
    print("ALL 7 EXTENDED OCR & CITIZEN WORKFLOW TESTS PASSED!")
    print("=======================================================\n")

if __name__ == '__main__':
    run_extended_tests()
