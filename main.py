import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import yfinance as yf
import duckduckgo_search as ddgs

# Load environment variables
load_dotenv()

class FinanceAgentApp:
    def __init__(self):
        # Initialize Groq client
        self.groq_client = Groq(
            api_key=os.getenv('GROQ_API_KEY')
        )

    def duckduckgo_search(self, query):
        """Perform web search using DuckDuckGo"""
        try:
            search_results = ddgs.ddg(query, max_results=5)
            return search_results
        except Exception as e:
            st.error(f"Web search error: {e}")
            return []

    def get_stock_info(self, ticker):
        """Retrieve stock information using yfinance"""
        try:
            stock = yf.Ticker(ticker)
            
            # Basic stock info
            info = stock.info
            
            # Recent stock price
            history = stock.history(period="1d")
            current_price = history['Close'].iloc[0] if not history.empty else "N/A"
            
            # Analyst recommendations
            recommendations = stock.recommendations
            
            # Recent news
            news = stock.news[:5]
            
            return {
                "basic_info": info,
                "current_price": current_price,
                "recommendations": recommendations,
                "news": news
            }
        except Exception as e:
            st.error(f"Stock info retrieval error: {e}")
            return None

    def generate_analysis(self, stock_info, web_search_results):
        """Generate investment analysis using Groq"""
        try:
            prompt = f"""Provide a comprehensive investment analysis based on the following information:

Stock Information:
{stock_info['basic_info']}

Current Price: {stock_info['current_price']}

Analyst Recommendations:
{stock_info['recommendations']}

Web Search Results:
{web_search_results}

Please create a detailed report including:
1. Company Overview
2. Recent Performance
3. Market Sentiment
4. Investment Recommendation
5. Key Risks and Opportunities
"""
            
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a financial analyst providing investment insights."},
                    {"role": "user", "content": prompt}
                ],
                model="llama3-70b-8192"
            )
            
            return chat_completion.choices[0].message.content
        except Exception as e:
            st.error(f"Analysis generation error: {e}")
            return None

    def render_app(self):
        """Main Streamlit application rendering"""
        st.title("📈 AI Finance Agent")
        st.subheader("Investment Research & Analysis")

        # Sidebar for configuration
        with st.sidebar:
            st.header("Configuration")
            api_key = st.text_input("Groq API Key", type="password", 
                                    help="Your Groq API key for generating analysis")
            if api_key:
                os.environ['GROQ_API_KEY'] = api_key

        # Stock ticker input
        ticker = st.text_input("Enter Stock Ticker", placeholder="e.g., AAPL")
        
        if st.button("Analyze Investment") and ticker:
            with st.spinner("Gathering financial insights..."):
                # Step 1: Get Stock Information
                stock_info = self.get_stock_info(ticker)
                
                # Step 2: Perform Web Search
                web_search = self.duckduckgo_search(f"{ticker} stock investment analysis")
                
                # Step 3: Generate Comprehensive Analysis
                if stock_info and web_search:
                    analysis = self.generate_analysis(stock_info, web_search)
                    
                    # Display Results
                    st.subheader(f"Investment Analysis for {ticker}")
                    
                    # Stock Price Section
                    st.metric("Current Price", f"${stock_info['current_price']:.2f}")
                    
                    # Detailed Analysis
                    st.markdown("### 📊 Comprehensive Analysis")
                    st.write(analysis)
                    
                    # Recent News
                    st.subheader("📰 Recent News")
                    for news_item in stock_info['news']:
                        st.markdown(f"**{news_item['title']}**")
                        st.write(news_item['link'])
                else:
                    st.warning("Could not retrieve complete information. Please check the ticker.")

def main():
    app = FinanceAgentApp()
    app.render_app()

if __name__ == "__main__":
    main()
