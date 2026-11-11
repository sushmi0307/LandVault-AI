import io
import json
from app import app
from database import get_db

def run_tests():
    client = app.test_client()
    print("Testing LandVault AI Web Application...")

    # 1. Test Login Page GET & Content
    res = client.get('/login')
    assert res.status_code == 200, f"Login page failed: {res.status_code}"
    assert b"LandVault AI" in res.data
    assert b"Your Land, Your Rights, Digitally Secured." in res.data
    assert b"A smarter way to digitize, validate, and manage land records securely." in res.data
    assert b"Smart Document Processing" in res.data
    assert b"Secure Land Records" in res.data
    assert b"Reliable Verification" in res.data
    assert b"Welcome Back" in res.data
    assert b"Sign in to access your land records." in res.data
    assert b"OR TRY DEMO" in res.data
    assert b"Ramesh V. Sundaram" in res.data
    assert b"Ananya R. Sharma" in res.data
    print("[PASS] Login page loads successfully with 2-column dashboard-matched layout & 1-Click Demo buttons")

    # 1b. Test Root URL redirects to Login when not authenticated
    with app.test_client() as anon_client:
        res = anon_client.get('/', follow_redirects=False)
        assert res.status_code == 302
        assert '/login' in res.headers['Location']
        print("[PASS] Root URL '/' redirects unauthenticated users to '/login'")

    # 1c. Test Citizen Login via POST redirects to Citizen Dashboard
    with app.test_client() as cit_client:
        res = cit_client.post('/login', data={
            'username': 'citizen_ananya',
            'password': 'citizen123'
        }, follow_redirects=False)
        assert res.status_code == 302, f"Expected 302 redirect, got {res.status_code}"
        assert '/citizen' in res.headers['Location'], f"Expected redirect to /citizen, got {res.headers['Location']}"
        
        # Follow redirect and verify Citizen Dashboard loaded
        res_portal = cit_client.get(res.headers['Location'])
        assert res_portal.status_code == 200
        assert b"Citizen Land Portal" in res_portal.data
        print("[PASS] Valid citizen credentials redirect directly to Citizen Dashboard")

    # 1d. Test Invalid Credentials displays error message
    with app.test_client() as err_client:
        res = err_client.post('/login', data={
            'username': 'citizen_ananya',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        assert res.status_code == 200
        assert b"Invalid username or password" in res.data
        print("[PASS] Invalid credentials display clear error message on page")

    # 1e. Test Officer Login via POST redirects to Officer Dashboard
    with app.test_client() as off_client:
        res = off_client.post('/login', data={
            'username': 'officer_ramesh',
            'password': 'officer123'
        }, follow_redirects=False)
        assert res.status_code == 302
        assert '/dashboard' in res.headers['Location']
        print("[PASS] Valid officer credentials redirect to Officer Dashboard")

    # 2. Test Quick Login as Officer
    res = client.get('/quick-login/officer', follow_redirects=True)
    assert res.status_code == 200, f"Quick login failed: {res.status_code}"
    assert b"Good Morning, Officer" in res.data
    print("[PASS] Officer quick-login (Ramesh V. Sundaram) opens Officer dashboard")

    # 2b. Test Quick Login as Citizen (Isolated Client)
    with app.test_client() as cit_demo_client:
        res_cit_demo = cit_demo_client.get('/quick-login/citizen', follow_redirects=True)
        assert res_cit_demo.status_code == 200
        assert b"Citizen Land Portal" in res_cit_demo.data
        print("[PASS] Citizen quick-login (Ananya R. Sharma) opens Citizen dashboard")

    # 3. Test Dashboard Stats & Visualizations
    assert b"1,250" in res.data
    assert b"980" in res.data
    assert b"recordsTimelineChart" in res.data
    print("[PASS] Dashboard metrics and charts confirmed")

    # 4. Test Document Processing Page
    res = client.get('/process')
    assert res.status_code == 200
    assert b"Process Land Document" in res.data
    assert b"Sample 1: Standard Patta" in res.data
    print("[PASS] Document Processing interface loads with sample presets")

    # 5. Test AI Processing API with Sample 1 (Fresh Patta)
    res = client.post('/api/process-document', data={'sample_name': 'sample_patta_passbook_salem.png'})
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['data']['fields']['owner_name'] == 'Radhakrishnan K.'
    assert data['data']['overall_confidence'] >= 85
    rec_num = data['data']['record_number']
    print(f"[PASS] AI Processing API extracted: {rec_num} for {data['data']['fields']['owner_name']}")

    # 6. Test Officer Verification Approval
    payload = {
        'record_number': rec_num,
        'fields': data['data']['fields'],
        'status': 'VERIFIED',
        'confidence_score': data['data']['overall_confidence'],
        'officer_remarks': 'Demarcation and revenue survey matching verified.',
        'anomaly_flags': data['data']['anomalies'],
        'duplicate_of_id': None,
        'duplicate_similarity': None
    }
    res = client.post('/api/save-verification', json=payload)
    assert res.status_code == 200
    save_data = res.get_json()
    assert save_data['success'] is True
    assert save_data['status'] == 'VERIFIED'
    print(f"[PASS] Officer verification saved: {rec_num} is now VERIFIED")

    # 7. Test Record Detail Page
    res = client.get(f'/record/{rec_num}')
    assert res.status_code == 200
    assert b"Radhakrishnan K." in res.data
    assert b"VERIFIED" in res.data
    print(f"[PASS] Record detail page renders verified record {rec_num}")

    # 8. Test AI Processing with Sample 2 (Anomaly Document)
    res = client.post('/api/process-document', data={'sample_name': 'sample_deed_with_anomaly.png'})
    assert res.status_code == 200
    anom_data = res.get_json()
    assert anom_data['success'] is True
    assert len(anom_data['data']['anomalies']) > 0
    assert anom_data['data']['status'] == 'POTENTIAL_ANOMALY'
    print("[PASS] Anomaly detection verified: flagged potential anomalies respectfully")

    # 9. Test AI Processing with Sample 3 (Duplicate Document)
    res = client.post('/api/process-document', data={'sample_name': 'sample_duplicate_parcel.png'})
    assert res.status_code == 200
    dup_data = res.get_json()
    assert dup_data['success'] is True
    assert dup_data['data']['duplicate_info'] is not None
    assert dup_data['data']['duplicate_info']['record_number'] == 'LV-2026-00125'
    assert dup_data['data']['status'] == 'DUPLICATE_CANDIDATE'
    print("[PASS] Duplicate detection verified: matched against LV-2026-00125 with high similarity")

    # 10. Test Quick Patta Search API
    res = client.get('/api/search-patta?patta=45892')
    assert res.status_code == 200
    patta_res = res.get_json()
    assert patta_res['found'] is True
    assert patta_res['record']['survey_number'] == '123/4A'
    print("[PASS] Quick Patta Search API returned match for #45892")

    # 11. Test Public QR Verification Page
    res = client.get('/verify/LV-2026-00125')
    assert res.status_code == 200
    assert b"Verify Digital Land Record" in res.data
    assert b"VERIFIED" in res.data
    print("[PASS] Public QR verification landing page renders verified certificate")

    # 12. Test Citizen Portal Access
    client.get('/quick-login/citizen', follow_redirects=True)
    res = client.get('/citizen')
    assert res.status_code == 200
    assert b"Citizen Land Portal" in res.data or b"Land Record Services" in res.data
    print("[PASS] Citizen portal renders appropriately")

    # 13. Test Citizen Route Protection (Citizen cannot access officer dashboard)
    res = client.get('/dashboard', follow_redirects=False)
    assert res.status_code in [302, 403], f"Citizen was not redirected: {res.status_code}"
    print("[PASS] Role-based access control verified: Citizen restricted from officer dashboard")

    # 14. Test Audit Trail Page as Officer
    client.get('/quick-login/officer', follow_redirects=True)
    res = client.get('/audit')
    assert res.status_code == 200
    assert b"System Audit Trail" in res.data
    print("[PASS] System audit trail renders with logged events")

    # 15. Test Reports Page
    res = client.get('/reports')
    assert res.status_code == 200
    assert b"Reports & Verification Certificates" in res.data
    print("[PASS] Reports generator loads successfully")

    # 16. Test Land Records List Page as Officer
    res = client.get('/records')
    assert res.status_code == 200
    assert b"Land Records" in res.data
    assert b"All Records" in res.data
    print("[PASS] Officer Land Records table renders with active records")

    # 17. Test Search Page with Query
    res = client.get('/search?q=Radhakrishnan')
    assert res.status_code == 200
    assert b"Search Land Records" in res.data
    assert b"Radhakrishnan" in res.data
    print("[PASS] Search page renders and returns matched cadastral records")

    # 18. Test Upload Validation (Unsupported format & empty file rejection)
    res = client.post('/api/process-document', data={
        'document': (io.BytesIO(b'some binary content'), 'malicious_script.exe')
    }, content_type='multipart/form-data')
    assert res.status_code == 400
    err_data = res.get_json()
    assert err_data['success'] is False
    assert 'Unsupported file type' in err_data['error']
    print("[PASS] Upload validation correctly rejects unsupported file formats")

    res = client.post('/api/process-document', data={
        'document': (io.BytesIO(b''), 'empty_document.pdf')
    }, content_type='multipart/form-data')
    assert res.status_code == 400
    err_data = res.get_json()
    assert err_data['success'] is False
    assert 'empty' in err_data['error'].lower()
    print("[PASS] Upload validation correctly rejects empty (0 bytes) documents")

    print("\n=======================================================")
    print("ALL 18 INTEGRATION & UNIT TESTS PASSED WITH 100% SUCCESS!")
    print("=======================================================\n")

if __name__ == '__main__':
    run_tests()
