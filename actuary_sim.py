import numpy as np
import pandas as pd
from pandas import Series
from pandas import DataFrame
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
  
def run_years(end_year, stat_str, num_sims=100, thresholds=[0.05, 0.5, 0.95]):
  results = {}
  ages, ignore_years = parse_string(stat_str)
  start_year = datetime.datetime.today().year + 1

  for threshold in thresholds:
    results[threshold] = {(start_year - 1): 0}

  for year in range(start_year, end_year + 1):
#    print year
    probs = []
    years = year - datetime.datetime.today().year
    for age in ages:
      probs.append(deathprob(age, years))
    sims = build_sims(num_sims, len(ages))
    death_counts = count_deaths(probs, sims)
    death_rates = death_thresholds(death_counts, thresholds)
    for threshold in thresholds:
      results[threshold][year] = death_rates[threshold]

  ages = Series(ages).abs()
  ages = [ int(x) for x in ages ]
  birthyears = datetime.datetime.today().year - np.array(ages) # Being very lazy about math here
  births = np.bincount(birthyears).cumsum()[min(birthyears):]
  birthseries = Series(births, index=range(min(birthyears),len(births)+min(birthyears)))
  interimyrs = range(max(birthyears) + 1, start_year)
  birthseries = birthseries.append(Series(len(ages), index=interimyrs))
  results['births'] = (len(ages) - birthseries).to_dict()

  return results
  
def build_graph_data(results, num):
  livingdf = num - DataFrame(results)
  return livingdf
  
def graph_data(livingdf):
  livingdf.plot(figsize=(10,4))

def run_sim(stat_str, num, end_year=2100, num_sims=1000):
  results = run_years(end_year, stat_str, num_sims)
  livingdf = build_graph_data(results, num)
  graph_data(livingdf)
  return livingdf