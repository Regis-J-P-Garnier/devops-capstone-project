"""
Account Service

This microservice handles the lifecycle of Accounts
"""
# pylint: disable=unused-import
from flask import jsonify, request, make_response, abort, url_for   # noqa; F401
from service.models import Account
from service.common import status  # HTTP Status Codes
from . import app  # Import Flask application


############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return jsonify(dict(status="OK")), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Account REST API Service",
            version="1.0",
            # paths=url_for("list_accounts", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
# CREATE A NEW ACCOUNT
######################################################################
@app.route("/accounts", methods=["POST"])
def create_accounts():
    """
    Creates an Account
    This endpoint will create an Account based the data in the body that is posted
    """
    app.logger.info("Request to create an Account")
    check_content_type("application/json")
    account = Account()
    account.deserialize(request.get_json())
    account.create()
    message = account.serialize()
    # Uncomment once get_accounts has been implemented
    # location_url = url_for("get_accounts", account_id=account.id, _external=True)
    location_url = "/"  # Remove once get_accounts has been implemented
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )

######################################################################
# READ AN ACCOUNT
######################################################################
@app.route("/accounts/<int:account_id>", methods=["GET"])
def get_accounts(account_id):
    """
    Reads an Account
    This endpoint will read an Account based the account_id that is requested
    """
    app.logger.info("Request to read an Account(id == %s).", account_id)
    account = Account.find(account_id)
    if account is None:
        abort(status.HTTP_404_NOT_FOUND, f"Account(id == [{account_id}]) not found.")
    return jsonify(account.serialize()), status.HTTP_200_OK


######################################################################
# DELETE AN ACCOUNT
######################################################################
@app.route("/accounts/<int:account_id>", methods=["DELETE"])
def delete_accounts(account_id):
    """
    Delete an Account
    This endpoint will delete an Account based on the account_id that is requested
    """
    app.logger.info("Request to delete an Account(id == %s)", account_id)
    account = Account.find(account_id)
    if account is None:
        app.logger.warning(f"Account(id == [{account_id}]) not found.")
        return jsonify(""), status.HTTP_204_NO_CONTENT
    account.delete()
    app.logger.info(f"Account(id == [{account_id}]) deleted.")
    return jsonify(""), status.HTTP_204_NO_CONTENT

######################################################################
# LIST ALL ACCOUNTS
######################################################################

# ... place you code here to LIST accounts ...
"""
List

    List should use the Account.all() method to return all of the accounts as a list of dict and return the HTTP_200_OK return code.
    It should never send back a 404_NOT_FOUND. If you do not find any accounts, send back an empty list ([]) and 200_OK.
"""


######################################################################
# UPDATE AN EXISTING ACCOUNT
######################################################################

# ... place you code here to UPDATE an account ...
"""
Update

    Update should accept an account_id and use Account.find() to find the account.
    It should return an HTTP_404_NOT_FOUND if the account cannot be found.
    If the account is found, it should call the deserialize() method on the account instance passing in request.get_json() and call the update() method to update the account in the database.
    It should call the serialize() method on the account instance and return a Python dictionary with a return code of HTTP_200_OK.
"""

######################################################################
# DELETE AN ACCOUNT
######################################################################

# ... place you code here to DELETE an account ...
"""
Delete

    Delete should accept an account_id and use Account.find() to find the account.
    If the account is not found, it should do nothing.
    If the account is found, it should call the delete() method on the account instance to delete it from the database.
    It should return an empty body "" with a return code of HTTP_204_NO_CONTENT.

Use these hints to write your test cases first, and then write the code to make the test cases pass.
"""

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )
