import streamlit as st 
import pandas as pd
import psycopg
# from dotenv import load_dotenv
# import os
from datetime import datetime as dt, timedelta

# load_dotenv()

def get_data():
  # dbconn = os.getenv("DBCONN")
  dbconn = st.secrets["DBCONN"]
  conn = psycopg.connect(dbconn)
  cur = conn.cursor()

  cur.execute('''
    SELECT * FROM bitcoin_api_data;
  ''')
  data = cur.fetchall()
  av_data = pd.DataFrame(data, columns=["date", "open", "high", "low", "close", "volume"])

  cur.execute('''
    SELECT * FROM financial_times_scaped WHERE date > LOCALTIMESTAMP - INTERVAL '7 days' ORDER BY date DESC;
  ''')
  data = cur.fetchall()
  ft_data = pd.DataFrame(data, columns=["tag", "link", "heading", "teaser", "date", "sentiment"])
  ft_data.set_index("heading", inplace=True)
  ft_data["date"] = ft_data["date"].dt.strftime('%Y-%m-%d')


  conn.commit()
  cur.close()
  conn.close()

  return (av_data, ft_data)

av_data, ft_data = get_data()


st.title("CAB Pipeline Project")
st.write("This page uses data collected from the [Alpha Vantage API](https://www.alphavantage.co/) and [Financial Times](https://www.ft.com/).")

st.subheader("Bitcoin Closing Prices Over Time")
st.line_chart(data=av_data, x="date", y="close", y_label="Closing Price", x_label="Date")

st.subheader("This Week's Bitcoin News")
st.dataframe(data=ft_data.drop(["link", "tag", "teaser"], axis="columns"))
