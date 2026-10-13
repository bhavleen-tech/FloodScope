import unittest
from fastapi.testclient import TestClient
from backend.main import app

class APITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.client=TestClient(app)
    def test_health(self):
        r=self.client.get('/api/health'); self.assertEqual(r.status_code,200); self.assertEqual(r.json()['operational'],False)
    def test_demo_is_synthetic(self):
        r=self.client.get('/api/demo-assessment'); self.assertEqual(r.status_code,200); self.assertTrue(r.json()['synthetic'])
    def test_no_ai_route(self):
        r=self.client.post('/api/ai-infer'); self.assertIn(r.status_code,(404,405))
    def test_capabilities(self):
        r=self.client.get('/api/capabilities'); self.assertEqual(r.status_code,200); self.assertNotIn('Optional user-trained UNet inference',r.json()['implemented'])
