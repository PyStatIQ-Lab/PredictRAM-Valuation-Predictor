import yfinance as yf
import pandas as pd
import streamlit as st
import numpy as np

# Function to fetch stock data from Yahoo Finance
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period='1y')
    info = stock.info
    dividend_history = stock.dividends
    shares_outstanding = stock.info.get('sharesOutstanding', 0)
    
    financials = {
        'P/E Ratio': info.get('trailingPE', 'N/A'),
        'P/B Ratio': info.get('priceToBook', 'N/A'),
        'EV/EBITDA': info.get('enterpriseToEbitda', 'N/A'),
        'ROE (%)': round(info.get('returnOnEquity', 0) * 100, 2) if info.get('returnOnEquity') else 'N/A',
        'Market Cap': info.get('marketCap', 'N/A'),
        'Dividend Yield (%)': round(info.get('dividendYield', 0) * 100, 2) if info.get('dividendYield') else 'N/A',
        'Shares Outstanding': shares_outstanding,
        'P/S Ratio': info.get('priceToSalesTrailing12Months', 'N/A'),
        'P/CF Ratio': info.get('priceToCashflow', 'N/A'),
        'Debt-to-Equity': info.get('debtToEquity', 'N/A'),
        'Beta': info.get('beta', 'N/A'),
        'Earnings Surprise': info.get('earningsQuarterlyGrowth', 'N/A'),
        'Analyst Rating': info.get('recommendationKey', 'N/A'),
    }
    
    return hist, financials, dividend_history, stock

# Function to calculate historical averages for P/E, P/B, and EV/EBITDA
def calculate_historical_averages(stock, hist):
    # Get historical data for ratios (we need them for each day)
    pe_history = []
    pb_history = []
    ev_ebitda_history = []
    
    for date in hist.index:
        # Fetch data for each date
        info = stock.history(period='1d', start=date, end=date)
        pe = info['P/E Ratio'][0] if 'P/E Ratio' in info else np.nan
        pb = info['P/B Ratio'][0] if 'P/B Ratio' in info else np.nan
        ev_ebitda = info['EV/EBITDA'][0] if 'EV/EBITDA' in info else np.nan
        
        pe_history.append(pe)
        pb_history.append(pb)
        ev_ebitda_history.append(ev_ebitda)
    
    # Calculate historical averages for the ratios
    pe_avg = np.nanmean(pe_history)
    pb_avg = np.nanmean(pb_history)
    ev_ebitda_avg = np.nanmean(ev_ebitda_history)
    
    return pe_avg, pb_avg, ev_ebitda_avg

# Function to analyze valuation comparison
def valuation_comparison(financials, hist_averages, stock_choice):
    analysis = []
    
    # Compare P/E Ratio
    pe_current = financials['P/E Ratio']
    pe_avg = hist_averages[0]
    
    if pe_current != 'N/A' and pe_avg != 'N/A':
        if pe_current < pe_avg:
            analysis.append(f"{stock_choice} is currently undervalued compared to its historical average P/E ratio ({pe_avg}).")
        else:
            analysis.append(f"{stock_choice} is currently overvalued compared to its historical average P/E ratio ({pe_avg}).")
    
    # Compare P/B Ratio
    pb_current = financials['P/B Ratio']
    pb_avg = hist_averages[1]
    
    if pb_current != 'N/A' and pb_avg != 'N/A':
        if pb_current < pb_avg:
            analysis.append(f"{stock_choice} is currently undervalued compared to its historical average P/B ratio ({pb_avg}).")
        else:
            analysis.append(f"{stock_choice} is currently overvalued compared to its historical average P/B ratio ({pb_avg}).")
    
    # Compare EV/EBITDA Ratio
    ev_ebitda_current = financials['EV/EBITDA']
    ev_ebitda_avg = hist_averages[2]
    
    if ev_ebitda_current != 'N/A' and ev_ebitda_avg != 'N/A':
        if ev_ebitda_current < ev_ebitda_avg:
            analysis.append(f"{stock_choice} is currently undervalued compared to its historical average EV/EBITDA ratio ({ev_ebitda_avg}).")
        else:
            analysis.append(f"{stock_choice} is currently overvalued compared to its historical average EV/EBITDA ratio ({ev_ebitda_avg}).")
    
    return analysis

# Streamlit Dashboard App
def main():
    st.title("Stock Valuation Dashboard with Historical Averages")
    
    # Sidebar for stock input
    st.sidebar.header("Stock Input")
    stock = st.sidebar.text_input("Enter the stock symbol (e.g., TCS.NS, ITC.NS):").strip().upper()
    
    if stock:
        if '.' not in stock:
            st.error("Invalid stock symbol format. Please include the exchange suffix (e.g., TCS.NS).")
        else:
            hist, financials, dividend_history, stock_obj = get_stock_data(stock)
            
            # Calculate historical averages for valuation ratios
            hist_averages = calculate_historical_averages(stock_obj, hist)
            
            # Create the dashboard layout
            col1, col2 = st.columns(2)
            
            with col1:
                st.header(f"Financial Metrics for {stock}")
                st.dataframe(pd.DataFrame(financials.items(), columns=['Metric', 'Value']))
                
            with col2:
                st.header("Historical Stock Data")
                st.line_chart(hist['Close'])
                
            # Valuation Comparison
            st.header(f"Valuation Comparison for {stock}")
            for line in valuation_comparison(financials, hist_averages, stock):
                st.write(line)

if __name__ == "__main__":
    main()
