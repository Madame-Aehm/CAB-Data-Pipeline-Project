from dotenv import load_dotenv
import os
import requests
import datetime as dt
import psycopg
import bs4


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


def scrape_for_date(date):
  response = requests.get(f"https://www.ft.com/search?q=bitcoin&dateFrom={date}&dateTo={date}&sort=relevance")
  scraped_date = []
  print(response.status_code)
  if response.status_code == 200:
    soup = bs4.BeautifulSoup(response.text, 'lxml')
    limit = 5
    search_results = soup.select("div.o-teaser__content", limit=limit)
    for result in search_results:
      scraped = [date]
      try:
        scraped.append(result.select_one("a.o-teaser__tag").get_text())
      except:
        scraped.append("")
      try:
        scraped.append(result.select_one("a.js-teaser-heading-link").get_text())
      except:
        scraped.append("")
      try:
        scraped.append(result.select_one("a.js-teaser-heading-link")["href"])
      except:
        scraped.append("")
      try:
        scraped.append(result.select_one("p.o-teaser__standfirst > a").get_text())
      except:
        scraped.append("")
      scraped_date.append(tuple(scraped))
  return scraped_date


def update_db(api_data, scraped_data):
  dbconn = os.getenv("DBCONN")
  conn = psycopg.connect(dbconn)
  cur = conn.cursor()

  cur.execute(
    '''
      INSERT INTO bitcoin_api_data(date, open, high, low, close, volume)
      VALUES (%s, %s, %s, %s, %s, %s);
    ''', 
    api_data
  )
  conn.commit()

  for item in scraped_data:
    print("adding item", item)
    cur.execute(
      '''
        INSERT INTO financial_times_scaped(date, tag, heading, link, teaser)
        VALUES (%s, %s, %s, %s, %s);
      ''', 
      item
    )
  conn.commit()

  cur.close()
  conn.close()


def main():
  load_dotenv()
  api_data = request_api()
  if api_data != None:
    scraped_data = scrape_for_date(api_data[0])
    update_db(api_data, scraped_data)
    print("update complete")
  else:
    print("no data")


main()