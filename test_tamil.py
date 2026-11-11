"""
Unit & Integration Test Suite for Complete Tamil Language Support in Citizen Portal
"""
import unittest
import json
import re
from html.parser import HTMLParser
from app import app


class TagParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.i18n_keys = set()
        self.i18n_placeholders = set()

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if 'data-i18n' in attr_dict:
            self.i18n_keys.add(attr_dict['data-i18n'])
        if 'data-i18n-placeholder' in attr_dict:
            self.i18n_placeholders.add(attr_dict['data-i18n-placeholder'])


class TamilLanguageTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_01_translation_dictionary_coverage(self):
        """Verify static/js/app.js contains comprehensive en and ta translation dictionaries with matching keys."""
        with open('static/js/app.js', 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('const TRANSLATIONS = {', content)
        self.assertIn('en: {', content)
        self.assertIn('ta: {', content)

        # Check essential Tamil terms from requirements
        tamil_terms = [
            "முகப்புப் பலகை",      # Dashboard
            "எனது நிலப் பதிவுகள்", # My Land Records
            "ஆவணத்தைப் பதிவேற்றவும்", # Upload Document
            "ஆவணத்தைப் பார்க்கவும்", # View Document
            "பதிவிறக்கவும்",       # Download
            "தேடுக",              # Search
            "சரிபார்ப்பு நிலை",   # Verification Status
            "சர்வே எண்",          # Survey Number
            "பட்டா எண்",          # Patta Number
            "மாவட்டம்",           # District
            "வட்டம்",              # Taluk
            "கிராமம்",             # Village
            "நிலத்தின் பரப்பளவு",   # Land Area
            "வெளியேறவும்",         # Logout
            "பதிவுகள் எதுவும் கிடைக்கவில்லை", # No Records Found
            "ஆவணம் வெற்றிகரமாகச் சமர்ப்பிக்கப்பட்டது", # Upload Successful
        ]
        for term in tamil_terms:
            self.assertIn(term, content, f"Expected Tamil term '{term}' not found in static/js/app.js")

    def test_02_citizen_portal_elements_tagged_for_i18n(self):
        """Verify Citizen dashboard template contains data-i18n on all headings, cards, labels, placeholders, and buttons."""
        with open('templates/citizen.html', 'r', encoding='utf-8') as f:
            html = f.read()

        parser = TagParser()
        parser.feed(html)

        # Check key data-i18n tags
        required_i18n_keys = [
            'cit_hero_tag',
            'cit_hero_title',
            'cit_hero_desc',
            'cit_logged_in_label',
            'cit_search_title',
            'cit_search_desc',
            'cit_search_btn',
            'cit_upload_title',
            'cit_upload_desc',
            'cit_presets_title',
            'cit_preset_passbook',
            'cit_preset_chitta',
            'cit_preset_scanned',
            'cit_dropzone_title',
            'cit_dropzone_sub',
            'cit_browse_btn',
            'cit_extract_btn',
            'cit_preview_title',
            'cit_review_title',
            'cit_quality_label',
            'owner_name',
            'survey_number',
            'subdivision_number',
            'patta_number',
            'district',
            'taluk',
            'village',
            'land_area',
            'doc_type',
            'doc_date',
            'cit_remarks_label',
            'notice_title',
            'cit_notice_prefix',
            'cit_notice_suffix',
            'cit_submit_btn',
            'cit_table_title',
            'cit_table_desc',
            'th_record_id',
            'th_owner_name',
            'th_survey_no',
            'th_patta_no',
            'th_village_district',
            'th_submission_date',
            'th_status',
            'th_seal'
        ]

        for key in required_i18n_keys:
            self.assertIn(key, parser.i18n_keys, f"Missing data-i18n attribute: '{key}' in citizen.html")

        # Check placeholders
        required_placeholders = [
            'cit_search_placeholder',
            'ph_owner_name',
            'ph_survey_number',
            'ph_subdivision_number',
            'ph_patta_number',
            'ph_district',
            'ph_taluk',
            'ph_village',
            'ph_land_area',
            'ph_doc_type',
            'ph_doc_date',
            'ph_remarks'
        ]
        for ph in required_placeholders:
            self.assertIn(ph, parser.i18n_placeholders, f"Missing data-i18n-placeholder attribute: '{ph}' in citizen.html")

    def test_03_base_navigation_localization(self):
        """Verify base template has data-i18n on Citizen navigation items."""
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            html = f.read()

        parser = TagParser()
        parser.feed(html)
        self.assertIn('nav_citizen_services', parser.i18n_keys)
        self.assertIn('nav_home', parser.i18n_keys)
        self.assertIn('nav_search_record', parser.i18n_keys)
        self.assertIn('nav_qr_verification', parser.i18n_keys)
        self.assertIn('nav_download_report', parser.i18n_keys)
        self.assertIn('search_placeholder', parser.i18n_placeholders)

    def test_04_set_language_api(self):
        """Verify /api/set-language endpoint sets session and cookie properly."""
        with self.app.test_client() as client:
            resp = client.get('/api/set-language/ta')
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertTrue(data.get('success'))
            self.assertEqual(data.get('lang'), 'ta')
            self.assertIn('landvault_lang=ta', resp.headers.get('Set-Cookie', ''))

            # Check invalid language
            resp_invalid = client.get('/api/set-language/xyz')
            self.assertEqual(resp_invalid.status_code, 400)

    def test_05_citizen_login_and_portal_access(self):
        """Verify Citizen login opens the Citizen dashboard with language switcher."""
        with self.app.test_client() as client:
            resp = client.get('/quick-login/citizen', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Citizen Land Portal', html)
            self.assertIn('data-lang="ta"', html)
            self.assertIn('data-lang="en"', html)

    def test_06_verify_public_page_localization(self):
        """Verify public QR verification certificate has language switcher and localization."""
        with self.app.test_client() as client:
            resp = client.get('/verify/LV-2026-00125')
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('data-i18n="verify_public_title"', html)
            self.assertIn('data-i18n="verify_public_tag"', html)
            self.assertIn('data-i18n="verify_public_pattadhar"', html)
            self.assertIn('data-lang="ta"', html)

    def test_07_record_detail_localization(self):
        """Verify record detail page contains localization tags."""
        with self.app.test_client() as client:
            client.get('/quick-login/citizen')
            resp = client.get('/record/LV-2026-00125')
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('data-i18n="detail_title"', html)
            self.assertIn('data-i18n="doc_info_header"', html)
            self.assertIn('data-i18n="btn_back_home"', html)

    def test_08_reports_page_localization(self):
        """Verify reports & certificate page contains localization tags."""
        with self.app.test_client() as client:
            client.get('/quick-login/citizen')
            resp = client.get('/reports')
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('data-i18n="reports_title"', html)
            self.assertIn('data-i18n="cert_title"', html)
            self.assertIn('data-i18n="cert_disclaimer_title"', html)

    def test_09_search_page_localization(self):
        """Verify search page contains localization tags."""
        with self.app.test_client() as client:
            client.get('/quick-login/citizen')
            resp = client.get('/search?q=Salem')
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('data-i18n="search_page_title"', html)
            self.assertIn('data-i18n="btn_search"', html)
            self.assertIn('data-i18n="th_record_id"', html)

    def test_10_patta_search_api_functioning(self):
        """Verify search Patta API works and returns valid land records."""
        with self.app.test_client() as client:
            resp = client.get('/api/search-patta?patta=45892')
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertTrue(data.get('found'))
            self.assertEqual(data['record']['patta_number'], '45892')


if __name__ == '__main__':
    unittest.main()
