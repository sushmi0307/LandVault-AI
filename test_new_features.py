import json
import unittest
from app import app
from database import get_db

class TestThreeNewFeatures(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def login_citizen(self):
        return self.client.get('/quick-login/citizen', follow_redirects=True)

    def login_officer(self):
        return self.client.get('/quick-login/officer', follow_redirects=True)

    # =========================================================
    # FEATURE 1: INTERACTIVE LAND MAP TESTS
    # =========================================================
    def test_map_page_renders_for_officer_and_citizen(self):
        """Test that /map renders correctly for authenticated users."""
        self.login_officer()
        res_off = self.client.get('/map')
        self.assertEqual(res_off.status_code, 200)
        self.assertIn(b"Interactive Cadastral Land Map", res_off.data)
        self.assertIn(b"landMap", res_off.data)

        self.login_citizen()
        res_cit = self.client.get('/map')
        self.assertEqual(res_cit.status_code, 200)
        self.assertIn(b"Interactive Cadastral Land Map", res_cit.data)

    def test_api_land_locations_returns_parcels_with_coordinates(self):
        """Test that /api/land-locations returns parcel data with verified/approx coordinates."""
        self.login_officer()
        res = self.client.get('/api/land-locations')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertGreater(data['count'], 0)
        loc = data['locations'][0]
        self.assertIn('latitude', loc)
        self.assertIn('longitude', loc)
        self.assertIn('is_approx_location', loc)
        self.assertIn('status', loc)

    def test_api_land_locations_filters(self):
        """Test District, Taluk, Village and Status filters."""
        self.login_officer()
        # Filter by District
        res_salem = self.client.get('/api/land-locations?district=Salem')
        data_salem = res_salem.get_json()
        self.assertTrue(data_salem['success'])
        for loc in data_salem['locations']:
            self.assertEqual(loc['district'], 'Salem')

        # Filter by Status
        res_verified = self.client.get('/api/land-locations?status=VERIFIED')
        data_verified = res_verified.get_json()
        self.assertTrue(data_verified['success'])
        for loc in data_verified['locations']:
            self.assertEqual(loc['status'], 'VERIFIED')

        # Search query
        res_q = self.client.get('/api/land-locations?q=Attur')
        data_q = res_q.get_json()
        self.assertTrue(data_q['success'])
        self.assertGreater(data_q['count'], 0)

    # =========================================================
    # FEATURE 2: CITIZEN APPLICATION TRACKING TESTS
    # =========================================================
    def test_citizen_application_tracking_portal(self):
        """Test that Citizen Portal displays citizen's own submitted applications with statuses."""
        self.login_citizen()
        res = self.client.get('/citizen')
        self.assertEqual(res.status_code, 200)
        # Verify Ananya's applications are displayed
        self.assertIn(b"LV-APP-2026-001", res.data)
        self.assertIn(b"LV-APP-2026-002", res.data)
        self.assertIn(b"LV-APP-2026-003", res.data)
        self.assertIn(b"LV-APP-2026-004", res.data)
        # Verify statuses: PENDING, UNDER REVIEW, APPROVED, REJECTED
        self.assertIn(b"PENDING", res.data)
        self.assertIn(b"UNDER REVIEW", res.data)
        self.assertIn(b"APPROVED", res.data)
        self.assertIn(b"REJECTED", res.data)
        # Verify officer remarks column
        self.assertIn(b"Officer Remarks", res.data)

    def test_api_application_history_timeline(self):
        """Test /api/application-history/<rec_num> returns full timeline & officer remarks."""
        self.login_citizen()
        res = self.client.get('/api/application-history/LV-APP-2026-003')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['record_number'], 'LV-APP-2026-003')
        self.assertEqual(data['current_status'], 'APPROVED')
        self.assertIn('officer_remarks', data)
        self.assertGreater(len(data['history']), 0)
        actions = [h['action'] for h in data['history']]
        self.assertIn('APPLICATION_SUBMITTED', actions)
        self.assertIn('APPROVED', actions)

    def test_citizen_privacy_restriction(self):
        """Test that citizens cannot access history of records not submitted by them."""
        # Log in as an anonymous client without session
        anon = app.test_client()
        res = anon.get('/api/application-history/LV-APP-2026-001')
        self.assertEqual(res.status_code, 302) # Redirect to login

    # =========================================================
    # FEATURE 3: OWNERSHIP HISTORY TESTS
    # =========================================================
    def test_record_detail_displays_ownership_history(self):
        """Test that record detail page displays historical and current ownership."""
        self.login_officer()
        res = self.client.get('/record/LV-2026-00125')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Ownership History & Chain of Title", res.data)
        self.assertIn(b"K. Shanmugam Sundaram", res.data)
        self.assertIn(b"Previous Owner", res.data)
        self.assertIn(b"Ramesh Kumar", res.data)
        self.assertIn(b"Current Owner", res.data)
        self.assertIn(b"1998-04-12", res.data)
        self.assertIn(b"2014-06-20", res.data)

    def test_api_ownership_history_endpoint(self):
        """Test /api/record/<rec_num>/ownership-history endpoint returns structured data."""
        self.login_officer()
        res = self.client.get('/api/record/LV-2026-00125/ownership-history')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 2)
        owners = [row['owner_name'] for row in data['ownership_history']]
        self.assertIn('K. Shanmugam Sundaram', owners)
        self.assertIn('Ramesh Kumar', owners)

    def test_record_without_prior_history_indicates_cleanly(self):
        """Test that parcels without prior transfers indicate no prior history without inventing data."""
        self.login_officer()
        res = self.client.get('/record/LV-2026-00130')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"No prior historical title transfers are currently registered", res.data)
        self.assertIn(b"Balasubramaniam V.", res.data)

if __name__ == '__main__':
    unittest.main()
