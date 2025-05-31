import streamlit as st
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import re
import time

# Import both assistant types
try:
    from assistant_openai import OpenAIPersonalAssistant, AssistantResponse
    openai_available = True
except:
    openai_available = False

try:
    from assistant_ollama import OllamaPersonalAssistant
    ollama_available = True
except:
    ollama_available = False

def fallback_intent_classifier(user_input: str) -> Dict[str, Any]:
    """Fallback rule-based classifier when AI models fail"""
    user_input_lower = user_input.lower()
    
    # Define keywords for each intent
    intent_keywords = {
        "dining": ["restaurant", "dinner", "lunch", "breakfast", "table", "booking", "reservation", "eat", "food", "cuisine", "menu", "dinning"],
        "travel": ["trip", "travel", "flight", "hotel", "vacation", "visit", "destination", "booking", "tickets"],
        "gifting": ["gift", "present", "birthday", "anniversary", "occasion", "buy", "shopping"],
        "cab_booking": ["cab", "taxi", "uber", "lyft", "ride", "pickup", "drop", "airport", "transport"],
        "other": []
    }
    
    # Score each intent based on keyword matches
    scores = {}
    for intent, keywords in intent_keywords.items():
        score = sum(1 for keyword in keywords if keyword in user_input_lower)
        if score > 0:
            scores[intent] = score
    
    # Determine best intent
    if scores:
        best_intent = max(scores, key=scores.get)
        confidence = min(scores[best_intent] * 0.15 + 0.3, 0.9)
    else:
        best_intent = "other"
        confidence = 0.3
    
    # Extract basic entities using regex patterns
    entities = {}
    
    # Extract numbers (for party size, budget, etc.)
    numbers = re.findall(r'\b\d+\b', user_input)
    
    # Improved time patterns
    time_patterns = re.findall(r'\b\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)\b', user_input)
    
    # Improved date patterns
    date_patterns = []
    date_formats = [
        r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\s*,?\s*\d{4}\b',
        r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(?:st|nd|rd|th)?\s*,?\s*\d{4}\b',
        r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\b',
        r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(?:st|nd|rd|th)?\b',
        r'\b\d{1,2}/\d{1,2}/\d{4}\b',
        r'\b\d{1,2}/\d{1,2}\b',
        r'\b\d{4}-\d{1,2}-\d{1,2}\b',
        r'\btoday\b',
        r'\btomorrow\b',
        r'\bnext\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
        r'\bthis\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b'
    ]
    
    for pattern in date_formats:
        matches = re.findall(pattern, user_input_lower)
        date_patterns.extend(matches)
    
    # Extract budget patterns
    budget_patterns = re.findall(r'\b(?:budget|cost|price|spend|around|under|max|maximum)\s*(?:of|is|at)?\s*\$?(\d+)\b', user_input_lower)
    
    # Extract party size patterns
    party_size_patterns = re.findall(r'\b(?:for|party\s+of|table\s+for)\s*(\d+)\s*(?:people?|person|pax|guests?)?\b|\b(\d+)\s*(?:person|people|pax|guests?)\b', user_input_lower)
    party_size = None
    if party_size_patterns:
        for pattern_groups in party_size_patterns:
            for group in pattern_groups:
                if group and group.isdigit():
                    party_size = group
                    break
            if party_size:
                break
    
    if not party_size and numbers:
        for num in numbers:
            if 1 <= int(num) <= 20:
                party_size = num
                break
    
    if best_intent == "dining":
        entities = {
            "cuisine": None,
            "party_size": party_size,
            "date": date_patterns[0] if date_patterns else None,
            "time": time_patterns[0] if time_patterns else None,
            "budget": budget_patterns[0] if budget_patterns else None,
            "location": None,
            "dietary_restrictions": None
        }
        
        # Extract cuisine types
        cuisines = ["italian", "chinese", "indian", "mexican", "french", "japanese", "thai", "american", "mediterranean", "korean", "vietnamese", "greek", "spanish", "turkish", "lebanese", "moroccan"]
        for cuisine in cuisines:
            if cuisine in user_input_lower:
                entities["cuisine"] = cuisine.title()
                break
    
    elif best_intent == "travel":
        entities = {
            "destination": None,
            "departure_date": date_patterns[0] if date_patterns else None,
            "return_date": None,
            "number_of_travelers": party_size,
            "budget": budget_patterns[0] if budget_patterns else None,
            "accommodation_type": None,
            "transportation": None
        }
        
        destinations = re.findall(r'\bto\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', user_input)
        if destinations:
            entities["destination"] = destinations[0]
    
    elif best_intent == "gifting":
        entities = {
            "recipient": None,
            "occasion": None,
            "budget": budget_patterns[0] if budget_patterns else (numbers[0] if numbers else None),
            "gift_type": None,
            "relationship": None,
            "interests": None
        }
        
        occasions = ["birthday", "anniversary", "wedding", "graduation", "christmas", "valentine", "mother's day", "father's day"]
        for occasion in occasions:
            if occasion in user_input_lower:
                entities["occasion"] = occasion.title()
                break
        
        relationships = ["mom", "mother", "dad", "father", "sister", "brother", "friend", "wife", "husband", "girlfriend", "boyfriend"]
        for rel in relationships:
            if rel in user_input_lower:
                entities["recipient"] = rel.title()
                entities["relationship"] = rel
                break
    
    elif best_intent == "cab_booking":
        entities = {
            "pickup_location": None,
            "destination": None,
            "date": date_patterns[0] if date_patterns else None,
            "time": time_patterns[0] if time_patterns else None,
            "vehicle_type": None,
            "number_of_passengers": party_size
        }
        
        from_matches = re.findall(r'\bfrom\s+([^,]+?)(?:\s+to|\s+at|$)', user_input_lower)
        to_matches = re.findall(r'\bto\s+([^,]+?)(?:\s+at|$)', user_input_lower)
        
        if from_matches:
            entities["pickup_location"] = from_matches[0].strip()
        if to_matches:
            entities["destination"] = to_matches[0].strip()
    
    else:
        # For "other" category
        entities = {
            "query": user_input,
            "topic": None,
            "keywords": None,
            "specific_request": user_input
        }
        
        topic_patterns = [
            r'how to\s+(.+?)(?:\?|$)',
            r'what is\s+(.+?)(?:\?|$)',
            r'where is\s+(.+?)(?:\?|$)',
            r'when is\s+(.+?)(?:\?|$)',
            r'update\s+(.+?)(?:\s+in|\s+on|$)',
            r'(.+?)\s+(?:procedure|process|steps|method)',
        ]
        
        for pattern in topic_patterns:
            matches = re.findall(pattern, user_input_lower)
            if matches:
                entities["topic"] = matches[0].strip()
                entities["keywords"] = matches[0].strip()
                break
        
        if not entities["topic"]:
            import string
            words = user_input.translate(str.maketrans('', '', string.punctuation)).split()
            key_words = [word for word in words if len(word) > 3 and word.lower() not in ['this', 'that', 'with', 'have', 'will', 'from', 'they', 'been', 'said', 'each', 'which', 'their']]
            if key_words:
                entities["keywords"] = " ".join(key_words[:5])
    
    # Don't clean up entities - keep None values so follow-up questions can be generated
    # Only remove empty strings, but keep None values for required field detection
    entities = {k: v for k, v in entities.items() if v != ""}
    
    return {
        "intent_category": best_intent,
        "entities": entities,
        "confidence_score": confidence
    }

