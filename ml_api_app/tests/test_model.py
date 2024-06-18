import unittest
from app.models.model import predict

class ModelTestCase(unittest.TestCase):
    def test_predict(self):
        result = predict({"data": "test"})
        self.assertIn("prediction", result)

if __name__ == '__main__':
    unittest.main()
