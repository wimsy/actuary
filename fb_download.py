import csv
import webbrowser
import json
import facebook
from datetime import date
import datetime

from temboo.core.session import *
from temboo.Library.Facebook.OAuth import *
from temboo.Library.Facebook.Reading import *


def get_authvals_csv(authf):
	vals = {}	
	with open(authf, 'rU') as f:
		f_iter = csv.DictReader(f)
		vals = f_iter.next()
	return vals

def write_authvals_csv(authd, authf):
	f = open(authf, 'wb')
	fieldnames = tuple(authd.iterkeys())
	headers = dict((n,n) for n in fieldnames)
	f_iter = csv.DictWriter(f, fieldnames=fieldnames)
	f_iter.writerow(headers)
	f_iter.writerow(authd)
	f.close

def fb_oauth(auth_vals):
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
  
  write_authvals_csv(auth_vals,'auth_keys.csv')
  return auth_vals

def get_friends_temboo(auth_vals):
  """Don't use this. Use get_friends_fql instead."""
  
  # Instantiate the choreography, using a previously instantiated TembooSession object
  session = TembooSession(auth_vals['temboo_account_name'], \
    auth_vals['temboo_app_key_name'], \
    auth_vals['temboo_app_key'])
  friendsChoreo = Friends(session)

  # Get an InputSet object for the choreo
  friendsInputs = friendsChoreo.new_input_set()

  # Set inputs
  friendsInputs.set_AccessToken(auth_vals['access_token'])
  friendsInputs.set_Fields("id,birthday")
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
  
def extract_ids(friends_list):
  ids = []
  for friend in friends_list:
    ids = ids + [friend['id']]
  return ids
  
def get_friends_fql(auth_vals):
  graph = facebook.GraphAPI(auth_vals['access_token'])
  friends_data = \
    graph.fql("SELECT birthday_date,sex FROM user WHERE uid in (SELECT uid2 FROM friend WHERE uid1 = me())")
  return friends_data
  
def calculate_age(born):
  today = date.today()
  try: # raised when birth date is February 29 and the current year is not a leap year
      birthday = born.replace(year=today.year)
  except ValueError:
      birthday = born.replace(year=today.year, day=born.day-1)
  if birthday > today:
      return today.year - born.year - 1
  else:
      return today.year - born.year
        
def parse_birthdate(bday_str):
  return datetime.datetime.strptime(bday_str, '%m/%d/%Y').date()
  
def filter_friends(friend_list):
  for friend in friend_list:
    if type(friend['birthday_date']) == type('str'):
      if len(friend['birthday_date']) > 5:
        born = parse_birthdate(friend['birthday_date'])
        friend['age'] = calculate_age(born)
  filtered_list = [friend for friend in friend_list if 'age' in friend and friend['sex'] != ""]
  for friend in filtered_list:
    friend['age_sex'] = str(friend['age'])+friend['sex'][0]
  return filtered_list
  
def extract_age_sex_str(filtered_friend_list):
  age_sex = []
  for friend in filtered_friend_list:
    age_sex = age_sex + [friend['age_sex']]
  age_sex_str = " ".join(age_sex)
  return age_sex_str, len(age_sex)