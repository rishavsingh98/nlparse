import json
import re

class OllamaPersonalAssistant:
    def __init__(self, model="llama3.2:3b"):
        self.model = model
        self.url = "http://localhost:11434"

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
            result = self._classify(user_input)
            
            followups = []
            intent = result["intent_category"]
            entities = result["entities"]
            
            # Merge with existing
            if existing_entities:
                entities.update(existing_entities)
            
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

    def _classify(self, user_input):
        prompt = f"""Classify this request and extract entities:

Categories: dining, travel, gifting, cab_booking, other

Request: "{user_input}"

Return JSON with intent_category, entities dict, confidence_score (0-1)."""
        
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