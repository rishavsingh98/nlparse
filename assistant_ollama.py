import json
import re
from web_search import WebSearcher

class OllamaPersonalAssistant:
    def __init__(self, model="llama3.2:3b"):
        self.model = model
        self.url = "http://localhost:11434"
        self.web_searcher = WebSearcher()

    @staticmethod
    def is_available():
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                if any("llama3.2" in m["name"] for m in models):
                    return True, "Ollama ready"
            return False, "Model not found"
        except:
            return False, "Ollama not running"

    def process_input(self, user_input, existing_entities=None):
        try:
            result = self._classify(user_input, existing_entities)
            
            followups = []
            intent = result["intent_category"]
            entities = result["entities"]
            
            # Merge with existing
            if existing_entities:
                entities.update(existing_entities)
            
            # Handle "other" intent with web search
            if intent == "other":
                # Perform web search for the query
                search_results = self.web_searcher.get_search_summary(user_input)
                
                # Use AI to generate a helpful response based on web search
                web_response = self._generate_web_search_response(user_input, search_results)
                
                # Update entities with web search information
                entities["web_search_performed"] = True
                entities["search_query"] = user_input
                entities["ai_response"] = web_response
                
                # Return with high confidence since we have web results
                from assistant_openai import AssistantResponse
                return AssistantResponse(
                    intent_category=intent,
                    entities=entities,
                    confidence_score=0.85,  # High confidence with web results
                    follow_up_questions=[]
                )
            
            # Check for missing info
            if intent == "dining":
                if not entities.get("cuisine"):
                    followups.append("What type of cuisine?")
                elif not entities.get("party_size"):
                    followups.append("How many people?")
            
            # Use the same response class structure as OpenAI assistant
            from assistant_openai import AssistantResponse
            return AssistantResponse(
                intent_category=intent,
                entities=entities,
                confidence_score=result["confidence_score"],
                follow_up_questions=followups
            )
            
        except Exception:
            from assistant_openai import AssistantResponse
            return AssistantResponse(
                intent_category="other",
                entities={},
                confidence_score=0.0,
                follow_up_questions=["Could you rephrase that?"]
            )

    def _classify(self, user_input, existing_entities=None):
        # Build context if we have existing entities
        context = ""
        if existing_entities and any(v for v in existing_entities.values() if v):
            context = f"\nPrevious context: {json.dumps(existing_entities)}"
            context += "\n(Increase confidence based on accumulated information)"
            
        prompt = f"""Classify this request and extract entities:

Categories: dining, travel, gifting, cab_booking, other

Request: "{user_input}"{context}

Calculate confidence_score (0.0-1.0) based on:
1. Intent clarity (0.2-0.5): How clearly the request matches a category
2. Entity completeness (0.0-0.4): How many required entities are found
   - dining: cuisine, party_size, date, time
   - travel: destination, departure_date, number_of_travelers
   - gifting: recipient, occasion, budget
   - cab_booking: pickup_location, destination, date, time
3. Quality bonus (0.0-0.1): Well-formatted data, specific details

Examples:
- "Book Italian restaurant" = 0.4
- "Book Italian restaurant for 4 tomorrow 8pm" = 0.9
- "I need something" = 0.1

Return JSON with intent_category, entities dict, confidence_score."""
        
        try:
            import requests
            response = requests.post(
                f"{self.url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result_text = response.json().get("response", "")
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            
            # Fallback
            return {
                "intent_category": "other",
                "entities": {},
                "confidence_score": 0.3
            }
            
        except:
            return {
                "intent_category": "other", 
                "entities": {},
                "confidence_score": 0.0
            } 

    def _generate_web_search_response(self, query: str, search_results: str) -> str:
        """Generate a helpful response based on web search results"""
        prompt = f"""Based on web search results, provide a helpful response.

User Query: {query}

Web Search Results:
{search_results}

Provide a clear, informative answer that synthesizes the search results. Include specific steps if found. Be helpful and conversational."""

        try:
            import requests
            response = requests.post(
                f"{self.url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7,
                    "max_tokens": 500
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get("response", "").strip()
        except Exception:
            pass
        
        # Fallback response if AI fails
        return f"I found some information about '{query}' from web search:\n\n{search_results}\n\nPlease review the search results above for relevant information." 