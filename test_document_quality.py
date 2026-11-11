import os
import unittest
from app import app
from ocr_engine import check_document_quality

class TestDocumentQualityChecker(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_check_document_quality_clear_sample(self):
        """Test that sharp, high-quality documents are recognized as clear."""
        img_path = os.path.join('sample_docs', 'sample_patta_passbook_salem.png')
        if os.path.exists(img_path):
            result = check_document_quality(img_path)
            self.assertFalse(result['is_poor_quality'])
            self.assertFalse(result['is_blurry'])
            self.assertIsNone(result['warning'])
            self.assertGreaterEqual(result['blur_score'], 70.0)

    def test_check_document_quality_blurry_sample(self):
        """Test that blurry, out-of-focus documents trigger a quality warning."""
        img_path = os.path.join('sample_docs', 'sample_blurry_patta.png')
        if os.path.exists(img_path):
            result = check_document_quality(img_path)
            self.assertTrue(result['is_poor_quality'])
            self.assertTrue(result['is_blurry'])
            self.assertIsNotNone(result['warning'])
            self.assertIn('blurry', result['warning'].lower())
            self.assertLess(result['blur_score'], 70.0)

    def test_api_check_quality_endpoint_clear(self):
        """Test the /api/check-quality endpoint with a clear sample."""
        res = self.client.post('/api/check-quality', data={'sample_name': 'sample_patta_passbook_salem.png'})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertFalse(data['quality']['is_poor_quality'])
        self.assertIsNone(data['quality']['warning'])

    def test_api_check_quality_endpoint_blurry(self):
        """Test the /api/check-quality endpoint with a blurry sample."""
        res = self.client.post('/api/check-quality', data={'sample_name': 'sample_blurry_patta.png'})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertTrue(data['quality']['is_poor_quality'])
        self.assertTrue(data['quality']['is_blurry'])
        self.assertIn('blurry', data['quality']['warning'].lower())

    def test_pipeline_blurry_warning_and_anomalies(self):
        """Test that the full processing pipeline flags blurry documents in anomalies and updates validation checks."""
        res = self.client.post('/api/process-document', data={'sample_name': 'sample_blurry_patta.png'})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        doc_data = data['data']
        self.assertTrue(doc_data['document_quality']['is_poor_quality'])
        self.assertFalse(doc_data['validation_checks']['quality_valid'])
        self.assertTrue(any('blurry' in a.lower() for a in doc_data['anomalies']))

if __name__ == '__main__':
    unittest.main()
