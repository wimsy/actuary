from actuary_fb import *
from fb_download import *

def get_data():
  auth_vals = get_authvals_csv('auth_keys.csv')
  auth_vals = fb_oauth(auth_vals)
  friends = get_friends_fql(auth_vals)
  ffs = filter_friends(friends)
  stat_str, num = extract_age_sex_str(ffs)
  return stat_str, num

def print_results(stat_str):
  result_str = print_actuary(stat_str)
  print result_str