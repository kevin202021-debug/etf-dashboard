import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import os

#streamlit設定
st.set_page_config(page_title="ETF 投資組合分析平台",page_icon="📈",layout="wide")

#title
st.title("📈 ETF 新手投資組合分析")
st.caption("透過 ETF 歷史資料模擬不同資產配置的長期投資績效")

st.markdown("""
提供服務：

- ETF 資產配置分析
- 定期定額模擬
- 投資風險評估
- 歷史情境分析
""")

#核心概念
st.markdown("---")
st.header("核心概念")
st.write("""
許多投資新手：

- 不知道自己適合哪種投資風格
- 不知道如何做 ETF 資產配置
- 害怕市場下跌
- 缺乏風險概念

因此：

透過 ETF 歷史資料分析、
定期定額模擬、
風險測驗、
市場情境模擬，

協助新手投資者
建立風險認知與長期投資觀念。
""")

#Database
DB_PATH = "data/ETF_Project.db"

#ETF資訊
ETF_INFO = {
    "0050": {
        "name": "元大台灣50",
        "table": "etf_0050",
        "type": "市值型"
    },

    "006208": {
        "name": "富邦台50",
        "table": "etf_006208",
        "type": "市值型"
    },

    "0056": {
        "name": "元大高股息",
        "table": "etf_0056",
        "type": "高股息"
    },

    "00679B": {
        "name": "元大美債20年",
        "table": "etf_00679b",
        "type": "債券型"
    },

    "00687B": {
        "name": "國泰20年美債",
        "table": "etf_00687b",
        "type": "債券型"
    },

    "00631L": {
        "name": "元大台灣50正2",
        "table": "etf_00631l",
        "type": "槓桿型"
    },

    "00632R": {
        "name": "元大台灣反1",
        "table": "etf_00632r",
        "type": "反向型"
    }
}

#讀取ETF資料
@st.cache_data
def load_etf(table_name):
    try:
        conn = sqlite3.connect(DB_PATH)
        query = f"""
        SELECT *
        FROM {table_name}
        """
        df = pd.read_sql(query, conn)
        conn.close()

        df["trade_date"] = pd.to_datetime(
            df["trade_date"]
        )
        return df

    except Exception as e:
        st.error(f"資料庫讀取失敗：{e}")
        st.stop()

#投資風格小測驗
st.markdown("---")
st.header("投資風格小測驗")
st.write("回答以下問題，系統會自動推薦適合你的投資風格！")
col1, col2 = st.columns(2)
with col1:
    q1 = st.radio(
        "1. 如果你的 ETF 在一個禮拜內下跌10%，你最可能會？",
        [
            "立刻賣掉止損！",
            "再觀察幾天看看好了",
            "長期持有 蓋牌不看！",
            "好機會 趁機加碼＾＾"
        ]
    )

    q2 = st.radio(
        "2. 你期望你的投資帶來什麼效果？",
        [
            "盡量不要虧損",
            "穩定慢慢成長",
            "長期資產增加",
            "追求高獲利"
        ]
    )

    q3 = st.radio(
        "3. 如果帳面虧損，你大概能接受多少？",
        [
            "幾乎不能虧",
            "小幅虧損可以(0~5%)",
            "中等波動可以接受(5~10%)",
            "大幅波動也撐得住!(10%以上)"
        ]
    )
with col2:
    q4 = st.radio(
        "4. 如果投資短期下跌，你願意等多久讓它慢慢回升？",
        [
            "不想等太久!",
            "1~3年",
            "3~5年",
            "5年以上"
        ]
    )
    q5 = st.radio(
        "5. 你目前的收入狀況如何？",
        [
            "不太穩定",
            "普普通通",
            "穩定",
            "非常穩定且有成長性"
        ]
    )

    q6 = st.radio(
        "6. 你對投資市場熟悉嗎？",
        [
            "完全不熟",
            "略懂略懂",
            "有投資經驗",
            "非常熟悉市場運作"
        ]
    )

