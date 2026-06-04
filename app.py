import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import PercentFormatter

# mac中文字體設定
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
# 修正負號顯示
plt.rcParams['axes.unicode_minus'] = False

# Streamlit 設定
st.set_page_config(page_title="ETF投資組合分析平台",layout="wide")

# 標題
st.title("ETF 投資組合分析平台")

st.markdown("""
模擬 ETF 定期定額投資績效

資料期間：

2019/01/01 ~ Today

""")
#資料庫
DB_PATH = "data/ETF_Project.db"


# 讀取 ETF 資料
@st.cache_data
def load_etf(table_name):
    conn = sqlite3.connect(DB_PATH)
    query = f"""
    SELECT *
    FROM {table_name}
    """

    df = pd.read_sql(query,conn)
    conn.close()

    df["trade_date"] = pd.to_datetime(df["trade_date"])
    return df

# ETF 分類
ETF_OPTIONS = {
    "市值型": {"0050": "etf_0050","006208": "etf_006208"},
    "高股息": { "0056": "etf_0056"},
    "債券型": {"00679B": "etf_00679b","00687B": "etf_00687b"},
    "槓桿型": {"00631L": "etf_00631l"},
    "反向型": { "00632R": "etf_00632r"}
}

# 側邊欄位
st.sidebar.title("投資組合配置")

# 每月定期定額
monthly_investment = st.sidebar.number_input("每月定期定額",min_value=1000,value=10000,step=1000)


# 權重設定
weights = {}
for category, etfs in ETF_OPTIONS.items():
    st.sidebar.subheader(category)
    for etf_name in etfs.keys():
        weights[etf_name] = st.sidebar.number_input(f"{etf_name} 配置比例",min_value=0,max_value=100,value=0,step=1)


# 權重防呆
total_weight = sum(weights.values())
st.sidebar.write(f"目前總權重：{total_weight}%")

if total_weight != 100:
    st.error("總權重必須等於100%")
    st.stop()

# 載入 ETF 報酬資料
returns_data = []
for category, etfs in ETF_OPTIONS.items():
    for etf_name, table_name in etfs.items():
        if weights[etf_name] > 0:
            df = load_etf(table_name)
            temp = pd.DataFrame({"trade_date":df["trade_date"],etf_name:df["close_price"].pct_change()})
            returns_data.append(temp)


#Merge Return
merged_df = returns_data[0]
for df in returns_data[1:]:
    merged_df = pd.merge(merged_df,df,on="trade_date",how="outer")


# 日期排序
merged_df = merged_df.sort_values("trade_date")

# 缺值補0
merged_df = merged_df.fillna(0)

#日期 Index
merged_df = merged_df.set_index("trade_date")


# 投資組合報酬率
weight_array = []
selected_columns = merged_df.columns
for col in selected_columns:
    weight_array.append(weights[col] / 100)

weight_array = np.array(weight_array)

portfolio_return = (merged_df * weight_array).sum(axis=1)

# 定期定額投資
portfolio_value = []
current_value = 0
daily_investment = monthly_investment / 21
for daily_return in portfolio_return:
    current_value += daily_investment
    current_value *= (1 + daily_return)
    portfolio_value.append(current_value)

portfolio_value = pd.Series(portfolio_value,index=portfolio_return.index)

#累積投入本金
cumulative_investment = pd.Series(np.arange(1, len(portfolio_value) + 1)* daily_investment,index=portfolio_value.index)


#真正累積報酬率
cumulative_return = (portfolio_value - cumulative_investment) / cumulative_investment

#CAGR
end_value = portfolio_value.iloc[-1]
years = (portfolio_value.index[-1] - portfolio_value.index[0]).days / 365

cagr = ((end_value / cumulative_investment.iloc[-1]) ** (1 / years)) - 1


#總投入金額
total_investment = cumulative_investment.iloc[-1]


#損益金額
profit = (end_value - total_investment)

#總報酬率
total_return = (end_value / total_investment) - 1


