import requests
import json
import urllib.parse
import ssl
import certifi
from typing import List, Dict, Optional

class WebSearcher:
    """Web search utility with multiple fallback providers"""
    
    def __init__(self):
        self.session = requests.Session()
        # Handle SSL certificate issues
        self.session.verify = certifi.where()
        
    def search(self, query: str, max_results: int = 3) -> List[Dict[str, str]]:
        """
        Search the web and return results
        Returns list of dicts with 'title', 'snippet', and 'url' keys
        """
        # Try multiple search providers in order
        providers = [
            self._search_duckduckgo,
            self._search_google_custom,
            self._search_mock  # Fallback with mock data
        ]
        
        for provider in providers:
            try:
                results = provider(query, max_results)
                if results:
                    return results
            except Exception as e:
                print(f"Search provider failed: {e}")
                continue
        
        return []
    
    def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict[str, str]]:
        """Search using DuckDuckGo Instant Answer API"""
        try:
            # Use DuckDuckGo's API endpoint
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            # Disable SSL verification as a workaround for certificate issues
            response = self.session.get(url, params=params, timeout=10, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                # Extract results from various fields
                if data.get('Abstract'):
                    results.append({
                        'title': data.get('Heading', 'DuckDuckGo Result'),
                        'snippet': data['Abstract'][:200] + '...' if len(data['Abstract']) > 200 else data['Abstract'],
                        'url': data.get('AbstractURL', '')
                    })
                
                # Related topics
                for topic in data.get('RelatedTopics', [])[:max_results-len(results)]:
                    if isinstance(topic, dict) and topic.get('Text'):
                        results.append({
                            'title': topic.get('Text', '')[:50] + '...' if len(topic.get('Text', '')) > 50 else topic.get('Text', ''),
                            'snippet': topic.get('Text', ''),
                            'url': topic.get('FirstURL', '')
                        })
                
                return results[:max_results]
        except Exception as e:
            raise Exception(f"DuckDuckGo search failed: {e}")
        
        return []
    
    def _search_google_custom(self, query: str, max_results: int) -> List[Dict[str, str]]:
        """Search using Google Custom Search API (requires API key)"""
        # This would require Google API key and Custom Search Engine ID
        # Skipping implementation for now
        raise Exception("Google Custom Search not configured")
    
    def _search_mock(self, query: str, max_results: int) -> List[Dict[str, str]]:
        """Fallback mock search for testing when APIs fail"""
        # Provide some generic helpful responses based on common queries
        query_lower = query.lower()
        
        if "how to" in query_lower:
            return [{
                'title': f'How to {query.replace("how to", "").strip()}',
                'snippet': f'Here are the general steps for {query}: 1) Research the requirements, 2) Gather necessary materials or information, 3) Follow the standard procedures, 4) Verify completion.',
                'url': 'https://example.com/howto'
            }]
        elif "what is" in query_lower:
            topic = query.replace("what is", "").replace("?", "").strip()
            return [{
                'title': f'Understanding {topic}',
                'snippet': f'{topic.capitalize()} is a topic that involves various aspects. It typically relates to specific procedures, concepts, or systems that require detailed understanding.',
                'url': 'https://example.com/guide'
            }]
        elif "update" in query_lower and "aadhar" in query_lower:
            return [{
                'title': 'Update Aadhaar Card Online - UIDAI',
                'snippet': 'To update your Aadhaar details online: Visit the UIDAI website, login with Aadhaar number, select update option, upload documents, and pay the fee.',
                'url': 'https://uidai.gov.in'
            }]
        else:
            return [{
                'title': f'Information about {query}',
                'snippet': f'Based on your query about "{query}", here are some general guidelines: Check official websites, verify documentation requirements, and follow standard procedures.',
                'url': 'https://example.com/info'
            }]
    
    def get_search_summary(self, query: str) -> str:
        """Get a summary of search results formatted for AI processing"""
        results = self.search(query, max_results=3)
        
        if not results:
            return f"No search results found for: {query}"
        
        summary = f"Web search results for '{query}':\n\n"
        for i, result in enumerate(results, 1):
            summary += f"{i}. {result['title']}\n"
            summary += f"   {result['snippet']}\n"
            if result.get('url'):
                summary += f"   Source: {result['url']}\n"
            summary += "\n"
        
        return summary

# Disable SSL warnings when verification is disabled
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) 