#分數對照
score_map = {

    "立刻賣掉止損！": 1,
    "再觀察幾天看看好了": 2,
    "長期持有 蓋牌不看！": 3,
    "好機會 趁機加碼＾＾": 4,

    "盡量不要虧損": 1,
    "穩定慢慢成長": 2,
    "長期資產增加": 3,
    "追求高獲利": 4,

    "幾乎不能虧": 1,
    "小幅虧損可以(0~5%)": 2,
    "中等波動可以接受(5~10%)": 3,
    "大幅波動也撐得住!(10%以上)": 4,

    "不想等太久!": 1,
    "1~3年": 2,
    "3~5年": 3,
    "5年以上": 4,

    "不太穩定": 1,
    "普普通通": 2,
    "穩定": 3,
    "非常穩定且有成長性": 4,

    "完全不熟": 1,
    "略懂略懂": 2,
    "有投資經驗": 3,
    "非常熟悉市場運作": 4
}

risk_score = (score_map[q1]+score_map[q2]+score_map[q3]+score_map[q4]+score_map[q5]+score_map[q6])

#風格分類
if risk_score <= 9:
    risk_profile = "保守型"
elif risk_score <= 14:
    risk_profile = "穩健型"
elif risk_score <= 19:
    risk_profile = "成長型"
else:
    risk_profile = "積極型"
st.success(f"你的投資風格：{risk_profile}")

#側邊欄
st.sidebar.title("投資設定")
monthly_investment = st.sidebar.number_input(
    "每月投入金額",
    min_value=1000,
    max_value=1000000,
    value=10000,
    step=1000
)
portfolio_template = st.sidebar.selectbox(
    "投資風格",
    [
        "自訂配置",
        "保守型",
        "穩健型",
        "成長型",
        "積極型"
    ]
)

#預設權重
default_weights = {
    "0050": 0,
    "006208": 0,
    "0056": 0,
    "00679B": 0,
    "00687B": 0,
    "00631L": 0,
    "00632R": 0
}
#風格模板
if portfolio_template != "自訂配置":

    if portfolio_template == "保守型":

        default_weights["0050"] = 35 
        default_weights["0056"] = 15 
        default_weights["00679B"] = 30 
        default_weights["00687B"] = 20

    elif portfolio_template == "穩健型":

        default_weights["0050"] = 45
        default_weights["0056"] = 25
        default_weights["00679B"] = 20
        default_weights["00687B"] = 10



    elif portfolio_template == "成長型":

        default_weights["0050"] = 55 
        default_weights["0056"] = 15 
        default_weights["00679B"] = 10 
        default_weights["00631L"] = 20

    elif portfolio_template == "積極型":

      default_weights["0050"] = 50
      default_weights["0056"] = 10
      default_weights["00631L"] = 40




#ETF權重設定
weights = {}
st.sidebar.markdown("---")
st.sidebar.subheader("ETF 配置比例")
for etf_code, info in ETF_INFO.items():
    weights[etf_code] = st.sidebar.number_input(
        f"{etf_code} {info['name']} ({info['type']})",
        min_value=0,
        max_value=100,
        value=default_weights[etf_code],
        step=5
    )


#權重檢查
total_weight = sum(weights.values())
st.sidebar.write(f"目前總權重：{total_weight}%")

if total_weight != 100:
    st.sidebar.error("總權重必須等於100%")
    st.stop()

#載入ETF報酬資料
returns_data = []
for etf_code, info in ETF_INFO.items():
    if weights[etf_code] > 0:
        df = load_etf(
            info["table"]
        )
        temp = pd.DataFrame({
            "trade_date":
            df["trade_date"],
            etf_code:
            df["close_price"].pct_change()
        })
        returns_data.append(temp)

#防止空資料
if len(returns_data) == 0:
    st.error("請至少選擇一個 ETF")
    st.stop()

merged_df = returns_data[0]
for df in returns_data[1:]:
    merged_df = pd.merge(
        merged_df,
        df,
        on="trade_date",
        how="outer"
    )

merged_df = merged_df.sort_values("trade_date")
merged_df = merged_df.fillna(0)
merged_df = merged_df.set_index("trade_date")

