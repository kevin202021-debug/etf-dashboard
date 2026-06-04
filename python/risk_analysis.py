import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

RISK_FREE_RATE = 0.01
TRADING_DAYS = 252


def load_data():
    conn = sqlite3.connect("data/ETF_Project.db")
    try:

        df = pd.read_sql("SELECT * FROM etf_price",conn)

    finally:

        conn.close()

    return df

def calculate_return(df):

    df["trade_date"] = pd.to_datetime(df["trade_date"])

    df = df.sort_values(["etf_code", "trade_date"])

    df["daily_return"] = (df.groupby("etf_code")["close_price"].pct_change())

    df["daily_return"] = (df["daily_return"].fillna(0))

    return df

def calculate_risk_metrics(df):

    result = []

    etf_list = df["etf_code"].unique()

    for etf in etf_list:
        temp = df[df["etf_code"] == etf]
        returns = temp["daily_return"]

        annual_return = (returns.mean()* TRADING_DAYS)

        annual_volatility = (returns.std()* np.sqrt(TRADING_DAYS))

        sharpe_ratio = (annual_return- RISK_FREE_RATE) / annual_volatility

        cumulative_return = ((1 + returns).cumprod().iloc[-1]- 1)

        cumulative_curve = (1 + returns).cumprod()

        running_max = (cumulative_curve.cummax())

        drawdown = (cumulative_curve- running_max) / running_max

        max_drawdown = (drawdown.min())

        result.append({"ETF": etf,"Annual Return":annual_return,"Annual Volatility":annual_volatility,"Sharpe Ratio":sharpe_ratio,"Cumulative Return":cumulative_return,"Max Drawdown":max_drawdown})

    risk_df = pd.DataFrame(result)

    return risk_df

def plot_risk_return(risk_df):

    plt.figure(figsize=(10, 6))

    scatter = plt.scatter(risk_df["Annual Volatility"],risk_df["Annual Return"],c=risk_df["Sharpe Ratio"],s=200)

    plt.colorbar(scatter,label="Sharpe Ratio")

    for i in range(len(risk_df)):
        plt.text(risk_df["Annual Volatility"].iloc[i],risk_df["Annual Return"].iloc[i],risk_df["ETF"].iloc[i])

    plt.xlabel("Annual Volatility")
    plt.ylabel("Annual Return")
    plt.title("ETF Risk Return Analysis")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def export_csv(risk_df):
    risk_df.to_csv("dashboard/risk_analysis.csv",index=False)
    print("risk_analysis.csv 匯出成功")

def main():
    print("開始進行 Risk Analysis...")
    df = load_data()
    df = calculate_return(df)
    risk_df = calculate_risk_metrics(df)
    print("\nETF Risk Metrics\n")
    print(risk_df)
    export_csv(risk_df)
    plot_risk_return(risk_df)
    print("\nRisk Analysis 完成!")

if __name__ == "__main__":
    main()
