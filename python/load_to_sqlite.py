import sqlite3
import pandas as pd

CSV_PATH = "data/etf_price.csv"
DB_PATH = "data/ETF_Project.db"

ETF_TABLES = {"0050.TW": "etf_0050","006208.TW":"etf_006208",
              "0056.TW":"etf_0056",
              "00679B.TWO": "etf_00679b","00687B.TWO":"etf_00687b",
              "00631L.TW":"etf_00631l",
              "00632.TW":"etf_00632r"}

def main():

    df = pd.read_csv(CSV_PATH)

    df = df[["Date","ETF","Open","High","Low","Close","Volume"]]

    df.columns = ["trade_date","etf_code","open_price","high_price","low_price","close_price","volume"]

    df["trade_date"] = pd.to_datetime(df["trade_date"])

    with sqlite3.connect(DB_PATH) as conn:

        for etf_code, table_name in ETF_TABLES.items():

            temp_df = df[df["etf_code"] == etf_code]

            temp_df.to_sql(table_name,conn,if_exists="replace",index=False)

            print(f"{table_name} 匯入成功")

        df.to_sql("etf_price",conn,if_exists="replace",index=False)

        print("etf_price 匯入成功")


if __name__ == "__main__":
    main()
