from pytrends.request import TrendReq
import pandas as pd
import time

pytrends = TrendReq(hl='zh-TW',tz=480,retries=3,backoff_factor=0.5)

keywords = ["AI"]

time.sleep(10)

pytrends.build_payload(keywords,timeframe='2020-01-01 2026-05-26',geo="TW")

df = pytrends.interest_over_time()

if "isPartial" in df.columns:
    df = df.drop(columns=["isPartial"])

df.to_csv("dashboard/google_trends_ai.csv")

print(df.head())
print("Google Trends 匯出成功")