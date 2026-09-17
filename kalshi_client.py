import requests
import json
import datetime

# return a dictionary with location names and their yes, no probabilities 

markets_url = f"https://external-api.kalshi.com/trade-api/v2/markets?series_ticker=KXRAIN&status=open"

def implied_probability(yes_bid, no_bid):
    yes_ask = 1 - no_bid 
    mid_point = (yes_ask+yes_bid)/2
    return round(mid_point*100,1)

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

def check_contract_resolution(ticker: str):
    """
    Fetches a single market by its full ticker (e.g. 'KXRAIN-26SEP01-TTN')
    and reports whether it has settled.

    Returns a dict:
        resolved (bool)
        outcome (int or None): 1 if 'yes' won, 0 if 'no' won, None if unresolved
        settled_price (float or None)
        status (str or None): raw Kalshi status, for debugging
    """
    market_url = f"https://external-api.kalshi.com/trade-api/v2/markets/{ticker}"

    try:
        resp = requests.get(market_url)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching market {ticker}: {e}")
        return {"resolved": False, "outcome": None, "settled_price": None, "status": None}

    try:
        market = resp.json()["market"]
    except (KeyError, ValueError) as e:
        print(f"Unexpected response shape for {ticker}: {e}")
        return {"resolved": False, "outcome": None, "settled_price": None, "status": None}

    status = market.get("status")
    if status != "settled":
        return {"resolved": False, "outcome": None, "settled_price": None, "status": status}

    result = market.get("result")  # "yes" or "no"
    if result not in ("yes", "no"):
        print(f"Market {ticker} marked settled but result is invalid: {result}")
        return {"resolved": False, "outcome": None, "settled_price": None, "status": status}

    return {
        "resolved": True,
        "outcome": 1 if result == "yes" else 0,
        "settled_price": market.get("settlement_value"),
        "status": status,
    }

def main() -> None:
    return None


if __name__ == "__main__":
    main()