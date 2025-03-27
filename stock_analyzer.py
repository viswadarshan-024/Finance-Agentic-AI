import yfinance as yf
import streamlit as st

class StockAnalyzer:
    @staticmethod
    def get_stock_info(ticker):
        """
        Retrieve comprehensive stock information
        
        Args:
            ticker (str): Stock ticker symbol
        
        Returns:
            dict: Detailed stock information
        """
        try:
            stock = yf.Ticker(ticker)
            
            # Basic stock information
            info = stock.info
            
            # Extract key financial metrics
            stock_data = {
                "Symbol": ticker,
                "Company Name": info.get('longName', 'N/A'),
                "Current Price": info.get('currentPrice', 'N/A'),
                "Market Cap": info.get('marketCap', 'N/A'),
                "Sector": info.get('sector', 'N/A'),
                "Industry": info.get('industry', 'N/A'),
                "P/E Ratio": info.get('trailingPE', 'N/A'),
                "Dividend Yield": info.get('dividendYield', 'N/A'),
                "52-Week Low": info.get('fiftyTwoWeekLow', 'N/A'),
                "52-Week High": info.get('fiftyTwoWeekHigh', 'N/A'),
                "Average Volume": info.get('averageVolume', 'N/A')
            }
            
            return stock_data
        
        except Exception as e:
            st.error(f"Error retrieving stock information: {e}")
            return None

    @staticmethod
    def format_stock_info(stock_data):
        """
        Format stock information for display
        
        Args:
            stock_data (dict): Stock information dictionary
        
        Returns:
            str: Formatted stock information
        """
        if not stock_data:
            return "No stock information available."
        
        formatted_info = "🔍 **Stock Analysis Report**\n\n"
        for key, value in stock_data.items():
            formatted_info += f"**{key}**: {value}\n"
        
        return formatted_info