def detect_available_provider():
    """Detect which AI provider is available"""
    if openai_available:
        is_available, message = OpenAIPersonalAssistant.is_available()
        if is_available:
            return "openai", message
    
    if ollama_available:
        is_available, message = OllamaPersonalAssistant.is_available()
        if is_available:
            return "ollama", message
    
    if openai_available:
        _, message = OpenAIPersonalAssistant.is_available()
        return "openai", message
    elif ollama_available:
        _, message = OllamaPersonalAssistant.is_available()
        return "ollama", message
    else:
        return None, "No AI providers available"

def generate_follow_up_questions(intent_category: str, entities: Dict[str, Any]) -> List[str]:
    """Generate follow-up questions for missing information"""
    required_fields = {
        "dining": ["cuisine", "party_size", "date", "time"],
        "travel": ["destination", "departure_date", "number_of_travelers"],
        "gifting": ["recipient", "occasion", "budget"],
        "cab_booking": ["pickup_location", "destination", "date", "time"],
        "other": []
    }
    
    if intent_category not in required_fields:
        return []
    
    missing = []
    for field in required_fields[intent_category]:
        if field not in entities or not entities[field]:
            missing.append(field)
    
    questions = []
    for field in missing[:3]:
        if field == "party_size" or field == "number_of_travelers":
            questions.append("How many people will be joining?")
        elif field == "date" or field == "departure_date":
            questions.append("What date are you planning for?")
        elif field == "time":
            questions.append("What time would you prefer?")
        elif field == "cuisine":
            questions.append("What type of cuisine are you looking for?")
        elif field == "destination":
            questions.append("Where would you like to go?")
        elif field == "pickup_location":
            questions.append("Where should we pick you up?")
        elif field == "recipient":
            questions.append("Who is this gift for?")
        elif field == "occasion":
            questions.append("What's the occasion?")
        elif field == "budget":
            questions.append("What's your budget range?")
        else:
            questions.append(f"Could you provide details about {field.replace('_', ' ')}?")
    
    return questions

