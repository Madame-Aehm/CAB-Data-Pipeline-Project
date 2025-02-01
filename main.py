from dotenv import load_dotenv
import os
import requests
from datetime import datetime as dt, timedelta
import psycopg
import bs4


def get_av_data(date):
  api_key = os.getenv("AV_API_KEY")
  response = requests.get(f"https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=BTC&market=EUR&apikey={api_key}")
  if response.status_code == 200:
    data = response.json()
    values = [date]
    for value in data["Time Series (Digital Currency Daily)"][date].values():
      values.append(float(value))
    return tuple(values)


def get_ft_data(date):
  response = requests.get(f"https://www.ft.com/search?q=bitcoin&dateFrom={date}&dateTo={date}&sort=relevance")
  scraped_date = []
  print(response.status_code)
  if response.status_code == 200:
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
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
      scraped.append("sentiment")
      scraped_date.append(tuple(scraped))
  return scraped_date

def get_sentiment(data):
  hf_api_key = os.getenv("HF_API_KEY")
  url = "https://api-inference.huggingface.co/models/mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"

  payload = { "inputs": [post[2] for post in data] }
  headers = { "Authorization": f"Bearer {hf_api_key}" }
  response = requests.post(url, headers=headers, json=payload)
  print(response)

  if response.status_code == 503:
    headers["x-wait-for-model"] = "true"
    response = requests.post(url, headers=headers, json=payload)
  print(response)

  if response.status_code == 200:
    sentiment_results = response.json()
    if len(sentiment_results) == len(data):
      for i in range(0, len(data)):
        item_list = list(data[i])
        item_list[-1] = sentiment_results[i][0]["label"]
        data[i] = tuple(item_list)
  return data


def update_db(av_data, ft_data):
  dbconn = os.getenv("DBCONN")
  conn = psycopg.connect(dbconn)
  cur = conn.cursor()

  if av_data != None:
    cur.execute(
      '''
        INSERT INTO bitcoin_api_data(date, open, high, low, close, volume)
        VALUES (%s, %s, %s, %s, %s, %s);
      ''', 
      av_data
    )
    print("av data successfully added to db")

  for item in ft_data:
    cur.execute(
      '''
        INSERT INTO financial_times_scaped(date, tag, heading, link, teaser, sentiment)
        VALUES (%s, %s, %s, %s, %s, %s);
      ''', 
      item
    )
  print("ft data successfully added to db")

  conn.commit()
  cur.close()
  conn.close()


def main():
  load_dotenv()
  today = dt.today() - timedelta(1)
  today = today.strftime('%Y-%m-%d')
  print("today is", today)
  # av_data = get_av_data(today)
  ft_data = get_ft_data(today)
  ft_data = get_sentiment(ft_data)
  # print("AV DATA", av_data)
  print("FT DATA", ft_data)
  update_db(av_data=None, ft_data=ft_data)
  print("end")


main()