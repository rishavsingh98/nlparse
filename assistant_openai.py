import os
import json
import re

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
        prompt = f"""Classify this request into one of these categories:
- dining (restaurants, food)
- travel (trips, hotels)  
- gifting (gifts, presents)
- cab_booking (rides, taxis)
- other (everything else)

Extract relevant entities like dates, times, numbers, locations.

Request: "{user_input}"

Return JSON with intent_category, entities dict, and confidence_score (0-1).
"""
        
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