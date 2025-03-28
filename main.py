import os
import json
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import yfinance as yf
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()

class FinanceAgentApp:
    def __init__(self):
        # Initialize Groq client
        self.groq_client = Groq(
            api_key=os.getenv('GROQ_API_KEY')
        )
        
        # Initialize Google Search client
        self.google_search_client = build(
            "customsearch", 
            "v1", 
            developerKey=os.getenv('GOOGLE_SEARCH_API_KEY')
        )

    def google_grounded_search(self, query, num_results=5):
        """
        Perform a grounded search using Google Custom Search API
        
        Grounded search strategies:
        1. Use specific search parameters
        2. Filter for recent, high-quality sources
        3. Limit to specific domains if needed
        """
        try:
            # Perform search with advanced parameters
            search_results = self.google_search_client.cse().list(
                q=query,
                cx=os.getenv('GOOGLE_SEARCH_ENGINE_ID'),
                num=num_results,
                sort='date',  # Sort by date to get recent results
                # Optional: restrict to specific domains for financial information
                siteSearch='finance.yahoo.com,seekingalpha.com,bloomberg.com,reuters.com',
                # Optionally add more filters like date range
                dateRestrict='m[1]'  # Results from last month
            ).execute()
            
            # Process and return refined results
            refined_results = []
            if 'items' in search_results:
                for item in search_results['items']:
                    refined_results.append({
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'source': item.get('displayLink', '')
                    })
            
            return refined_results
        
        except Exception as e:
            st.error(f"Google Search error: {e}")
            return []

    def get_stock_info(self, ticker):
        """Retrieve comprehensive stock information"""
        try:
            stock = yf.Ticker(ticker)
            
            # Comprehensive stock information gathering
            info = stock.info
            history = stock.history(period="1mo")
            
            # Extended stock metrics
            stock_data = {
                "basic_info": info,
                "current_price": history['Close'].iloc[-1] if not history.empty else "N/A",
                "52_week_high": info.get('fiftyTwoWeekHigh', "N/A"),
                "52_week_low": info.get('fiftyTwoWeekLow', "N/A"),
                "market_cap": info.get('marketCap', "N/A"),
                "pe_ratio": info.get('trailingPE', "N/A"),
                "dividend_yield": info.get('dividendYield', "N/A"),
                "recommendations": stock.recommendations,
                "earnings_dates": stock.earnings_dates,
                "news": stock.news[:5]
            }
            
            return stock_data
        
        except Exception as e:
            st.error(f"Stock info retrieval error: {e}")
            return None

    def generate_grounded_analysis(self, stock_info, search_results):
        """
        Generate a grounded, contextually rich investment analysis
        
        Grounding strategies:
        1. Incorporate web search context
        2. Provide multi-source perspective
        3. Highlight verifiable information
        """
        try:
            # Construct a comprehensive prompt with multiple information sources
            sources_text = "\n".join([
                f"Source {i+1}: {result['title']} ({result['source']})\n"
                f"Snippet: {result['snippet']}\n"
                f"Link: {result['link']}"
                for i, result in enumerate(search_results)
            ])
            
            prompt = f"""Provide a comprehensive, multi-source investment analysis with a strong emphasis on verifiable facts:

Stock Fundamentals:
- Current Price: ${stock_info['current_price']}
- 52-Week Range: ${stock_info['52_week_low']} - ${stock_info['52_week_high']}
- Market Cap: {stock_info['market_cap']}
- P/E Ratio: {stock_info['pe_ratio']}
- Dividend Yield: {stock_info['dividend_yield']}

Recent Web Search Context:
{sources_text}

Analysis Requirements:
1. Synthesize information from stock data and web sources
2. Provide a balanced investment perspective
3. Highlight key risks and opportunities
4. Use clear, evidence-based language
5. Cite sources where possible

Format the analysis as a professional investment report with clear sections and actionable insights."""
            
            # Generate analysis using Groq's Llama model
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an objective financial analyst. Provide nuanced, data-driven investment insights."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                model="llama3-70b-8192",
                temperature=0.3,  # Lower temperature for more focused output
                max_tokens=1000
            )
            
            return chat_completion.choices[0].message.content
        
        except Exception as e:
            st.error(f"Grounded analysis generation error: {e}")
            return None

    def render_app(self):
        """Main Streamlit application interface"""
        st.title("🔍 Grounded Finance Intelligence")
        st.subheader("AI-Powered Investment Research")

        # Sidebar configuration
        with st.sidebar:
            st.header("🔑 API Configuration")
            groq_key = st.text_input("Groq API Key", type="password")
            google_search_key = st.text_input("Google Search API Key", type="password")
            google_search_engine_id = st.text_input("Google Search Engine ID")
            
            # Allow dynamic API key setting
            if groq_key:
                os.environ['GROQ_API_KEY'] = groq_key
            if google_search_key:
                os.environ['GOOGLE_SEARCH_API_KEY'] = google_search_key
            if google_search_engine_id:
                os.environ['GOOGLE_SEARCH_ENGINE_ID'] = google_search_engine_id

        # Stock analysis section
        ticker = st.text_input("Enter Stock Ticker", placeholder="e.g. AAPL, GOOGL")
        
        if st.button("Generate Grounded Analysis") and ticker:
            with st.spinner("Conducting comprehensive research..."):
                # Retrieve stock information
                stock_info = self.get_stock_info(ticker)
                
                # Perform grounded web search
                search_query = f"{ticker} stock analysis latest financial insights"
                search_results = self.google_grounded_search(search_query)
                
                # Generate analysis
                if stock_info and search_results:
                    analysis = self.generate_grounded_analysis(stock_info, search_results)
                    
                    # Display results
                    st.subheader(f"🔬 Grounded Analysis: {ticker}")
                    
                    # Stock key metrics
                    cols = st.columns(3)
                    cols[0].metric("Current Price", f"${stock_info['current_price']}")
                    cols[1].metric("Market Cap", str(stock_info['market_cap']))
                    cols[2].metric("P/E Ratio", str(stock_info['pe_ratio']))
                    
                    # Detailed analysis
                    st.markdown("### 📊 Comprehensive Insights")
                    st.write(analysis)
                    
                    # Web sources used
                    st.subheader("🌐 Sources Consulted")
                    for source in search_results:
                        st.markdown(f"- **{source['title']}** ([Read More]({source['link']}))")
                
                else:
                    st.warning("Unable to generate analysis. Please verify the stock ticker.")

def main():
    app = FinanceAgentApp()
    app.render_app()

if __name__ == "__main__":
    main()