#投資組合報酬
selected_columns = merged_df.columns
weight_array = np.array([weights[col] / 100 for col in selected_columns])
portfolio_return = (merged_df * weight_array).sum(axis=1)

#定期定額模擬
daily_investment = (monthly_investment / 21)
portfolio_value = []
current_value = 0
for daily_return in portfolio_return:
    current_value += daily_investment
    current_value *= (1 + daily_return)
    portfolio_value.append(current_value)

portfolio_value = pd.Series(
    portfolio_value,
    index=portfolio_return.index
)


#累積本金
cumulative_investment = pd.Series(np.arange
    (1,len(portfolio_value) + 1) * daily_investment,
    index=portfolio_value.index
)

#累積報酬率
cumulative_return = (portfolio_value - cumulative_investment)/cumulative_investment

#KPI
end_value = portfolio_value.iloc[-1] #最後總資產
total_investment = cumulative_investment.iloc[-1] #總投入本金
total_return = (end_value / total_investment) - 1 #總報酬率
years = (portfolio_value.index[-1]-portfolio_value.index[0]).days / 365 #總投資年數

#長期平均年化報酬
if years > 0:
    cagr = (
        (end_value / total_investment)
        ** (1 / years)
    ) - 1
else:
    cagr = 0

#年化波動率
annual_volatility = (portfolio_return.std()* np.sqrt(252))

#最大回撤
running_max = cumulative_return.cummax()
running_max = running_max.replace(0,np.nan)
drawdown = (cumulative_return - running_max)/running_max

max_drawdown = drawdown.min()
max_drawdown = (max_drawdown if pd.notna(max_drawdown) else 0)


# AI 投資分析
st.markdown("---")
st.header("AI 投資顧問分析")
st.info(f"""
### AI 分析結果

- 長期平均年化報酬：約 {cagr:.2%}

- 歷史最大回撤：約 {max_drawdown:.2%}

- 年化波動度：約 {annual_volatility:.2%}

- 此投資組合較適合：
  {risk_profile} 投資人

⚠ 投資一定有風險，
過去績效不一定百分之百等於未來報酬。
""")


#KPI顯示
st.markdown("---")
st.subheader("投資組合績效")
col1, col2, col3, col4 = st.columns(4)
col1.metric("目前資產",f"${end_value:,.0f}")
col2.metric("總報酬率",f"{total_return:.2%}")
col3.metric("年化報酬率",f"{cagr:.2%}")
col4.metric("年化波動率",f"{annual_volatility:.2%}")


#ETF配置圖
st.markdown("---")
st.subheader("ETF 資產配置比例")
allocation_df = pd.DataFrame({"ETF": selected_columns,"Weight": weight_array * 100})
fig_pie = px.pie(allocation_df,names="ETF",values="Weight")
st.plotly_chart(fig_pie,use_container_width=True)


#投資組合資產總值
st.markdown("---")
st.subheader("投資組合資產總值")
fig_value = go.Figure()
fig_value.add_trace(
    go.Scatter(x=portfolio_value.index,y=portfolio_value,mode="lines",name="資產總值"))

fig_value.update_layout(xaxis_title="日期",yaxis_title="資產金額（元）")
st.plotly_chart(fig_value,use_container_width=True)

#累積報酬率
st.markdown("---")
st.subheader("長期投資績效")
fig_return = go.Figure()
fig_return.add_trace(
    go.Scatter(x=cumulative_return.index,y=cumulative_return,mode="lines",name="累積報酬率"))

fig_return.update_layout(xaxis_title="日期",yaxis_title="累積報酬率 (%)",yaxis_tickformat=".0%")
st.plotly_chart(fig_return,use_container_width=True)

#Benchmark比較
st.markdown("---")
st.subheader("投資組合 vs 0050")
benchmark_df = load_etf("etf_0050")
benchmark_return = (benchmark_df["close_price"].pct_change().fillna(0))
benchmark_return.index = (benchmark_df["trade_date"])
benchmark_cumulative = (1 + benchmark_return).cumprod() - 1
portfolio_cumulative = (1 + portfolio_return).cumprod() - 1
fig_compare = go.Figure()
fig_compare.add_trace(
    go.Scatter(x=portfolio_cumulative.index,y=portfolio_cumulative,mode="lines",name="投資組合"))

