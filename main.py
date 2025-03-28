import streamlit as st
import yfinance as yf
from groq import Groq
from googleapiclient.discovery import build
import traceback
import plotly.express as px
import pandas as pd

class FinanceIntelligenceApp:
    def __init__(self):
        """Initialize the application with secure API access"""
        # Access Streamlit secrets
        self.groq_api_key = st.secrets.get("GROQ_API_KEY")
        self.google_search_api_key = st.secrets.get("GOOGLE_SEARCH_API_KEY")
        self.google_search_engine_id = st.secrets.get("GOOGLE_SEARCH_ENGINE_ID")

        # Initialize clients
        try:
            self.groq_client = Groq(api_key=self.groq_api_key)
            self.google_search_client = build(
                "customsearch", 
                "v1", 
                developerKey=self.google_search_api_key
            )
        except Exception as e:
            st.error(f"Client Initialization Error: {e}")

    def render_sidebar(self):
        """
        Create an informative sidebar with application details and usage guide
        """
        st.sidebar.title("Finance Intelligence Pro")
        
        st.sidebar.markdown("""
        ## About the App
        An AI-powered financial research tool that provides:
        - Real-time stock information
        - Comprehensive market insights
        - AI-generated financial analysis
        """)
        
        st.sidebar.markdown("### 🔍 How to Use")
        st.sidebar.markdown("""
        1. Enter a stock ticker (e.g., AAPL, GOOGL)
        2. Click "Analyze Stocks"
        3. View detailed financial insights
        """)
        
        st.sidebar.markdown("### 💡 Example Tickers")
        example_tickers = [
            "AAPL (Apple)", 
            "GOOGL (Google)", 
            "MSFT (Microsoft)", 
            "AMZN (Amazon)", 
            "NVDA (NVIDIA)"
        ]
        for ticker in example_tickers:
            st.sidebar.markdown(f"- {ticker}")
        
        st.sidebar.markdown("### ℹ️ Key Features")
        features = [
            "Real-time stock data retrieval",
            "AI-powered market analysis",
            "Interactive price trend charts",
            "Web search insights"
        ]
        for feature in features:
            st.sidebar.markdown(f"- {feature}")
        
        st.sidebar.markdown("""
        ---
        *Powered by Groq, Google Search, and Yahoo Finance*
        """)

    def get_stock_info(self, ticker):
        """
        Comprehensive stock information retrieval
        Handles multiple potential data sources and error scenarios
        """
        try:
            # Validate ticker
            if not ticker or not isinstance(ticker, str):
                st.warning("Please enter a valid stock ticker")
                return None

            # Fetch stock data
            stock = yf.Ticker(ticker.upper())
            
            # Retrieve comprehensive information
            info = stock.info
            if not info:
                st.warning(f"No information found for ticker: {ticker}")
                return None

            # Historical price data
            history = stock.history(period="1mo")
            
            # Construct detailed stock data dictionary
            stock_data = {
                "ticker": ticker.upper(),
                "name": info.get('longName', ticker),
                "current_price": round(info.get('regularMarketPrice', 0), 2),
                "previous_close": round(info.get('previousClose', 0), 2),
                "open_price": round(info.get('regularMarketOpen', 0), 2),
                "day_high": round(info.get('dayHigh', 0), 2),
                "day_low": round(info.get('dayLow', 0), 2),
                "volume": info.get('volume', 0),
                "market_cap": f"${info.get('marketCap', 0):,}",
                "pe_ratio": round(info.get('trailingPE', 0), 2),
                "dividend_yield": f"{info.get('dividendYield', 0)*100:.2f}%",
                "52_week_high": round(info.get('fiftyTwoWeekHigh', 0), 2),
                "52_week_low": round(info.get('fiftyTwoWeekLow', 0), 2),
                "sector": info.get('sector', 'N/A'),
                "industry": info.get('industry', 'N/A')
            }
            
            return stock_data
        
        except Exception as e:
            st.error(f"Stock Information Retrieval Error: {e}")
            return None

    def generate_google_search(self, query):
        """
        Advanced Google Search with refined results
        """
        try:
            search_results = self.google_search_client.cse().list(
                q=query,
                cx=self.google_search_engine_id,
                num=5
            ).execute()
            
            # Process and refine search results
            refined_results = []
            if 'items' in search_results:
                for item in search_results['items']:
                    refined_results.append({
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', '')
                    })
            
            return refined_results
        
        except Exception as e:
            st.error(f"Google Search Error: {e}")
            return []

    def generate_ai_analysis(self, stock_info, search_results):
        """
        AI-Powered Financial Analysis Generation
        """
        try:
            # Construct detailed prompt
            sources_text = "\n".join([
                f"Source: {result['title']}\n"
                f"Snippet: {result['snippet']}\n"
                f"Link: {result['link']}"
                for result in search_results
            ])
            
            prompt = f"""Provide a comprehensive investment analysis for {stock_info['ticker']}:

FORMATTING INSTRUCTIONS:
- Use clear, professional markdown formatting
- Structure the analysis with clear headings and subheadings
- Use bullet points for key insights
- Highlight important information with bold or italic text
- Maintain a professional, analytical tone
- Provide actionable insights

Stock Overview:
- Company: {stock_info['name']}
- Current Price: ${stock_info['current_price']}
- Market Cap: {stock_info['market_cap']}
- Sector: {stock_info['sector']}
- Industry: {stock_info['industry']}

Price Performance:
- 52-Week Range: ${stock_info['52_week_low']} - ${stock_info['52_week_high']}
- Day Range: ${stock_info['day_low']} - ${stock_info['day_high']}
- Previous Close: ${stock_info['previous_close']}

Financial Metrics:
- P/E Ratio: {stock_info['pe_ratio']}
- Dividend Yield: {stock_info['dividend_yield']}

Web Search Insights:
{sources_text}

Analysis Requirements:
1. Comprehensive company overview
2. Recent financial performance
3. Market sentiment and trends
4. Potential investment risks and opportunities
5. Short to medium-term outlook"""
            
            # Generate analysis using Groq
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a professional financial analyst providing nuanced investment insights."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                max_tokens=1500,
                temperature=0.3
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            st.error(f"AI Analysis Generation Error: {e}")
            return None

    def create_price_trend_chart(self, ticker):
        """
        Create interactive price trend chart
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1y")
            
            # Create interactive line chart with enhanced styling
            fig = px.line(
                hist, 
                x=hist.index, 
                y='Close', 
                title=f'{ticker} Stock Price Trend (Past Year)',
                labels={'Close': 'Price', 'Date': 'Date'}
            )
            
            # Customize chart appearance
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#e0e0e0',
                title_font_size=20,
                title_x=0.5
            )
            fig.update_xaxes(
                showgrid=True, 
                gridwidth=1, 
                gridcolor='rgba(255,255,255,0.1)'
            )
            fig.update_yaxes(
                showgrid=True, 
                gridwidth=1, 
                gridcolor='rgba(255,255,255,0.1)'
            )
            
            return fig
        
        except Exception as e:
            st.error(f"Price Chart Generation Error: {e}")
            return None

    def render_app(self):
        """
        Enhanced Streamlit Application Rendering with Dark Theme
        """
        # Page Configuration
        st.set_page_config(
            page_title="Finance Intelligence Pro",
            page_icon="📈",
            layout="wide"
        )

        # Render Sidebar
        self.render_sidebar()

        # Custom Dark Theme CSS
        st.markdown("""
        <style>
        /* Dark Theme Base */
        body {
            color: #e0e0e0;
            background-color: #121212;
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
        }
        ::-webkit-scrollbar-track {
            background: #1e1e1e;
        }
        ::-webkit-scrollbar-thumb {
            background: #4a4a4a;
            border-radius: 5px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #6a6a6a;
        }

        /* Streamlit Container Styles */
        .stApp {
            background-color: #121212;
        }
        .stCard {
            background-color: #1e1e1e;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .stCard:hover {
            transform: scale(1.02);
        }

        /* Typography */
        h1, h2, h3, h4, h5, h6 {
            color: #4CAF50 !important;
            font-weight: 600;
        }

        /* Input and Button Styles */
        .stTextInput > div > div > input {
            color: #e0e0e0;
            background-color: #2c2c2c !important;
            border: 1px solid #4a4a4a !important;
            border-radius: 8px;
            padding: 10px;
        }
        .stButton > button {
            background-color: #4CAF50 !important;
            color: white !important;
            border-radius: 8px;
            border: none;
            padding: 10px 20px;
            font-weight: bold;
            transition: background-color 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #45a049 !important;
        }

        /* Sidebar Enhancements */
        .css-1aumxhk {
            background-color: #1e1e1e !important;
        }
        .css-1aumxhk .stMarkdown {
            color: #e0e0e0 !important;
        }

        /* Metric Styles */
        .metric-container {
            background-color: #1e1e1e;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .metric-value {
            color: #4CAF50;
            font-size: 1.5em;
            font-weight: bold;
        }
        .metric-label {
            color: #a0a0a0;
            font-size: 0.9em;
        }

        /* Spinner and Progress Bar */
        .stSpinner > div {
            border-color: #4CAF50 transparent #4CAF50 transparent !important;
        }
        </style>
        """, unsafe_allow_html=True)

        # Main Application Title with Gradient
        st.markdown("""
        <div style="background: linear-gradient(135deg, #4CAF50, #2196F3); 
                    -webkit-background-clip: text; 
                    -webkit-text-fill-color: transparent; 
                    font-size: 3em; 
                    font-weight: bold; 
                    text-align: center; 
                    margin-bottom: 20px;">
            Finance Intelligence Pro
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <p style="color: #a0a0a0; text-align: center; margin-bottom: 30px;">
        AI-Powered Investment Research & Insights
        </p>
        """, unsafe_allow_html=True)

        # Stock Ticker Input
        col1, col2 = st.columns([3, 1])
        with col1:
            ticker = st.text_input(
                "Enter Stock Ticker", 
                placeholder="e.g., AAPL, GOOGL",
                help="Enter a valid stock ticker symbol"
            )
        
        with col2:
            st.write(" ") # Spacer
            analyze_button = st.button("Analyze Stocks", type="primary")

        # Analysis Section
        if analyze_button and ticker:
            with st.spinner("🔍 Conducting deep financial research..."):
                try:
                    # Retrieve Stock Information
                    stock_info = self.get_stock_info(ticker)
                    
                    if not stock_info:
                        st.warning("Unable to retrieve stock information. Check the ticker symbol.")
                        return

                    # Perform Web Search
                    search_query = f"{ticker} stock financial analysis current market insights"
                    search_results = self.generate_google_search(search_query)

                    # Generate AI Analysis
                    ai_analysis = self.generate_ai_analysis(stock_info, search_results)
                    
                    # Price Trend Chart
                    price_chart = self.create_price_trend_chart(ticker)

                    # Display Results
                    if ai_analysis:
                        # Key Metrics Display
                        st.subheader(f"📊 {stock_info['name']} ({stock_info['ticker']}) Analysis")
                        
                        # Metrics Columns
                        metrics_cols = st.columns(4)
                        metrics_data = [
                            ("Current Price", f"${stock_info['current_price']}"),
                            ("Market Cap", stock_info['market_cap']),
                            ("P/E Ratio", stock_info['pe_ratio']),
                            ("Dividend Yield", stock_info['dividend_yield'])
                        ]
                        
                        for col, (label, value) in zip(metrics_cols, metrics_data):
                            col.metric(label, value)

                        # Price Trend Chart
                        if price_chart:
                            st.plotly_chart(price_chart, use_container_width=True)

                        # AI Generated Analysis
                        st.markdown("### 🤖 AI Insights")
                        st.write(ai_analysis)

                        # Web Sources
                        with st.expander("Sources Consulted"):
                            for source in search_results:
                                st.markdown(f"- **{source['title']}** ([Link]({source['link']}))")

                    else:
                        st.warning("Could not generate comprehensive analysis.")
                
                except Exception as e:
                    st.error(f"Unexpected Error: {e}")
                    st.warning("Please try again with a different stock ticker.")

def main():
    # Initialize and run the application
    app = FinanceIntelligenceApp()
    app.render_app()

if __name__ == "__main__":
    main()
