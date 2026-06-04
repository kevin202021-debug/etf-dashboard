import sqlite3
import pandas as pd

ETF_TABLES=["etf_0050","etf_00878","etf_00981a","etf_00679b"]

def load_data():
    conn=sqlite3.connect("data/ETF_Project.db")

    all_data=[]
    
    try:
        for table in ETF_TABLES:
            query=f"""
            SELECT
                trade_date,close_price
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

def main():
    df=load_data()
    return_df=(df.drop(columns=["trade_date"]).pct_change().dropna())

    corr_matrix=return_df.corr()
    corr_matrix.to_csv("dashboard/correlation_matrix.csv")
    print("Correlation Matrix 匯出成功!")

if __name__=="__main__":
    main()


