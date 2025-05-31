# NLParse - Smart Natural Language Intent Processor

A conversational AI assistant that transforms messy human requests into clean, structured JSON data. Think of it as a smart parser that actually understands what people are asking for.

## What does this thing do?

Ever tried to build a system that needs to understand user requests like "book me a table for Italian food tonight" or "find a gift for my mom's birthday"? That's exactly what NLParse handles. It takes natural language input and spits out properly structured JSON with intent classification, entity extraction, and confidence scoring.

The best part? It actually follows up with questions when it needs more info, just like a human would.

## Features

### 🧠 Smart Intent Classification

Automatically categorizes requests into 5 main types:

- **Dining**: Restaurant bookings, food orders, table reservations
- **Travel**: Trip planning, hotel bookings, flight searches
- **Gifting**: Present suggestions, occasion-based shopping
- **Cab Booking**: Ride requests, transportation planning
- **Other**: Everything else (with web search support)

### 💬 Conversational Follow-ups

Instead of just failing when info is missing, NLParse asks follow-up questions:

```
User: "Book a restaurant"
NLParse: "What type of cuisine are you looking for?"
User: "Italian"
NLParse: "How many people will be joining?"
```

### 📊 Progressive JSON Building

Watch your JSON structure build in real-time as the conversation progresses. No more guessing what data you'll get back.

### 🔍 Web Search Integration

For requests that don't fit the main categories, NLParse can search the web and provide relevant information with fallback suggestions.

### 🤖 Multiple AI Backends

- **OpenAI GPT-3.5**: Most accurate results (requires API key)
- **Ollama**: Local processing with Llama 3.2 (free, private)
- **Rule-based Fallback**: Always works, even without AI setup

## Intent Coverage

### Dining Intent

**Extracts**: cuisine, party size, date, time, budget, location, dietary restrictions

Examples:

- "Book an Italian restaurant for 4 people tonight at 8pm"
- "Find a vegetarian place for lunch tomorrow"
- "Reserve a table for anniversary dinner, budget around $200"

### Travel Intent

**Extracts**: destination, departure date, travelers, budget, accommodation type

Examples:

- "Plan a trip to Paris for 3 people next month"
- "Book a hotel in Tokyo for business travel"
- "Find flights to New York for weekend getaway"

### Gifting Intent

**Extracts**: recipient, occasion, budget, gift type, relationship

Examples:

- "Find a birthday gift for my sister, budget $50"
- "What should I get for my dad's retirement?"
- "Need anniversary present ideas under $100"

### Cab Booking Intent

**Extracts**: pickup location, destination, date, time, vehicle type

Examples:

- "Book a cab from downtown to airport tomorrow 3pm"
- "Need an Uber to the hotel tonight"
- "Schedule ride to the conference center"

### Other Intent + Web Search

For general queries, NLParse performs web searches and provides contextual information:

Examples:

- "How to update address in Aadhaar card"
- "Apply for passport online procedure"
- "Income tax filing deadline 2024"

## Local Setup

### Prerequisites

- Python 3.9 or higher
- Git (obviously)

### Quick Start

1. **Clone and enter the project**

```bash
git clone <your-repo-url>
cd ChatBot
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Run the app**

```bash
# Easy way - use the provided script
./run.sh

# Manual way
/usr/bin/python3 -m streamlit run chat_app.py --server.port 8505
```

4. **Open your browser**
   Navigate to `http://localhost:8505`

That's it! The app works out of the box with rule-based processing.

### Optional AI Setup

Want better accuracy? Set up an AI backend:

#### Option 1: OpenAI (Recommended)

```bash
export OPENAI_API_KEY="your_api_key_here"
```

Get your API key from [OpenAI Platform](https://platform.openai.com/)

#### Option 2: Ollama (Local & Free)

```bash
# Install Ollama
brew install ollama

# Start the service
brew services start ollama

# Download the model (this takes a while)
ollama pull llama3.2:3b
```

### Troubleshooting

**Port already in use?**

```bash
# Kill existing processes
lsof -ti:8505 | xargs kill -9

# Or use a different port
/usr/bin/python3 -m streamlit run chat_app.py --server.port 8506
```

**SSL/Certificate errors?**
These are handled gracefully and won't break the app. The fallback processing still works perfectly.

**Python version issues?**
The `run.sh` script automatically detects the right Python version. If manual setup fails, try:

```bash
/usr/bin/python3 -m streamlit run chat_app.py --server.port 8505
```

## File Structure

```
ChatBot/
├── chat_app.py           # Main Streamlit application
├── assistant_openai.py   # OpenAI integration
├── assistant_ollama.py   # Ollama integration
├── run.sh               # Smart startup script
├── requirements.txt     # Dependencies
├── env.example         # Environment variables template
└── README.md           # You're reading this
```

## API Response Format

Here's what you get back:

```json
{
  "intent_category": "dining",
  "entities": {
    "cuisine": "Italian",
    "party_size": "4",
    "date": "tonight",
    "time": "8pm"
  },
  "confidence_score": 0.85,
  "status": "complete",
  "missing_info": [],
  "timestamp": "2024-05-31T15:30:00"
}
```

## Development Notes

- Built with Streamlit for the UI (because it's fast to prototype)
- Fallback rule-based processing means it always works
- State management handles conversation flow properly
- Export functionality for integration with other systems
- No database needed - it's stateless by design

## Known Limitations

- Web search is basic (no advanced filtering)
- Entity extraction could be more sophisticated for edge cases
- Currently English-only (though adding languages wouldn't be too hard)

## Contributing

Found a bug? Want to add a new intent category? Pull requests welcome! The code is pretty straightforward to follow.

## License

MIT License - do whatever you want with it.

---

**Built with ❤️ and probably too much coffee**

_P.S. - If you're using this in production, maybe don't rely solely on the rule-based fallback. The AI backends are much more reliable for real-world use cases._
