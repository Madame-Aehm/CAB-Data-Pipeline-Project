import os
import psycopg

def update_db(event, context):
  id = event["responsePayload"]["id"]
  data = event["responsePayload"]["data"]
  dbconn = os.getenv("DBCONN")
  conn = psycopg.connect(dbconn)
  cur = conn.cursor()

  if id == "av_data":
    cur.execute(
      '''
        INSERT INTO bitcoin_api_data(date, open, high, low, close, volume)
        VALUES (%s, %s, %s, %s, %s, %s);
      ''', 
      data
    )
    conn.commit()
    print("av data successfully added to db")

  if id == "ft_data":
    for item in data:
      cur.execute(
        '''
          INSERT INTO financial_times_scaped(date, tag, heading, link, teaser)
          VALUES (%s, %s, %s, %s, %s);
        ''', 
        item
      )
    conn.commit()
    print("ft data successfully added to db")

  cur.close()
  conn.close()