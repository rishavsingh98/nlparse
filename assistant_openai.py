import os
import json
import re
from web_search import WebSearcher

class AssistantResponse:
    def __init__(self, intent_category, entities, confidence_score, follow_up_questions=None):
        self.intent_category = intent_category
        self.entities = entities  
        self.confidence_score = confidence_score
        self.follow_up_questions = follow_up_questions or []

class OpenAIPersonalAssistant:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Need OpenAI API key")
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            self.web_searcher = WebSearcher()
        except ImportError:
            raise ValueError("OpenAI package not installed")

    @staticmethod
    def is_available():
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            return True, "OpenAI ready"
        return False, "No API key"

    def process_input(self, user_input, existing_entities=None):
        try:
            result = self._classify(user_input, existing_entities)
            
            followups = []
            intent = result["intent_category"]
            entities = result["entities"]
            
            # Handle "other" intent with web search
            if intent == "other":
                # Perform web search for the query
                search_results = self.web_searcher.get_search_summary(user_input)
                
                # Use AI to generate a helpful response based on web search
                web_response = self._generate_web_search_response(user_input, search_results)
                
                # Update entities with web search information
                entities = entities or {}
                entities["web_search_performed"] = True
                entities["search_query"] = user_input
                entities["ai_response"] = web_response
                
                # Return with high confidence since we have web results
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
                elif not entities.get("date"):
                    followups.append("What date?")
                elif not entities.get("time"):
                    followups.append("What time?")
            
            elif intent == "travel":
                if not entities.get("destination"):
                    followups.append("Where to?")
                elif not entities.get("departure_date"):
                    followups.append("When?")
                elif not entities.get("number_of_travelers"):
                    followups.append("How many travelers?")
            
            return AssistantResponse(
                intent_category=result["intent_category"],
                entities=result["entities"],
                confidence_score=result["confidence_score"],
                follow_up_questions=followups
            )
            
        except Exception:
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
        
        prompt = f"""Classify this request into one of these categories:
- dining (restaurants, food)
- travel (trips, hotels)  
- gifting (gifts, presents)
- cab_booking (rides, taxis)
- other (everything else)

Extract relevant entities like dates, times, numbers, locations.

Request: "{user_input}"{context}

Calculate confidence_score (0.0-1.0) based on:
1. Intent clarity (0.2-0.5): How clearly the request matches a category
   - Multiple matching keywords = higher score
   - Ambiguous request = lower score
2. Entity completeness (0.0-0.4): How many required entities are found
   - dining: cuisine, party_size, date, time
   - travel: destination, departure_date, number_of_travelers  
   - gifting: recipient, occasion, budget
   - cab_booking: pickup_location, destination, date, time
3. Quality bonus (0.0-0.1): Well-formatted dates/times, specific details

Example scores:
- "Book Italian restaurant" = 0.4 (clear intent, missing details)
- "Book Italian restaurant for 4 tomorrow 8pm" = 0.9 (clear + complete)
- "I need something" = 0.1 (vague intent, no entities)

Return JSON with intent_category, entities dict, and confidence_score."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON from response
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = json.loads(result_text)
            
            # Merge with existing entities
            if existing_entities:
                merged = existing_entities.copy()
                merged.update(result.get("entities", {}))
                result["entities"] = merged
                
            return result
            
        except:
            return {
                "intent_category": "other",
                "entities": existing_entities or {},
                "confidence_score": 0.0
            } 

    def _generate_web_search_response(self, query: str, search_results: str) -> str:
        """Generate a helpful response based on web search results"""
        prompt = f"""Based on the following web search results, provide a helpful and informative response to the user's query.

User Query: {query}

Web Search Results:
{search_results}

Instructions:
1. Synthesize the information from the search results
2. Provide a clear, concise, and helpful answer
3. If the search results contain specific steps or procedures, include them
4. Mention the sources when providing specific information
5. Be conversational and helpful
6. If the search results don't fully answer the question, acknowledge this

Response:"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            # Fallback response if AI fails
            return f"I found some information about '{query}' from web search:\n\n{search_results}\n\nPlease review the search results above for relevant information." 