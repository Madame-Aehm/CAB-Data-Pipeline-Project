import streamlit as st 
import pandas as pd
import psycopg
from dotenv import load_dotenv
import os

load_dotenv()

def get_data():
  dbconn = os.getenv("DBCONN")
  conn = psycopg.connect(dbconn)
  cur = conn.cursor()

  cur.execute('''
    SELECT * FROM bitcoin_api_data;
  ''')
  data = cur.fetchall()
  av_data = pd.DataFrame(data, columns=["date", "open", "high", "low", "close", "volume"])

  # cur.execute('''
  #   SELECT * FROM financial_times_scaped LIMIT 5;
  # ''')
  # data = cur.fetchall()
  # dataframe = pd.DataFrame(data, columns=["tag", "link", "heading", "teaser", "date"])
  # print(dataframe)
  

  conn.commit()
  cur.close()
  conn.close()

  return av_data

av_data = get_data()
# print(av_data)

st.line_chart(data=av_data, x="date", y="close", y_label="Closing Price", x_label="Date")