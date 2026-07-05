import unittest
from app.core.security import get_password_hash, verify_password

class SecurityTests(unittest.TestCase):
    def test_password_hash_round_trip(self):
        password = "password123"
        hashed = get_password_hash(password)
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("wrong-password", hashed))

if __name__ == "__main__":
    unittest.main()