def main():
    """Main Streamlit application"""
    
    # Page configuration
    st.set_page_config(
        page_title="NLParse - Smart Intent Processor",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS
    st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            padding: 2rem;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .chat-container {
            max-height: 500px;
            overflow-y: auto;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 10px;
            border: 1px solid #e9ecef;
        }
        
        .chat-message {
            padding: 1rem 1.5rem;
            margin: 1rem 0;
            border-radius: 15px;
            max-width: 75%;
            word-wrap: break-word;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .user-message {
            background: linear-gradient(135deg, #2196f3 0%, #21cbf3 100%);
            color: white;
            margin-left: auto;
            margin-right: 0;
            border-bottom-right-radius: 5px;
        }
        
        .assistant-message {
            background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
            color: white;
            margin-left: 0;
            margin-right: auto;
            border-bottom-left-radius: 5px;
        }
        
        .system-message {
            background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
            color: white;
            text-align: center;
            font-style: italic;
            margin: 0.5rem auto;
            max-width: 50%;
            border-radius: 20px;
        }
        
        .confidence-high { color: #2e7d32; font-weight: bold; }
        .confidence-medium { color: #f57c00; font-weight: bold; }
        .confidence-low { color: #d32f2f; font-weight: bold; }
        
        .json-container {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border: 2px solid #dee2e6;
            border-radius: 12px;
            padding: 1rem;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            max-height: 400px;
            overflow-y: auto;
            font-size: 0.9rem;
        }
        
        .provider-badge {
            display: inline-block;
            padding: 0.4rem 0.8rem;
            border-radius: 15px;
            font-size: 0.85rem;
            font-weight: bold;
            margin-right: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .openai-badge {
            background: linear-gradient(135deg, #00d4aa 0%, #00a085 100%);
            color: white;
        }
        
        .ollama-badge {
            background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
            color: white;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        
        .status-online { background-color: #4caf50; }
        .status-offline { background-color: #f44336; }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .loading-spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .loading-container {
            text-align: center;
            padding: 2rem;
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-radius: 15px;
            margin: 1rem 0;
        }
        
        .success-banner {
            background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            border-left: 4px solid #2e7d32;
        }
        
        .warning-banner {
            background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            border-left: 4px solid #ef6c00;
        }
    </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'current_entities' not in st.session_state:
        st.session_state.current_entities = {}
    if 'current_intent' not in st.session_state:
        st.session_state.current_intent = ""
    if 'current_confidence' not in st.session_state:
        st.session_state.current_confidence = 0.0
    if 'pending_followups' not in st.session_state:
        st.session_state.pending_followups = []
    if 'current_followup_index' not in st.session_state:
        st.session_state.current_followup_index = 0
    if 'assistant' not in st.session_state:
        st.session_state.assistant = None
    if 'provider' not in st.session_state:
        st.session_state.provider = None
    if 'conversation_state' not in st.session_state:
        st.session_state.conversation_state = "ready"
    if 'last_processed_input' not in st.session_state:
        st.session_state.last_processed_input = ""
    if 'original_request' not in st.session_state:
        st.session_state.original_request = ""

    # Helper functions for the UI
    def initialize_assistant():
        provider, message = detect_available_provider()
        
        if provider == "openai":
            try:
                st.session_state.assistant = OpenAIPersonalAssistant()
                st.session_state.provider = "openai"
                return True, "OpenAI GPT-3.5"
            except ValueError as e:
                if ollama_available:
                    provider, message = OllamaPersonalAssistant.is_available()
                    if "running with" in message:
                        st.session_state.assistant = OllamaPersonalAssistant()
                        st.session_state.provider = "ollama"
                        return True, "Ollama Llama 3.2"
                return False, str(e)
        
        elif provider == "ollama":
            st.session_state.assistant = OllamaPersonalAssistant()
            st.session_state.provider = "ollama"
            return True, "Ollama Llama 3.2"
        
        return False, message

    def get_confidence_class(score):
        if score >= 0.8:
            return "confidence-high"
        elif score >= 0.5:
            return "confidence-medium"
        else:
            return "confidence-low"

    def add_chat_message(role: str, content: str, metadata: Dict = None):
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "metadata": metadata or {}
        }
        st.session_state.chat_history.append(message)

    def process_user_input(user_input: str):
        # Prevent duplicate processing
        if user_input == st.session_state.last_processed_input and st.session_state.conversation_state == "processing":
            return
        
        st.session_state.last_processed_input = user_input
        
        # Determine if this is a follow-up answer or new request
        is_followup = bool(st.session_state.pending_followups and st.session_state.original_request)
        
        if not is_followup:
            st.session_state.current_entities = {}
            st.session_state.current_intent = ""
            st.session_state.current_confidence = 0.0
            st.session_state.pending_followups = []
            st.session_state.original_request = user_input
        
        add_chat_message("user", user_input)
        
        ai_processing_failed = False
        fallback_reason = ""
        
        try:
            if st.session_state.assistant:
                response = st.session_state.assistant.process_input(
                    user_input, 
                    st.session_state.current_entities
                )
                
                # Enhanced AI failure detection
                if (not response.intent_category or 
                    response.confidence_score == 0.0 or 
                    (response.intent_category == "other" and not response.entities)):
                    ai_processing_failed = True
                    fallback_reason = "AI returned empty result"
                else:
                    # Validate AI response has proper entity structure for non-other intents
                    if response.intent_category in ["dining", "travel", "gifting", "cab_booking"]:
                        # Check if AI response has malformed or missing entities
                        if not response.entities or not isinstance(response.entities, dict):
                            ai_processing_failed = True
                            fallback_reason = "AI returned malformed entities"
                        else:
                            # Check for suspicious entity structures (like {"entity_type": "request"})
                            if len(response.entities) == 1 and "entity_type" in response.entities:
                                ai_processing_failed = True
                                fallback_reason = "AI returned generic entity structure"
                            # Check if AI has reasonable entities for the intent
                            elif response.intent_category == "cab_booking":
                                expected_fields = ["pickup_location", "destination", "date", "time"]
                                if not any(field in response.entities for field in expected_fields):
                                    ai_processing_failed = True
                                    fallback_reason = "AI missing expected entities for cab booking"
                            elif response.intent_category == "dining":
                                expected_fields = ["cuisine", "party_size", "date", "time"]
                                if not any(field in response.entities for field in expected_fields):
                                    ai_processing_failed = True
                                    fallback_reason = "AI missing expected entities for dining"
                            elif response.intent_category == "travel":
                                expected_fields = ["destination", "departure_date", "number_of_travelers"]
                                if not any(field in response.entities for field in expected_fields):
                                    ai_processing_failed = True
                                    fallback_reason = "AI missing expected entities for travel"
                            elif response.intent_category == "gifting":
                                expected_fields = ["recipient", "occasion", "budget"]
                                if not any(field in response.entities for field in expected_fields):
                                    ai_processing_failed = True
                                    fallback_reason = "AI missing expected entities for gifting"
            else:
                ai_processing_failed = True
                fallback_reason = "No AI assistant available"
                
        except Exception as e:
            ai_processing_failed = True
            error_msg = str(e).lower()
            
            if "timeout" in error_msg or "read timed out" in error_msg:
                fallback_reason = "timeout"
            elif "certificate" in error_msg or "ssl" in error_msg:
                fallback_reason = "network"
            elif "api" in error_msg and "key" in error_msg:
                fallback_reason = "API authentication issue"
            elif "connection" in error_msg:
                fallback_reason = "service unavailable"
            else:
                fallback_reason = f"processing error"
        
        # Use fallback processing if AI failed OR always for structured intents to ensure follow-ups
        if ai_processing_failed:
            if fallback_reason not in ["timeout", "network"]:
                st.info(f"Using rule-based processing ({fallback_reason})")
            
            input_for_classification = f"{st.session_state.original_request} {user_input}" if is_followup else user_input
            classification_result = fallback_intent_classifier(input_for_classification)
            
            if st.session_state.current_entities:
                merged_entities = st.session_state.current_entities.copy()
                merged_entities.update(classification_result["entities"])
                classification_result["entities"] = merged_entities
            
            follow_up_questions = generate_follow_up_questions(
                classification_result["intent_category"],
                classification_result["entities"]
            )
            
            response = type('Response', (), {
                'intent_category': classification_result["intent_category"],
                'entities': classification_result["entities"],
                'confidence_score': classification_result["confidence_score"],
                'follow_up_questions': follow_up_questions
            })()
        else:
            # Even if AI succeeded, we need to check for follow-up questions for structured intents
            if response.intent_category in ["dining", "travel", "gifting", "cab_booking"]:
                # Merge with existing entities
                if st.session_state.current_entities:
                    merged_entities = st.session_state.current_entities.copy()
                    merged_entities.update(response.entities or {})
                    response.entities = merged_entities
                
                # Generate follow-up questions for missing required fields
                follow_up_questions = generate_follow_up_questions(
                    response.intent_category,
                    response.entities or {}
                )
                response.follow_up_questions = follow_up_questions
        
        # Update current state
        st.session_state.current_entities = response.entities.copy() if response.entities else {}
        st.session_state.current_intent = response.intent_category or ""
        st.session_state.current_confidence = response.confidence_score or 0.0
        st.session_state.pending_followups = response.follow_up_questions.copy() if response.follow_up_questions else []
        
        # Handle follow-up question progression
        if is_followup and st.session_state.pending_followups:
            # Advance to next follow-up question
            st.session_state.current_followup_index += 1
            
            # Check if we've answered all follow-up questions
            if st.session_state.current_followup_index >= len(st.session_state.pending_followups):
                st.session_state.conversation_state = "complete"
                st.session_state.current_followup_index = 0
            else:
                st.session_state.conversation_state = "waiting_followup"
        else:
            # New request or no follow-ups needed
            if st.session_state.pending_followups:
                st.session_state.conversation_state = "waiting_followup"
                st.session_state.current_followup_index = 0
            else:
                st.session_state.conversation_state = "complete"
                st.session_state.current_followup_index = 0
        
        # Generate response message
        if response.follow_up_questions:
            # Ask follow-up questions one at a time
            current_question_index = st.session_state.current_followup_index
            if current_question_index < len(response.follow_up_questions):
                chat_response = response.follow_up_questions[current_question_index]
            else:
                # All questions answered, mark as complete
                chat_response = f"Perfect! I've identified this as a {response.intent_category.replace('_', ' ').title().lower()} request and have all the details needed."
                st.session_state.conversation_state = "complete"
        else:
            intent_text = response.intent_category.replace("_", " ").title()
            if response.intent_category == "other":
                chat_response = "I understand this is a general inquiry. Let me help you with that."
            else:
                chat_response = f"Perfect! I've identified this as a {intent_text.lower()} request and have all the details needed."
        
        add_chat_message("assistant", chat_response, {
            "intent": response.intent_category,
            "confidence": response.confidence_score,
            "entities": response.entities,
            "followups": response.follow_up_questions,
            "processing_mode": "fallback" if ai_processing_failed else "ai"
        })

    def start_new_request():
        st.session_state.current_entities = {}
        st.session_state.current_intent = ""
        st.session_state.current_confidence = 0.0
        st.session_state.pending_followups = []
        st.session_state.current_followup_index = 0
        st.session_state.conversation_state = "ready"
        st.session_state.last_processed_input = ""
        st.session_state.original_request = ""
        add_chat_message("system", "New conversation started")

    def clear_chat():
        st.session_state.chat_history = []
        st.session_state.current_entities = {}
        st.session_state.current_intent = ""
        st.session_state.current_confidence = 0.0
        st.session_state.pending_followups = []
        st.session_state.current_followup_index = 0
        st.session_state.conversation_state = "ready"
        st.session_state.last_processed_input = ""
        st.session_state.original_request = ""

    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🧠 NLParse</h1>
        <h3>Smart Natural Language Intent Processor</h3>
        <p>Transform fuzzy requests into structured JSON with confidence</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize assistant
    assistant_ready, provider_info = initialize_assistant()

    # Provider status
    col1, col2 = st.columns([3, 1])

    with col1:
        if assistant_ready:
            provider_class = f"{st.session_state.provider}-badge" if st.session_state.provider else "ollama-badge"
            st.markdown(f"""
            <div class="success-banner">
                <span class="status-indicator status-online"></span>
                <span class="provider-badge {provider_class}">{provider_info}</span>
                <span>AI Engine Ready!</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="warning-banner">
                <span class="status-indicator status-offline"></span>
                <strong>AI Engine Unavailable</strong><br>
                {provider_info}<br>
                <small>Don't worry! Fallback rule-based processing is active.</small>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        new_request_disabled = st.session_state.conversation_state in ["processing"]
        
        if st.button("New Request", type="primary", disabled=new_request_disabled):
            start_new_request()
            st.rerun()
        
        if st.button("Clear Chat"):
            clear_chat()
            st.rerun()

    # Main interface
    col_chat, col_json = st.columns([2, 1])

    with col_chat:
        st.header("Conversation")
        
        # Show conversation state
        if st.session_state.conversation_state == "processing":
            st.markdown("""
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <p style="margin-top: 1rem; color: #1976d2; font-weight: bold;">Processing your request...</p>
            </div>
            """, unsafe_allow_html=True)
        elif st.session_state.conversation_state == "waiting_followup":
            follow_up_progress = f"{st.session_state.current_followup_index + 1}/{len(st.session_state.pending_followups)}" if st.session_state.pending_followups else "1/1"
            st.info(f"Question {follow_up_progress}: Please answer the follow-up question above")
        elif st.session_state.conversation_state == "complete":
            st.success("Request complete! Use 'New Request' to start over")
        
        # Display chat history
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        if st.session_state.chat_history:
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>You</strong> <small>({message['timestamp']})</small><br>
                        {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
                elif message["role"] == "assistant":
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <strong>NLParse</strong> <small>({message['timestamp']})</small><br>
                        {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
                elif message["role"] == "system":
                    st.markdown(f"""
                    <div class="chat-message system-message">
                        {message['content']} <small>({message['timestamp']})</small>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Welcome to NLParse! Start by typing your request below.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Input form
        if st.session_state.conversation_state in ["ready", "waiting_followup"]:
            with st.form("chat_input_form", clear_on_submit=True):
                if st.session_state.conversation_state == "waiting_followup":
                    question_num = st.session_state.current_followup_index + 1
                    total_questions = len(st.session_state.pending_followups)
                    placeholder = f"Answer question {question_num}/{total_questions} above..."
                else:
                    placeholder = "Example: Book a restaurant for Italian dinner for today 8 pm"
                
                user_input = st.text_area(
                    "Your message:",
                    placeholder=placeholder,
                    height=100,
                    key="user_input"
                )
                
                col_send, col_examples = st.columns([1, 1])
                
                with col_send:
                    send_disabled = st.session_state.conversation_state in ["complete", "processing"]
                    send_button = st.form_submit_button("Send", type="primary", disabled=send_disabled)
                
                with col_examples:
                    if st.session_state.conversation_state == "ready":
                        show_examples = st.form_submit_button("Examples")
                    else:
                        show_examples = False
            
            # Process input
            if send_button and user_input.strip():
                st.session_state.conversation_state = "processing"
                process_user_input(user_input.strip())
                st.rerun()
            
            # Show examples
            if show_examples and st.session_state.conversation_state == "ready":
                st.markdown("### Example Requests")
                examples = [
                    "Book a restaurant for Italian dinner for today 8 pm",
                    "Plan a trip to Paris for 3 people next month",
                    "Find a gift for my mom's birthday, budget around $100",
                    "Book a cab from downtown to airport tomorrow 3 PM",
                    "How to update address in Aadhar card online"
                ]
                
                for example in examples:
                    if st.button(f"{example}", key=f"ex_{hash(example)}"):
                        st.session_state.conversation_state = "processing"
                        process_user_input(example)
                        st.rerun()
        
        else:
            st.info("Conversation complete! Click 'New Request' to start over.")

    with col_json:
        st.header("Current Request")
        
        # Show current conversation state
        if st.session_state.conversation_state == "ready":
            st.info("Ready for new request")
        elif st.session_state.conversation_state == "processing":
            st.warning("Processing...")
        elif st.session_state.conversation_state == "waiting_followup":
            st.warning("Waiting for follow-up answers")
        elif st.session_state.conversation_state == "complete":
            st.success("Request complete")
        
        # Intent and confidence
        if st.session_state.current_intent and st.session_state.conversation_state != "ready":
            confidence_class = get_confidence_class(st.session_state.current_confidence)
            st.markdown(f"""
            **Intent:** {st.session_state.current_intent.replace('_', ' ').title()}<br>
            **Confidence:** <span class="{confidence_class}">{st.session_state.current_confidence:.1%}</span>
            """, unsafe_allow_html=True)
        
        # Current JSON state
        st.subheader("Building JSON")
        
        if st.session_state.current_entities or st.session_state.conversation_state != "ready":
            # Clean up entities for display - remove None values but keep during processing
            clean_entities = {k: v for k, v in st.session_state.get('current_entities', {}).items() if v is not None and v != ""}
            
            # Show current follow-up question being asked
            current_missing_info = []
            if st.session_state.conversation_state == "waiting_followup" and st.session_state.pending_followups:
                current_index = st.session_state.current_followup_index
                if current_index < len(st.session_state.pending_followups):
                    current_missing_info = [st.session_state.pending_followups[current_index]]
            
            current_json = {
                "intent_category": st.session_state.get('current_intent', ''),
                "entities": clean_entities,
                "confidence_score": st.session_state.get('current_confidence', 0.0),
                "status": "complete" if st.session_state.conversation_state == "complete" else ("pending" if st.session_state.get('pending_followups', []) else "processing"),
                "missing_info": current_missing_info,
                "followup_progress": f"{st.session_state.current_followup_index}/{len(st.session_state.pending_followups)}" if st.session_state.pending_followups else "0/0",
                "timestamp": datetime.now().isoformat()
            }
            
            st.markdown('<div class="json-container">', unsafe_allow_html=True)
            st.json(current_json)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Export functionality
            if st.session_state.conversation_state == "complete" and clean_entities:
                st.subheader("Export")
                
                st.download_button(
                    "Download JSON",
                    data=json.dumps(current_json, indent=2),
                    file_name=f"nlparse_request_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                
                if st.session_state.chat_history:
                    chat_export = {
                        "chat_history": st.session_state.chat_history,
                        "final_result": current_json,
                        "exported_at": datetime.now().isoformat(),
                        "app_version": "NLParse v1.0"
                    }
                    
                    st.download_button(
                        "Download Chat",
                        data=json.dumps(chat_export, indent=2),
                        file_name=f"nlparse_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
        else:
            st.info("JSON will appear here as you make requests")

    # Sidebar
    with st.sidebar:
        st.header("How NLParse Works")
        
        st.markdown("""
        **1. Intent Classification**
        - Dining, Travel, Gifting, Cab Booking, Other
        
        **2. Entity Extraction**  
        - Extracts key details from your request
        
        **3. Smart Follow-ups**
        - Asks for missing required information
        
        **4. Progressive Building**
        - JSON structure builds as you provide answers
        
        **5. Complete Output**
        - Final structured JSON ready for processing
        """)
        
        st.markdown("---")
        st.subheader("Supported Categories")
        
        categories_info = {
            "dining": {
                "required": ["cuisine", "party_size", "date", "time"],
                "optional": ["location", "budget", "dietary_restrictions"]
            },
            "travel": {
                "required": ["destination", "departure_date", "number_of_travelers"],
                "optional": ["return_date", "budget", "accommodation_type"]
            },
            "gifting": {
                "required": ["recipient", "occasion", "budget"],
                "optional": ["gift_type", "relationship", "interests"]
            },
            "cab_booking": {
                "required": ["pickup_location", "destination", "date", "time"],
                "optional": ["vehicle_type", "number_of_passengers"]
            },
            "other": {
                "required": [],
                "optional": ["topic", "keywords", "specific_request"]
            }
        }
        
        for category, details in categories_info.items():
            with st.expander(f"{category.title()}"):
                st.write("**Required:**", ", ".join(details.get("required", [])))
                st.write("**Optional:**", ", ".join(details.get("optional", [])))

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p><strong>NLParse v1.0</strong> - Smart Natural Language Intent Processor</p>
        <p>Built with Streamlit | Supports OpenAI GPT & Ollama Local Models</p>
    </div>
    """, unsafe_allow_html=True)

# Only run when executed as a script
if __name__ == "__main__":
    main() 