import json
import datetime
import fetch_ensemble
import kalshi_client
import logger

CITY_COORDS = {
    "TTN":  {"name": "Trenton, NJ (TTN)",         "lat": 40.28, "lon": -74.81},
    "SFO":  {"name": "San Francisco, CA (SFO)",   "lat": 37.62, "lon": -122.38},
    "SEA":  {"name": "Seattle, WA (SEA)",         "lat": 47.45, "lon": -122.31},
    "SATX": {"name": "San Antonio, TX (SAT)",     "lat": 29.53, "lon": -98.47},
    "PHX":  {"name": "Phoenix, AZ (PHX)",         "lat": 33.43, "lon": -112.01},
    "PHIL": {"name": "Philadelphia, PA (PHL)",    "lat": 39.87326, "lon": -75.22681},
    "OKC":  {"name": "Oklahoma City, OK (OKC)",   "lat": 35.39, "lon": -97.60},
    "NYC":  {"name": "New York, NY (Central Park)", "lat": 40.77898, "lon": -73.96925},
    "NOLA": {"name": "New Orleans, LA (MSY)",     "lat": 29.99, "lon": -90.26},
    "MIN":  {"name": "Minneapolis, MN (MSP)",     "lat": 44.88, "lon": -93.22},
    "MIA":  {"name": "Miami, FL (MIA)",           "lat": 25.78805, "lon": -80.31694},
    "LV":   {"name": "Las Vegas, NV (LAS)",       "lat": 36.08, "lon": -115.15},
    "LAX":  {"name": "Los Angeles, CA (LAX)",     "lat": 33.94, "lon": -118.41},
    "HOU":  {"name": "Houston, TX (KHOU - Hobby)", "lat": 29.64586, "lon": -95.28212},
    "EWR":  {"name": "Newark, NJ (EWR)",          "lat": 40.69, "lon": -74.17},
    "DEN":  {"name": "Denver, CO (DEN)",          "lat": 39.84657, "lon": -104.65623},
    "DC":   {"name": "Washington, DC (DCA)",      "lat": 38.85, "lon": -77.04},
    "DAL":  {"name": "Dallas, TX (DFW)",          "lat": 32.90, "lon": -97.04},
    "CHI":  {"name": "Chicago, IL (Midway)",      "lat": 41.78412, "lon": -87.75514},
    "BOS":  {"name": "Boston, MA (BOS)",          "lat": 42.36, "lon": -71.01},
    "AUS":  {"name": "Austin, TX (AUS)",          "lat": 30.18311, "lon": -97.67989},
    "ATL":  {"name": "Atlanta, GA (ATL)",         "lat": 33.64, "lon": -84.43},
}



def main() -> None:
    kalshi_data = kalshi_client.kalshi_data(datetime.date.today())
    records = []

    for key, city in CITY_COORDS.items():
        lat = city["lat"]
        lon = city["lon"]
        kalshi_value = kalshi_data[key]
        ensemble_value = fetch_ensemble.get_ensemble_data(lat, lon)

        record ={
            "loc":[lat, lon],
            "name":city["name"],
            "city":city["name"],
            "ensemble_percent":ensemble_value[0][0],
            "number_ensemble_members":ensemble_value[0][1],
            "event":None, 
            "kalshi_odds":kalshi_value,
            "area_code":key
        }

        now = datetime.datetime.now().time()
        MORNING_CUTOFF = datetime.time(15, 0)   # artbitrary before 8am
        NIGHT_START = datetime.time(22, 0)     # arbitrary 12, I did this because I live on eascoast and am awake around these times so I can check, probably better to do it based off when markets open and close

        if now < MORNING_CUTOFF:
            logger.log_morning_prediction(
                record["city"],
                record["ensemble_percent"],
                record["kalshi_odds"], 
                record["ensemble_percent"] - record["kalshi_odds"]#edge
            )
        elif now > NIGHT_START:
            ticker = f"KXRAIN-{datetime.datetime.now().strftime('%y%b%d').upper()}-{record['area_code']}"
            resolution = kalshi_client.check_contract_resolution(ticker)
            if resolution["resolved"]:
                logger.log_night_result(
                    record["city"],
                    actual_outcome=resolution["outcome"],
                    settledprice=resolution["settled_price"]
                )
            else:
                print(f"{record['city']} contract not yet resolved — skipping")


    print("Done!")






if __name__ == "__main__":
    main()
