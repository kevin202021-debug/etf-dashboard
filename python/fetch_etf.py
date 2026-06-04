import pandas as pd
import yfinance as yf

ETFS = ["0050.TW","006208.TW","0056.TW"
        ,"00687B.TWO","00679B.TWO","00631L.TW","00632R.TW"]

START_DATE = "2019-01-01"

def normalize_columns(df: pd.DataFrame):
    pd.DataFrame
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return df


def main():
    None
    data_frames = []

    for etf in ETFS:
        print(f"download {etf}...")

        df = yf.download(etf,start=START_DATE,progress=False,auto_adjust=True)
        df = normalize_columns(df)
        df = df.reset_index()
        df["ETF"] = etf
        df = df[["Date","ETF","Open","High","Low","Close","Volume"]]

        data_frames.append(df)

    final_df = pd.concat(data_frames,ignore_index=True)

    final_df.to_csv("data/etf_price.csv",index=False,encoding="utf-8-sig")
    
    print("ETF資料下載完成!")
    print(df.columns)

if __name__ == "__main__":
    main()
           
  