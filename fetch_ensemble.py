import requests
import json
#I want easy access to change parameters, so a dictionary with them and an f"String" URL 
#Want to automatically create lists of the time and rain probabilities, and return them
#just use the precipitation_probability_max for now, going to do the ensemble method anyways 
#Easy way to change paramters, and a function that returns precipitation_probability_max for that ensemble 

params_standard = {
    "latitude": 38.98,
    "longitude": -77.09,
    "hourly": ["temperature_2m", "precipitation_probability"],
    "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_probability_max"],
    "temperature_unit": "fahrenheit",
    "timezone": "auto",
    "forecast_days": 7,
}
params_ensemble = {
    "latitude": 38.98,
    "longitude": -77.09,
    "daily": "precipitation_sum",
    "models": "gfs_seamless",  # or icon_seamless, ecmwf_ifs025, gem_seamless, etc.
    "temperature_unit": "fahrenheit",
    "precipitation_unit": "inch",
    "timezone": "auto",
    "forecast_days": 1,
}
base_url_standard = "https://api.open-meteo.com/v1/forecast"
base_url_ensemble = "https://ensemble-api.open-meteo.com/v1/ensemble"

def get_daily_precip_probability(base_url,params):
  response = requests.get(base_url,params=params)
  data = response.json()
  precipitation_probability_max = data["daily"]["precipitation_probability_max"]
  return precipitation_probability_max[0]#returns todays probability of rain

def get_ensemble_String(lat,long):
  params = params_ensemble.copy()  
  params_ensemble["latitude"] = lat
  params_ensemble["longitude"] = long
  response = requests.get(base_url_ensemble,params_ensemble)
  data = response.json()
  dates = data["daily"]["time"]
  member_keys = [key for key in data["daily"] if key.startswith("precipitation_sum_member")]
  ensemble_prediction = f""
  for i, dates in enumerate(dates):
     values = [data["daily"][mk][i] for mk in member_keys]#gives the values of the day in the iteration
     n_members = len(values)
     n_rainy_members=(sum(1 for v in values if v is not None and v>.01))#counts rainy members
     prob_precip = 100*n_rainy_members/n_members
     ensemble_prediction += f"{dates}: {prob_precip:.0f}% of {n_members} members show precipitation \n"

  return ensemble_prediction


def get_ensemble_data(lat, long):
  params = params_ensemble.copy()
  params["latitude"] = lat
  params["longitude"] = long
  response = requests.get(base_url_ensemble, params)
  data = response.json()

  dates = data["daily"]["time"]
  member_keys = [key for key in data["daily"] if key.startswith("precipitation_sum_member")]

  probabilities = []
  for i, date in enumerate(dates):#allows capability to predict more days into the future
      values = [data["daily"][mk][i] for mk in member_keys]  # values for this day across all members
      n_members = len(values)
      n_rainy_members = sum(1 for v in values if v is not None and v > 0.01)

      prob_precip = 100 * n_rainy_members / n_members
      probabilities.append([round(prob_precip),n_members])

  return probabilities#list of predictions for each day 

def main() -> None:
  print(get_ensemble_data(38.98,-77.09,))#test case of Bethesda Maryland
  return None




if __name__ == "__main__":
    main()