#年化波動率
annual_volatility = (portfolio_return.std() * np.sqrt(252))

#夏普值
risk_free_rate = 0.01 
sharpe_ratio = (cagr - risk_free_rate) / annual_volatility

# 最大回撤
running_max = (cumulative_return.cummax())

drawdown = (cumulative_return - running_max) / running_max

max_drawdown = drawdown.min()


#歷史最佳和最差單日報酬
best_return = portfolio_return.max()
worst_return = portfolio_return.min()


#KPI顯示
st.subheader("投資組合績效")
col1, col2, col3 = st.columns(3)
col1.metric("每月投入金額",f"${monthly_investment:,.0f}")
col2.metric("總投入金額",f"${total_investment:,.0f}")
col3.metric("目前資產價值",f"${end_value:,.0f}")

col4, col5, col6 = st.columns(3)
col4.metric("損益金額",f"${profit:,.0f}")
col5.metric("總報酬率",f"{total_return:.2%}")
col6.metric("CAGR 年化報酬率",f"{cagr:.2%}")

col7, col8, col9 = st.columns(3)
col7.metric("年化波動率",f"{annual_volatility:.2%}")
col8.metric("夏普值",f"{sharpe_ratio:.2f}")
col9.metric("最大跌幅",f"{max_drawdown:.2%}")

col10, col11 = st.columns(2)
col10.metric("最佳單日報酬",f"{best_return:.2%}")
col11.metric("最差單日報酬",f"{worst_return:.2%}")

#顯示選擇ETF
selected_etfs = [etf for etf, weight in weights.items() if weight > 0]
st.write("目前投資組合：",", ".join(selected_etfs))


#投資組合資產總值圖
st.subheader("投資組合資產總值")
fig_value, ax_value = plt.subplots(figsize=(14, 7))
ax_value.plot(portfolio_value.index,portfolio_value,linewidth=2)
ax_value.set_title("投資組合資產總值",fontsize=18)
ax_value.set_xlabel("年份",fontsize=12)
ax_value.set_ylabel("資產金額 ($)",fontsize=12)
ax_value.grid(True)
ax_value.xaxis.set_major_locator(mdates.YearLocator())
ax_value.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
fig_value.autofmt_xdate()
st.pyplot(fig_value)


#累積報酬率走勢圖
st.subheader("累積報酬率走勢圖")
fig, ax = plt.subplots(figsize=(14, 7))
cumulative_return_pct = (cumulative_return * 100)
ax.plot(cumulative_return_pct.index,cumulative_return_pct,linewidth=2)
ax.set_title("投資組合累積報酬率",fontsize=18)
ax.set_xlabel("年份",fontsize=12)
ax.set_ylabel("累積報酬率 (%)",fontsize=12)
ax.yaxis.set_major_formatter(PercentFormatter())
ax.grid(True)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
fig.autofmt_xdate()
st.pyplot(fig)

#各年度報酬率
st.subheader("各年度報酬率")
yearly_return = (portfolio_return.resample("Y").apply(lambda x:(1 + x).prod() - 1))
yearly_return.index = (yearly_return.index.year)
yearly_return_df = pd.DataFrame({"年度":yearly_return.index,"年度報酬率":yearly_return.values})
yearly_return_df["年度報酬率"] = (yearly_return_df["年度報酬率"] * 100)

st.dataframe(yearly_return_df.style.format({"年度報酬率": "{:.2f}%"}))

#年度報酬率圖
st.subheader("年度報酬率圖")

fig2, ax2 = plt.subplots(figsize=(12, 6))

ax2.bar(yearly_return.index.astype(str),yearly_return.values * 100)
ax2.set_title("各年度報酬率",fontsize=18)
ax2.set_xlabel("年份",fontsize=12)
ax2.set_ylabel("報酬率 (%)",fontsize=12)
ax2.yaxis.set_major_formatter(PercentFormatter())
ax2.grid(True)
st.pyplot(fig2)

#報酬資料
st.subheader("投資組合報酬資料")

st.dataframe(merged_df.tail(20))