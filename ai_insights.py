from langchain.llms import Groq
from langchain.prompts import PromptTemplate
import os
import streamlit as st

class AIFinancialAnalyst:
    def __init__(self):
        """
        Initialize Groq language model
        """
        try:
            self.groq_api_key = os.getenv('GROQ_API_KEY')
            if not self.groq_api_key:
                raise ValueError("Groq API Key is missing")
            
            self.llm = Groq(
                groq_api_key=self.groq_api_key,
                model_name="llama3-70b-8192"
            )
        except Exception as e:
            st.error(f"Error initializing AI model: {e}")
            self.llm = None

    def generate_financial_insights(self, stock_data, news_results):
        """
        Generate AI-powered financial insights
        
        Args:
            stock_data (dict): Stock information
            news_results (list): Web search results
        
        Returns:
            str: AI-generated financial insights
        """
        if not self.llm:
            return "AI insights unavailable."

        try:
            # Construct detailed prompt
            prompt_template = PromptTemplate(
                input_variables=["stock_info", "market_news"],
                template="""
                Provide a comprehensive financial analysis based on the following information:

                Stock Information:
                {stock_info}

                Recent Market News:
                {market_news}

                Analysis Requirements:
                1. Summarize key financial indicators
                2. Provide context-aware market insights
                3. Discuss potential market trends
                4. Maintain an objective, research-based perspective
                5. Do NOT provide direct investment advice

                Deliverable: A balanced, informative financial analysis report.
                """
            )

            # Format inputs
            stock_info_str = "\n".join([f"{k}: {v}" for k, v in stock_data.items()])
            news_info_str = "\n".join([f"Title: {news['title']}, Snippet: {news['snippet']}" for news in news_results])

            # Generate insights
            prompt = prompt_template.format(
                stock_info=stock_info_str,
                market_news=news_info_str
            )

            insights = self.llm.invoke(prompt)
            return insights

        except Exception as e:
            st.error(f"Error generating AI insights: {e}")
            return "Unable to generate AI insights at this moment."
