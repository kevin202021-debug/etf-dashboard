# ETF Portfolio Analysis Dashboard

## Project Overview

This project analyzes multiple Taiwan ETFs using Python, SQLite, and Tableau.

The project focuses on:

- ETF return analysis
- Risk and volatility analysis
- Portfolio optimization
- Efficient Frontier simulation
- Interactive Tableau dashboard

---

## ETFs Included

| ETF | Type |
|---|---|
| 0050 | Taiwan Top 50 ETF |
| 00878 | High Dividend ETF |
| 00981A | Active ETF |
| 00679B | US Bond ETF |

---

## Technologies Used

- Python
- Pandas
- NumPy
- SQLite
- Tableau
- yfinance API
- Matplotlib

---

## Project Architecture

Yahoo Finance API
↓
Python ETL
↓
SQLite Database
↓
Portfolio Analysis
↓
Tableau Dashboard

---

## Features

### 1. ETF Data Pipeline

- Automatically download ETF historical data
- Store data into SQLite database
- Support multi-ETF analysis

### 2. Return Analysis

- Daily return
- Cumulative return
- ETF performance comparison

### 3. Risk Analysis

- Volatility
- Sharpe Ratio
- Correlation Matrix

### 4. Portfolio Optimization

- Monte Carlo Simulation
- Efficient Frontier
- Optimal portfolio allocation

### 5. Tableau Dashboard

- Interactive ETF dashboard
- Risk-return visualization
- Correlation heatmap

---

## Key Insights

- Bond ETF reduced portfolio volatility.
- High-dividend ETF showed relatively stable performance.
- Portfolio diversification improved Sharpe Ratio.

---

## Future Improvements

- Add more ETFs
- Add machine learning prediction
- Add macroeconomic indicators
- Deploy dashboard online