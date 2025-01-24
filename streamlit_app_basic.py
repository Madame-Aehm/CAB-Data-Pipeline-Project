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
    SELECT * FROM financial_times_scaped;
  ''')
  data = cur.fetchall()
  ft_data = pd.DataFrame(data, columns=["tag", "link", "heading", "teaser", "date"])
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

st.subheader("Bitcoin News")
yesterday = (dt.today() - timedelta(days=1)).strftime('%Y-%m-%d')
st.table(ft_data[ft_data["date"] == yesterday].drop(["link", "tag"], axis="columns"))
