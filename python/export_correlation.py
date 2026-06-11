import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from matplotlib import font_manager

#設定中文字型
font_list = ["/System/Library/Fonts/PingFang.ttc","/System/Library/Fonts/STHeiti Light.ttc","/Library/Fonts/Arial Unicode.ttf"]

for font_path in font_list:
    try:
        font_prop = font_manager.FontProperties(fname=font_path)
        matplotlib.rcParams["font.family"] = (font_prop.get_name())

        break

    except:

        continue

#避免負號變方框
matplotlib.rcParams["axes.unicode_minus"] = False

#基本參數
trading_days = 252
risk_free_rate = 0.01

#ETF資料表
etf_tables = [
    "etf_0050",
    "etf_006208",
    "etf_0056",
    "etf_00679b",
    "etf_00687b",
    "etf_00631l"
]


#讀取ETF資料
def load_all_etf_data():
    conn = sqlite3.connect("data/ETF_Project.db")
    all_data = []
    try:

        for table in etf_tables:

            query = f"""
            SELECT
                trade_date,
                close_price
            FROM {table}
            """

            df = pd.read_sql(query,conn)

            df["trade_date"] = pd.to_datetime(df["trade_date"])

            df = df.rename(columns={"close_price": table})
            all_data.append(df)

    finally:

        conn.close()

    merged_df = all_data[0]

    for df in all_data[1:]:
        merged_df = pd.merge(merged_df,df,on="trade_date",how="inner")
    return merged_df


#計算ETF報酬率
def calculate_returns(price_df):
    price_df = price_df.sort_values("trade_date")

    return_df = (price_df.drop(columns=["trade_date"]).pct_change())

    #清除異常值
    return_df = return_df.replace([np.inf, -np.inf],np.nan)

    return_df = return_df.dropna()

    return return_df


#投資組合績效
def portfolio_metrics(weights,mean_returns,cov_matrix):

  
    #年化報酬率
    portfolio_return = (np.sum(mean_returns * weights)*trading_days)


    #年化波動率
    portfolio_volatility = np.sqrt(
        np.dot(weights.T,
            np.dot(cov_matrix * trading_days,weights)))


    #防止除以0
    if portfolio_volatility <= 0.000001:

        sharpe_ratio = 0

    else:

        sharpe_ratio = ((portfolio_return - risk_free_rate) / portfolio_volatility)

    return (portfolio_return,portfolio_volatility,sharpe_ratio)


#蒙地卡羅模擬
def monte_carlo_simulation(returns_df,simulation=5000):

    mean_returns = returns_df.mean()

    cov_matrix = returns_df.cov()

    result = []

    for _ in range(simulation):

      
        #隨機權重
        weights = np.random.random(len(returns_df.columns))

        weights /= np.sum(weights)

        (portfolio_return,portfolio_volatility,sharpe_ratio) = portfolio_metrics(weights,mean_returns,cov_matrix)

        
        #避免NaN inf
        if (np.isnan(sharpe_ratio) or np.isinf(sharpe_ratio)):

            continue

        if (np.isnan(portfolio_volatility) or np.isinf(portfolio_volatility)):

            continue

        result.append([portfolio_return,portfolio_volatility,sharpe_ratio,*weights])

    columns = ["Return","Volatility","Sharpe Ratio", *returns_df.columns]

    simulation_df = pd.DataFrame(result,columns=columns)

    return simulation_df


#投資風格分類
def classify_risk_profile(volatility):
    if volatility < 0.10:

        return "保守型"

    elif volatility < 0.15:

        return "穩健型"

    elif volatility < 0.22:

        return "成長型"

    else:

        return "積極型"

#繪製效率前緣
def plot_efficient_frontier(simulation_df):
    simulation_df = simulation_df.dropna()   #清除異常資料

    simulation_df = simulation_df[simulation_df["Volatility"] > 0]

    if len(simulation_df) == 0:     # 防止空資料
        print("沒有可用的投資組合資料")

        return

    plt.figure(figsize=(12,7))

    scatter = plt.scatter(simulation_df["Volatility"],simulation_df["Return"],c=simulation_df["Sharpe Ratio"],cmap="viridis")

    plt.colorbar(scatter,label="Sharpe Ratio")

    plt.xlabel("投資波動率")
    plt.ylabel("預期報酬率")
    plt.title("ETF 效率前緣")

#最大Sharpe
    max_sharpe = simulation_df.loc[simulation_df["Sharpe Ratio"].idxmax()]

    plt.scatter(max_sharpe["Volatility"],max_sharpe["Return"],color="red",s=250,marker="*",label="最佳風險報酬組合")

   
    #風格區域線
    plt.axvline(x=0.10,color="green",linestyle="--",alpha=0.6)

    plt.axvline(x=0.15,color="orange",linestyle="--",alpha=0.6)

    plt.axvline(x=0.22,color="red",linestyle="--",alpha=0.6)


    #投資風格文字
    plt.text(
        0.05,
        0.18,
        "保守型",
        fontsize=10
    )

    plt.text(
        0.11,
        0.18,
        "穩健型",
        fontsize=10
    )

    plt.text(
        0.17,
        0.18,
        "成長型",
        fontsize=10
    )

    plt.text(
        0.24,
        0.18,
        "積極型",
        fontsize=10
    )

    plt.legend()

    plt.tight_layout()

    plt.show()
    
    #主程式
def main():

    # 讀取ETF資料
    price_df = load_all_etf_data()

    # 計算ETF報酬率
    return_df = calculate_returns(price_df)

    # 蒙地卡羅模擬
    simulation_df = monte_carlo_simulation(return_df)

    
    #投資風格分類
    simulation_df["Risk Profile"] = (simulation_df["Volatility"] .apply(classify_risk_profile))

    #儲存CSV
    simulation_df.to_csv("dashboard/portfolio_simulation.csv",index=False)

    #最佳配置
    print("\n====================")
    print("Sharpe Ratio 最高配置")
    print("====================\n")
    print(simulation_df.sort_values("Sharpe Ratio",ascending=False).head(1))

   
    #繪製效率前緣
    plot_efficient_frontier(simulation_df)


#執行主程式
if __name__ == "__main__":

    main()

