from dotenv import load_dotenv
import os
import requests
import datetime as dt
import psycopg


def request_api():
  api_key = os.getenv("WEATHER_APIKEY")
  response = requests.get(f"https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=BTC&market=EUR&apikey={api_key}")
  if response.status_code == 200:
    data = response.json()
    today = dt.datetime.today().strftime('%Y-%m-%d')
    # print(data["Time Series (Digital Currency Daily)"][today])
    values = [today]
    for value in data["Time Series (Digital Currency Daily)"][today].values():
      values.append(float(value))
    return tuple(values)


def update_api_table(data):
  dbconn = os.getenv("DBCONN")
  conn = psycopg.connect(dbconn)
  cur = conn.cursor()
  cur.execute(
    '''
      INSERT INTO bitcoin_api_data(date, open, high, low, close, volume)
      VALUES (%s, %s, %s, %s, %s, %s);
    ''', 
    data
  )
  conn.commit()
  cur.close()
  conn.close()
  print("update complete")


def main():
  load_dotenv()
  data = request_api()
  if data != None:
    update_api_table(data)


main()