import os
import psycopg

def update_db(event, context):
  execute_id = event["responsePayload"]["execute_id"]
  data = event["responsePayload"]["data"]

  dbconn = os.getenv("DBCONN")
  conn = psycopg.connect(dbconn)
  cur = conn.cursor()

  if execute_id == "av_data":
    cur.execute(
      '''
        INSERT INTO bitcoin_api_data(date, open, high, low, close, volume)
        VALUES (%s, %s, %s, %s, %s, %s);
      ''', 
      data
    )

  if execute_id == "ft_data":
    for item in data:
      cur.execute(
        '''
          INSERT INTO financial_times_scaped(date, tag, heading, link, teaser, sentiment)
          VALUES (%s, %s, %s, %s, %s, %s);
        ''', 
        item
      )

  conn.commit()
  cur.close()
  conn.close()