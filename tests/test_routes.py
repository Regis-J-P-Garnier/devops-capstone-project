"""
Account API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
import json
import http
from unittest import TestCase
from tests.factories import AccountFactory
from service.common import status  # HTTP Status Codes
from service.models import db, Account, init_db
from service.routes import app

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/accounts"


######################################################################
#  T E S T   C A S E S
######################################################################
class TestAccountService(TestCase):
    """Account Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.DEBUG)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Runs once before test suite"""

    def setUp(self):
        """Runs before each test"""
        db.session.query(Account).delete()  # clean up the last tests
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Runs once after each test case"""
        db.session.remove()
            

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_accounts(self, count, is_json=False):
        """Factory method to create accounts in bulk"""
        accounts = []
        for _ in range(count):
            account = AccountFactory()
            response = self.client.post(BASE_URL, json=account.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Account",
            )
            new_account = response.get_json()
            account.id = new_account["id"]
            if is_json:
                accounts.append(account.serialize())    
            else:
                accounts.append(account)
        return accounts
    
    def _create_account(self, is_json=False):
        """Factory method to create one account"""
        accounts = self._create_accounts(1, is_json)
        return accounts[0]
    
    def are_accounts_json_equals(self, account_a, account_b):
        are_equals =  True
        are_equals = are_equals and (account_a["id"] == account_b["id"])
        are_equals = are_equals and (account_a["name"] == account_b["name"])
        are_equals = are_equals and (account_a["email"] == account_b["email"])
        are_equals = are_equals and (account_a["address"] == account_b["address"])
        are_equals = are_equals and (account_a["phone_number"] == account_b["phone_number"])
        are_equals = are_equals and (account_a["date_joined"] == account_b["date_joined"])        
        return are_equals

    ######################################################################
    #  A C C O U N T   T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should get 200_OK from the Home Page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_health(self):
        """It should be healthy"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")

    def test_create_account(self):
        """It should Create a new Account"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_account = response.get_json()
        self.assertEqual(new_account["name"], account.name)
        self.assertEqual(new_account["email"], account.email)
        self.assertEqual(new_account["address"], account.address)
        self.assertEqual(new_account["phone_number"], account.phone_number)
        self.assertEqual(new_account["date_joined"], str(account.date_joined))

    def test_bad_request(self):
        """It should not Create an Account when sending the wrong data"""
        response = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create an Account when sending the wrong media type"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="test/html"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    # ADD YOUR TEST CASES HERE ...
    
    # READ AN ACCOUNT ####################################################
    # ... place you code here to READ an account ...
    def test_read_account(self):
        """It should read an existing Account"""
        # create with factory helper
        new_account_json = self._create_account(is_json=True)
        
        # client read 
        new_account_id = new_account_json["id"]
        retrieve_response = self.client.get(
            f"{BASE_URL}/{new_account_id}", 
            content_type="application/json"
        )
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        retrieved_account_json = retrieve_response.get_json()
        
        # Valid retrieved data
        self.assertTrue(
            self.are_accounts_json_equals(
                new_account_json,
                retrieved_account_json
                )
            )

    def test_account_not_found(self):
        """It should not read a not existing Account"""
        # client read
        new_account_id = 0 # can't exist
        retrieve_response = self.client.get(
            f"{BASE_URL}/{new_account_id}", 
            content_type="application/json"
        )
        self.assertEqual(retrieve_response.status_code, status.HTTP_404_NOT_FOUND)
        
    # DELETE AN ACCOUNT ##################################################
    def test_delete_account(self):
        """It should Delete an Account"""
        # create with factory helper
        new_account_json = self._create_account(is_json=True)
        # client delete 
        new_account_id = new_account_json["id"]
        resp = self.client.delete(f"{BASE_URL}/{new_account_id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_account_delete_not_found(self):
        """It should not read a not existing Account"""
        # client read
        new_account_id = 0 # can't exist
        retrieve_response = self.client.delete(
            f"{BASE_URL}/{new_account_id}", 
            content_type="application/json"
        )
        self.assertEqual(retrieve_response.status_code, status.HTTP_204_NO_CONTENT) 

    # UPDATE AN EXISTING ACCOUNT #########################################

    
      
    # LIST ALL ACCOUNTS ##################################################

    # ... place you code here to LIST accounts ...
    """
    List

        List should use the Account.all() method to return all of the accounts as a list of dict and return the HTTP_200_OK return code.
        It should never send back a 404_NOT_FOUND. If you do not find any accounts, send back an empty list ([]) and 200_OK.
    """





