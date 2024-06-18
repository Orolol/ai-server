import unittest
from app.main import app

class MainTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_predict(self):
        response = self.app.post('/predict', json={"data": "test"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("prediction", response.get_json())

    def test_chat_interaction(self):
        response = self.app.post('/chat', json={"message": "Hello, how are you?"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("response", response.get_json())
    unittest.main()