fig_compare.add_trace(go.Scatter(x=benchmark_cumulative.index,y=benchmark_cumulative,mode="lines",name="0050"))

fig_compare.update_layout(xaxis_title="日期",yaxis_title="累積報酬率 (%)",yaxis_tickformat=".0%")

st.plotly_chart(fig_compare,use_container_width=True)

#年度報酬率
st.markdown("---")
st.subheader("各年度投資報酬率")
yearly_return = (
    portfolio_return
    .resample("YE")
    .apply(
        lambda x:
        (1 + x).prod() - 1
    )
)

yearly_return_df = pd.DataFrame({
    "年度":yearly_return.index.year,
    "年度報酬率":yearly_return.values
})

st.dataframe(
    yearly_return_df.style.format({"年度報酬率":"{:.2%}"}),
    use_container_width=True
)

fig_year = px.bar(yearly_return_df,x="年度",y="年度報酬率",text_auto=".2%")
fig_year.update_layout(yaxis_tickformat=".0%",xaxis_title="年度",yaxis_title="報酬率 (%)")
st.plotly_chart(fig_year,use_container_width=True)

#歷史市場情境模擬
st.markdown("---")
st.subheader("📉 歷史市場情境模擬")

scenario = st.selectbox(
    "選擇歷史市場情境",
    [
        "2020 疫情",
        "2022 升息與俄烏戰爭",
        "2025 關稅",
        "台股30000點到40000點"
    ]
)

#情境日期設定
if scenario == "2020 疫情":

    # COVID 股災
    start_date = "2020-01-01"
    end_date = "2020-12-31"

elif scenario == "2022 升息與俄烏戰爭":

    # 美國升息 + 俄烏戰爭
    start_date = "2022-01-01"
    end_date = "2022-12-31"

elif scenario == "2025 關稅":

    # 關稅事件
    start_date = "2025-01-01"
    end_date = "2025-12-31"

elif scenario == "台股30000點到40000點":

    # AI 牛市
    start_date = "2026-01-05"
    end_date = "2026-04-27"


# 區間報酬資料
# 重新從該情境開始計算
scenario_return = portfolio_return[
    (portfolio_return.index >= start_date)
    &
    (portfolio_return.index <= end_date)
]


# 區間累積報酬
# 從該情境重新開始
scenario_period = (1 + scenario_return).cumprod() - 1

#情境分析
if len(scenario_period) > 0:
    # 區間最低報酬
    scenario_min_return = scenario_period.min()

    # 區間最高報酬
    scenario_max_return = scenario_period.max()

    # 假設投入100萬
    scenario_min_amount = int(
        1000000 * (1 + scenario_min_return)
    )

    scenario_max_amount = int(
        1000000 * (1 + scenario_max_return)
    )

  
    #顯示結果
    st.warning(f"""
    ### {scenario}

    假設投入 100 萬元：

    - 區間最低資產：
      ${scenario_min_amount:,.0f}

    - 區間最高資產：
      ${scenario_max_amount:,.0f}

    - 區間最低報酬：
      {scenario_min_return:.2%}

    - 區間最高報酬：
      {scenario_max_return:.2%}
    """)

 
    #圖表
    fig_scenario = go.Figure()

    fig_scenario.add_trace(
        go.Scatter(
            x=scenario_period.index,
            y=scenario_period,
            mode="lines",
            name=scenario
        )
    )

    fig_scenario.update_layout(
        xaxis_title="日期",
        yaxis_title="累積報酬率 (%)",
        yaxis_tickformat=".0%"
    )

    st.plotly_chart(
        fig_scenario,
        use_container_width=True
    )

#資料來源
st.markdown("---")
st.subheader("資料來源")
st.write("""
- Yahoo Finance
- 台灣證券交易所
""")

#風險聲明
st.subheader("風險聲明")
st.caption("""
本平台僅供一種分析方向，
不構成任何投資建議。

投資一定存在風險，
過去績效不一定百分之百等於未來報酬。
""")
