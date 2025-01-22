import datetime as dt
import os
import requests


def get_av_data():
  today = dt.datetime.today().strftime('%Y-%m-%d')
  api_key = os.getenv("AV_API_KEY")
  response = requests.get(f"https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=BTC&market=EUR&apikey={api_key}")
  if response.status_code == 200:
    data = response.json()
    values = [today]
    for value in data["Time Series (Digital Currency Daily)"][today].values():
      values.append(float(value))
    return tuple(values)