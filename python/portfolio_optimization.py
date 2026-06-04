import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

trading_days=252
risk_free_rate=0.01

etf_tables=["etf_0050","etf_00878","etf_00981a","etf_00679b"]

def load_all_etf_data():
    conn=sqlite3.connect("data/ETF_Project.db")
    all_data=[]

    try:
        for table in etf_tables:
            query=f"""
            SELECT
                trade_date,
                close_price
            FROM {table}
            """

            df=pd.read_sql(query,conn)
            df["trade_date"]=pd.to_datetime(df["trade_date"])
            df=df.rename(columns={"close_price":table})
            all_data.append(df)

    finally:
        conn.close()

    merged_df=all_data[0]
    for df in all_data[1:]:
        merged_df=pd.merge(merged_df,df,on="trade_date",how="inner")

    return merged_df

def calculate_returns(price_df):
    price_df=price_df.sort_values("trade_date")
    return_df=(price_df.drop(columns=["trade_date"]).pct_change())

    return_df=return_df.dropna()
    return return_df

def protfolio_metrics(weights,mean_returns,cov_matrix):
    portfolio_return=np.sum(mean_returns*weights)*trading_days

    portfolio_volatility=np.sqrt(np.dot(weights.T,np.dot(cov_matrix*trading_days,weights)))        

    sharpe_ratio=(portfolio_return-risk_free_rate)/portfolio_volatility

    return(portfolio_return,portfolio_volatility,sharpe_ratio)

def monte_carlo_simulation(returns_df,simulation=5000):
    mean_returns=returns_df.mean()
    cov_matrix=returns_df.cov()
    result=[]

    for _ in range(simulation):
        weights=np.random.random(len(returns_df.columns))
        weights/=np.sum(weights)

        portfolio_return,portfolio_volatility,sharpe_ratio=(protfolio_metrics(weights,mean_returns,cov_matrix))
        
        result.append([portfolio_return,portfolio_volatility,sharpe_ratio,*weights])

        columns=["Return","Volatility","Sharpe Ratio",*returns_df.columns]
        
    return pd.DataFrame(result,columns=columns)
    
def plot_efficient_frontier(simulation_df):
    plt.figure(figsize=(12,7))
    scatter=plt.scatter(simulation_df["Volatility"],simulation_df["Return"],c=simulation_df["Sharpe Ratio"],cmap="viridis")

    plt.colorbar(scatter,label="Sharpe Ratio")
    plt.xlabel("Volatility")
    plt.ylabel("Return")
    plt.title("Efficient Frontier")

    max_sharpe=simulation_df.loc[simulation_df["Sharpe Ratio"].idxmax()]

    plt.scatter(max_sharpe["Volatility"],max_sharpe["Return"],color="red",s=200,marker="*",label="Max Sharpe")
    plt.legend()
    plt.tight_layout()
    plt.show()

def main():
    price_df=load_all_etf_data()
    return_df=calculate_returns(price_df)
    simulation_df=monte_carlo_simulation(return_df)
    simulation_df.to_csv("dashboard/portfolio_simulation.csv",index=False)
    print(simulation_df.sort_values("Sharpe Ratio",ascending=False).head(1))
    plot_efficient_frontier(simulation_df)

if __name__=="__main__":
    main()        

