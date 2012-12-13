import csv
import webbrowser
import json

from temboo.core.session import *
from temboo.Library.Facebook.OAuth import *
from temboo.Library.Facebook.Reading import *


def get_authvals_csv(authf):
	vals = {}	
	with open(authf, 'rU') as f:
		f_iter = csv.DictReader(f)
		vals = f_iter.next()
	return vals

def fb_oauth():
  auth_vals = get_authvals_csv('auth_keys.csv')

  # Instantiate the choreography, using a previously instantiated TembooSession object, eg:
  session = TembooSession(auth_vals['temboo_account_name'], \
    auth_vals['temboo_app_key_name'], \
    auth_vals['temboo_app_key'])
  initializeOAuthChoreo = InitializeOAuth(session)

  # Get an InputSet object for the choreo
  initializeOAuthInputs = initializeOAuthChoreo.new_input_set()

  # Set inputs
  initializeOAuthInputs.set_AppKeyName(auth_vals['temboo_app_key_name'])
  initializeOAuthInputs.set_AccountName(auth_vals['temboo_account_name'])
  initializeOAuthInputs.set_AppID(auth_vals['app_id'])
  initializeOAuthInputs.set_AppKeyValue(auth_vals['temboo_app_key'])

  # Execute choreo
  initializeOAuthResults = initializeOAuthChoreo.execute_with_results(initializeOAuthInputs)

  # Send user for authentication
  webbrowser.open(initializeOAuthResults.get_AuthorizationURL())

  # Finalize authorization with FinalizeOAuth
  # Instantiate the choreography, using a previously instantiated TembooSession object, eg:
  finalizeOAuthChoreo = FinalizeOAuth(session)

  # Get an InputSet object for the choreo
  finalizeOAuthInputs = finalizeOAuthChoreo.new_input_set()

  # Set credential to use for execution
  finalizeOAuthInputs.set_credential(auth_vals['temboo_app_key_name'])

  # Set inputs
  finalizeOAuthInputs.set_CallbackID(initializeOAuthResults.get_CallbackID())

  # Execute choreo
  finalizeOAuthResults = finalizeOAuthChoreo.execute_with_results(finalizeOAuthInputs)
  
  auth_vals['access_token'] = finalizeOAuthResults.get_AccessToken()
  auth_vals['token_expires'] = finalizeOAuthResults.get_Expires()
  
  return auth_vals

def get_friends(auth_vals):
  # Instantiate the choreography, using a previously instantiated TembooSession object
  session = TembooSession(auth_vals['temboo_account_name'], \
    auth_vals['temboo_app_key_name'], \
    auth_vals['temboo_app_key'])
  friendsChoreo = Friends(session)

  # Get an InputSet object for the choreo
  friendsInputs = friendsChoreo.new_input_set()

  # Set inputs
  friendsInputs.set_AccessToken(auth_vals['access_token'])
  friendsInputs.set_Fields("id,name,birthday")
#  friendsInputs.set_Limit(100)

  # Execute choreo
  friendsResults = friendsChoreo.execute_with_results(friendsInputs)

  # Parse JSON into a list of friends
  friends_list_json = friendsResults.get_Response()
  friends_list = json.loads(friends_list_json)['data']
  friend_count = len(friends_list)

  # Navigate through pages
  while friendsResults.get_HasNext() == 'true':
    friendsInputs.set_Offset(friend_count)
    friendsResults = friendsChoreo.execute_with_results(friendsInputs)
    friends_list = friends_list + json.loads(friendsResults.get_Response())['data']
    print friend_count
    friend_count = len(friends_list)
    
  return friends_list