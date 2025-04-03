from datetime import datetime as dt
import requests
import bs4

def get_utoday_data(event, context):
    today = dt.today().strftime('%b %#d, %Y')
    response = requests.get("https://u.today/search/node?keys=bitcoin")
    document = bs4.BeautifulSoup(response.text, "html.parser")
    news_items = document.select(".news__item")

    add_to_db = []
    for item in news_items:
        try: 
            date = item.select_one("div.humble").get_text().split(" - ")[0]
            if date == today:
                data = []
                data.append(item.select_one("div.news__item-title").get_text()) # title
                data.append(item.select_one("a.humble.humble--author").get_text().split("\n")[0]) # author
                data.append(date) # date
                data.append(item.select_one("a.news__item-body")["href"]) # link
                add_to_db.append(data)
        except: print("value missing")
    
    return add_to_db