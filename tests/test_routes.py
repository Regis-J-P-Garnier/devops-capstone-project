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
from service import talisman
from service.common import status  # HTTP Status Codes
from service.models import db, Account, init_db
from service.routes import app

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/accounts"
HTTPS_ENVIRON = {'wsgi.url_scheme': 'https'}

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
        talisman.force_https = False

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
        are_equals = True
        are_equals = are_equals and (account_a["id"] == account_b["id"])
        are_equals = are_equals and (account_a["name"] == account_b["name"])
        are_equals = are_equals and (account_a["email"] == account_b["email"])
        are_equals = are_equals and (
            account_a["address"] == account_b["address"])
        are_equals = are_equals and (
            account_a["phone_number"] == account_b["phone_number"])
        are_equals = are_equals and (
            account_a["date_joined"] == account_b["date_joined"])
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
        self.assertEqual(response.status_code,
                         status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

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
        new_account_id = 0  # can't exist
        retrieve_response = self.client.get(
            f"{BASE_URL}/{new_account_id}",
            content_type="application/json"
        )
        self.assertEqual(retrieve_response.status_code,
                         status.HTTP_404_NOT_FOUND)

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
        """It should not delete a not existing Account"""
        # client read
        new_account_id = 0  # can't exist
        retrieve_response = self.client.delete(
            f"{BASE_URL}/{new_account_id}",
            content_type="application/json"
        )
        self.assertEqual(retrieve_response.status_code,
                         status.HTTP_204_NO_CONTENT)

    # UPDATE AN EXISTING ACCOUNT #########################################
    def test_update_account(self):
        """It should Update an existing Account"""
        test_str = "dummy string for testing purpose only"
        # create
        new_account_json = self._create_account(is_json=True)
        self.assertNotEqual(new_account_json["name"], test_str)
        # update
        new_account_json["name"] = test_str
        update_response = self.client.put(
            f"{BASE_URL}/{new_account_json['id']}", json=new_account_json)
        # Valid retrieved data
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        updated_account_json = update_response.get_json()
        self.assertEqual(updated_account_json["name"], test_str)
        self.assertTrue(
            self.are_accounts_json_equals(
                new_account_json,
                updated_account_json
            )
        )

    def test_account_update_not_found(self):
        """It should not update a not existing Account"""
        # client update
        new_account_id = 0  # can't exist
        retrieve_response = self.client.put(
            f"{BASE_URL}/{new_account_id}",
            content_type="application/json"
        )
        self.assertEqual(retrieve_response.status_code,
                         status.HTTP_404_NOT_FOUND)

    # LIST ALL ACCOUNTS ##################################################

    # ... place you code here to LIST accounts ...
    def test_get_account_list(self):
        """It should Get a list of Accounts"""
        # create
        created_number = 5
        new_accounts_json_list = self._create_accounts(
            created_number, is_json=True)
        # list
        retrieved_accounts_response = self.client.get(BASE_URL)
        self.assertEqual(
            retrieved_accounts_response.status_code, status.HTTP_200_OK)
        retrieved_accounts_json_list = retrieved_accounts_response.get_json()
        # test same number and the same ones
        count_tested = 0
        for retrieved_account_json in retrieved_accounts_json_list:
            for new_account_json in new_accounts_json_list:
                if retrieved_account_json["id"] == new_account_json["id"]:
                    count_tested += 1
                    self.assertTrue(
                        self.are_accounts_json_equals(
                            retrieved_account_json,
                            new_account_json
                        )
                    )
        self.assertEqual(count_tested, created_number)
        self.assertEqual(len(retrieved_accounts_json_list), created_number)

    def test_get_empty_accounts_list(self):
        """It should Get an empty list of Accounts"""
        # list
        retrieved_accounts_response = self.client.get(BASE_URL)
        self.assertEqual(
            retrieved_accounts_response.status_code, status.HTTP_200_OK)
        retrieved_accounts_json_list = retrieved_accounts_response.get_json()
        # test same number and the same ones
        self.assertEqual(len(retrieved_accounts_json_list), 0)

    # TEST METHOD NOT ALLOWED ###########################################

    def test_method_not_allowed(self):
        """It should not allow an illegal method call"""
        error_response = self.client.delete(BASE_URL)
        self.assertEqual(error_response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
    
        
    ######################################################################
    #  S E C U R I T Y   T E S T   C A S E S
    ######################################################################
            
    def test_security_headers(self):
        """It should return security headers"""
        root_url = '/'
        headers = {
            'X-Frame-Options': 'SAMEORIGIN',
            'X-Content-Type-Options': 'nosniff',
            'Content-Security-Policy': 'default-src \'self\'; object-src \'none\'',
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
        
        response = self.client.get(root_url, environ_overrides=HTTPS_ENVIRON)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key_header, val_header in headers.items():
            self.assertEqual(response.headers.get(key_header), val_header)
            
    def test_cors_security(self):
        """It should return a CORS header"""
        response = self.client.get('/', environ_overrides=HTTPS_ENVIRON)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check for the CORS header
        self.assertEqual(response.headers.get('Access-Control-Allow-Origin'), '*')