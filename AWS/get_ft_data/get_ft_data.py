import requests
from datetime import datetime as dt
import bs4

def get_ft_data():
  today = dt.today().strftime('%Y-%m-%d')
  print(today)
  response = requests.get(f"https://www.ft.com/search?q=bitcoin&dateFrom={today}&dateTo={today}&sort=relevance")
  scraped_data = []
  print(response.status_code)
  if response.status_code == 200:
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    limit = 5
    search_results = soup.select("div.o-teaser__content", limit=limit)
    for result in search_results:
      scraped = [today]
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
      scraped_data.append(scraped)
  return {
    "execute_id": "ft_data",
    "data": scraped_data
  }
  
data = get_ft_data()
print(data)
