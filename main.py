import streamlit as st
from dotenv import load_dotenv
import os

# Import custom modules
from src.stock_analyzer import StockAnalyzer
from src.financial_search import WebSearcher
from src.ai_insights import AIFinancialAnalyst

def main():
    # Load environment variables
    load_dotenv()

    # Page configuration
    st.set_page_config(
        page_title="AI Financial Analyst",
        page_icon="📊",
        layout="wide"
    )

    # Title and description
    st.title("🤖 AI Financial Analyst")
    st.markdown("*Empowering your financial research with AI-driven insights*")

    # Sidebar for user input
    st.sidebar.header("Financial Research Tools")
    
    # Stock ticker input
    ticker = st.sidebar.text_input(
        "Enter Stock Ticker", 
        placeholder="e.g., AAPL, GOOGL, MSFT"
    )

    # Search query input
    search_query = st.sidebar.text_input(
        "Market News & Trends Search",
        placeholder="e.g., Tech stocks, Market trends"
    )

    # Analysis button
    analyze_button = st.sidebar.button("Analyze Financial Data")

    # Main content area
    if analyze_button and ticker:
        # Initialize modules
        stock_analyzer = StockAnalyzer()
        web_searcher = WebSearcher()
        ai_analyst = AIFinancialAnalyst()

        # Perform stock analysis
        stock_data = stock_analyzer.get_stock_info(ticker)
        formatted_stock_info = stock_analyzer.format_stock_info(stock_data)
        
        # Perform web search
        search_results = web_searcher.search_financial_news(
            f"{ticker} stock market news", 
            max_results=3
        )
        formatted_search_results = web_searcher.display_search_results(search_results)
        
        # Generate AI insights
        ai_insights = ai_analyst.generate_financial_insights(stock_data, search_results)

        # Display results
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Stock Information")
            st.markdown(formatted_stock_info)
        
        with col2:
            st.markdown("### 📰 Market News")
            st.markdown(formatted_search_results)
        
        # AI Insights Section
        st.markdown("### 🧠 AI Financial Analysis")
        st.markdown(ai_insights)

    elif analyze_button and search_query:
        # Perform web search for general market trends
        web_searcher = WebSearcher()
        search_results = web_searcher.search_financial_news(search_query)
        formatted_search_results = web_searcher.display_search_results(search_results)
        
        st.markdown("### 📰 Market News and Trends")
        st.markdown(formatted_search_results)

    # Footer
    st.sidebar.markdown("""
    ---
    **Disclaimer**: 
    - Information for research purposes only
    - Not financial advice
    - Always consult financial professionals
    """)

if __name__ == "__main__":
    main()
