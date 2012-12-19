import numpy as np
import pandas as pd
from pandas import Series
import math
from actuary_fb import *
import datetime

def build_sims(num, length):
  sims = []
  for sim in range(0,num):
    sims.append(np.random.rand(length))
  return sims
  
def count_deaths(probs, sims):
  death_counts = []
  for sim in sims:
    death_counts.append(np.sum(sim < probs))
  return death_counts
  
def death_thresholds(death_counts, thresholds):
  death_rates = {}
  outcomes = np.bincount(death_counts)
  cumul_outcomes = []
  for idx, val in enumerate(outcomes):
    cumul_outcomes.append(np.sum(outcomes[idx:]))
  for threshold in thresholds:
    cutoff = np.ceil(threshold * len(death_counts)) - 1
    death_rates[threshold] = max(Series(np.where(cumul_outcomes > cutoff)[0]))
  return death_rates
  
def run_years(start_year, end_year, stat_str, num_sims=100, thresholds=[0.05, 0.5, 0.95]):
  results = {}
  ages, ignore_years = parse_string(stat_str)
#  print ages
  start_year = max(start_year,datetime.datetime.today().year + 1)
#  print start_year
  for year in range(start_year, end_year + 1):
    print year
    probs = []
    years = year - datetime.datetime.today().year
    for age in ages:
      probs.append(deathprob(age, years))
    sims = build_sims(num_sims, len(ages))
    death_counts = count_deaths(probs, sims)
    results[year] = death_thresholds(death_counts, thresholds)
  return results