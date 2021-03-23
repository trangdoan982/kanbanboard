import os
import unittest
import sys
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from app import app, db


TEST_DB = 'test.db'

class Tests(unittest.TestCase):
    '''
    Execute prior to each test.
    '''
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        self.app = app.test_client()


    def test_home_page(self):
        '''Test that home page is loaded'''
        req = self.app.get('/', follow_redirects=True)
        self.assertEqual(req.status_code, 200)

    


if __name__ == "__main__":
    unittest.main()