import streamlit as st 
import pandas as pd
import psycopg
from datetime import datetime as dt, timedelta

dbconn = st.secrets["DBCONN"]
st.title("CAB Pipeline Project")
st.write("This page uses data collected from the [Alpha Vantage API](https://www.alphavantage.co/) and [U.Today](https://u.today/).")

## AV DATA

def get_av_data(col):
  conn = psycopg.connect(dbconn)
  cur = conn.cursor()

  query = psycopg.sql.SQL('''
    SELECT date, {field} FROM bitcoin_api_data;
  ''').format(field=psycopg.sql.Identifier(col))
  cur.execute(query)
  
  data = cur.fetchall()
  
  conn.commit()
  cur.close()
  conn.close()
  
  return pd.DataFrame(data, columns=["date", col])

st.subheader("Bitcoin Prices Over Time")
ohlc = st.selectbox("Select OHLC value", ["open", "close", "high", "low", "volume"])

av_data = get_av_data(ohlc)
y_label = f"{ohlc.capitalize()}{" Price" if ohlc != "volume" else ""}"
st.line_chart(data=av_data, x="date", y=ohlc, y_label=y_label, x_label="Date")

## UTODAY DATA

def get_utoday_data(date):
  conn = psycopg.connect(dbconn)
  cur = conn.cursor()

  cur.execute('''
    SELECT title, author, sentiment FROM utoday_news WHERE date = %s;
  ''', (date,))
  data = cur.fetchall()
  print("DATA", data)
  utoday_data = pd.DataFrame(data, columns=["title", "author", "sentiment"])
  # utoday_data.set_index("title", inplace=True)
  # ft_data["date"] = ft_data["date"].dt.strftime('%Y-%m-%d')
  
  print("UTODAY_DATA", utoday_data)

  conn.commit()
  cur.close()
  conn.close()

  utoday_data.set_index("title", inplace=True)
  return utoday_data

def get_oldest_date():
  conn = psycopg.connect(dbconn)
  cur = conn.cursor()
  cur.execute("SELECT date FROM utoday_news ORDER BY date DESC LIMIT 1;")
  return cur.fetchall()[0][0].strftime("%Y-%m-%d")


st.subheader("Bitcoin News")
yesterday = dt.today() - timedelta(1)
selected_date = st.date_input(
  "Select a date to see news articles from that day.", 
  value=yesterday, 
  max_value=yesterday, 
  min_value=get_oldest_date()
)
print(selected_date)
utoday_data = get_utoday_data(selected_date)
# st.dataframe(data=ft_data.drop(["link", "tag", "teaser"], axis="columns"))
st.dataframe(data=utoday_data)
