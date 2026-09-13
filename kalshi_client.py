import requests
import json
import datetime

# return a dictionary with location names and their yes, no probabilities 



markets_url = f"https://external-api.kalshi.com/trade-api/v2/markets?series_ticker=KXRAIN&status=open"
def implied_probability(yes_bid, no_bid):
    yes_ask = 1 - no_bid 
    mid_point = (yes_ask+yes_bid)/2
    return round(mid_point*100,1)
import datetime

def kalshi_data(target_date: datetime.date):
    markets_response = requests.get(markets_url)
    markets_data = markets_response.json()
    areas_predictions = {}
    for market in markets_data["markets"]:
        ticker_parts = market['ticker'].split('-')   # ['KXRAIN', '26SEP01', 'TTN']
        date_code = ticker_parts[1]                  # '26SEP01'
        city = ticker_parts[-1]
        market_date = datetime.datetime.strptime(date_code, "%y%b%d").date()
        if market_date != target_date:
            continue  # skip contracts for other days
        yes_bid = float(market.get("yes_bid_dollars"))
        no_bid = float(market.get("no_bid_dollars"))
        areas_predictions[city] = implied_probability(yes_bid, no_bid)
    return areas_predictions

def main() -> None:
    return None


if __name__ == "__main__":
    main()
