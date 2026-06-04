import pandas as pd
import sqlite3
import matplotlib.pyplot as plt


def main():
    None
    conn = sqlite3.connect("data/ETF_Project.db")

    try:
        df = pd.read_sql("SELECT * FROM etf_price", conn)
        print(df.columns)
    finally:
        conn.close()

    df["trade_date"] = pd.to_datetime(df["trade_date"])
    df = df.sort_values(["etf_code", "trade_date"]).copy()

    df["daily_return"] = df.groupby("etf_code")["close_price"].pct_change()
    df["daily_return"] = df["daily_return"].fillna(0)
    df["cumulative_return"] = (1 + df["daily_return"]).groupby(df["etf_code"]).cumprod()

    print(df.head())

    plt.figure(figsize=(12, 6))
    for etf in df["etf_code"].unique():
        temp = df[df["etf_code"] == etf]
        plt.plot(temp["trade_date"], temp["cumulative_return"], label=etf)

    plt.title("ETF Cumulative Return")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Return")
    plt.legend()
    plt.tight_layout()
    df.to_csv("dashboard/etf_return_analysis.csv",index=False)
    plt.show()

if __name__=="__main__":
    main()

