import sqlite3
import pandas as pd

conn=sqlite3.connect("data/ETF_Project.db")

query=""" SELECT * FROM etf_0050 """

df=pd.read_sql(query,conn)
conn.close()

df["trade_date"]=pd.to_datetime(df["trade_date"])

df["daily_return"]=(df["close_price"].pct_change())

df["ma5"]=(df["close_price"].rolling(5).mean())

df["ma20"]=(df["close_price"].rolling(20).mean())

df["volatility"]=(df["daily_return"].rolling(20).std())

df["target"]=(df["daily_return"].shift(-1))

df=df.dropna()

df.to_csv("dashboard/ml_dataset.csv",index=False)
print(df.head())
print("ml dataset 建立成功!")