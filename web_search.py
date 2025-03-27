from duckduckgo_search import DDGS
import streamlit as st

class WebSearcher:
    @staticmethod
    def search_financial_news(query, max_results=5):
        """
        Search financial news and market trends
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of search results
        
        Returns:
            list: News and market trend results
        """
        try:
            with DDGS() as ddgs:
                results = list(ddgs.news(query, max_results=max_results))
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "title": result.get('title', 'N/A'),
                    "snippet": result.get('body', 'N/A'),
                    "source": result.get('source', 'N/A'),
                    "date": result.get('date', 'N/A')
                })
            
            return formatted_results
        
        except Exception as e:
            st.error(f"Error performing web search: {e}")
            return []

    @staticmethod
    def display_search_results(results):
        """
        Display search results in a formatted manner
        
        Args:
            results (list): Search result dictionary
        
        Returns:
            str: Formatted search results
        """
        if not results:
            return "No search results found."
        
        formatted_results = "📰 **Market News and Trends**\n\n"
        for idx, result in enumerate(results, 1):
            formatted_results += f"**{idx}. {result['title']}**\n"
            formatted_results += f"*Source: {result['source']}*\n"
            formatted_results += f"*Date: {result['date']}*\n"
            formatted_results += f"{result['snippet']}\n\n"
        
        return formatted_results
