# NLParse - Smart Natural Language Intent Processor

A conversational AI assistant that transforms messy human requests into clean, structured JSON data. Think of it as a smart parser that actually understands what people are asking for.

> **Quick Start:** Want the best experience? [Set up Ollama (free)](#ollama-setup) for local AI processing, or just [run it immediately](#quick-start-without-any-ai-setup) with rule-based processing. No OpenAI API key required!

---

## What does this thing do?

Ever tried to build a system that needs to understand user requests like "book me a table for Italian food tonight" or "find a gift for my mom's birthday"? That's exactly what NLParse handles. It takes natural language input and returns structured JSON with:

- Intent classification
- Entity extraction
- Confidence scoring
- Conversational follow-ups (when needed)

---

## Features

### Smart Intent Classification

Automatically categorizes requests into 5 main types:

- **Dining**: Restaurant bookings, food orders, table reservations
- **Travel**: Trip planning, hotel bookings, flight searches
- **Gifting**: Present suggestions, occasion-based shopping
- **Cab Booking**: Ride requests, transportation planning
- **Other**: Everything else (with web search support)

### Conversational Follow-ups

```text
User: "Book a restaurant"
NLParse: "What type of cuisine are you looking for?"
User: "Italian"
NLParse: "How many people will be joining?"
```

### Progressive JSON Building

Watch your structured JSON build in real-time as the conversation unfolds.

### Web Search Integration

**Automatic Web Intelligence for General Queries**

When NLParse encounters requests outside its main categories (dining, travel, gifting, cab booking), it automatically:

1. **Performs intelligent web searches** using multiple providers (DuckDuckGo API primary, with fallbacks)
2. **Retrieves and analyzes top results** from the web
3. **Uses AI to synthesize information** into helpful, conversational responses
4. **Handles SSL/certificate errors gracefully** with automatic fallback to mock data

This means you can ask about anything - government procedures, how-to guides, general information - and get helpful responses!

### Multiple AI Backends

- **Ollama (Recommended)**: Local, free, private, accurate (Llama 3.2)
- **OpenAI GPT-3.5**: Premium accuracy, requires API key (\$)
- **Rule-based**: Basic keyword matcher (no setup needed)

NLParse automatically picks the best available backend.

---

## Intent Coverage

### Dining Intent

**Extracts:** cuisine, party size, date, time, budget, location, dietary restrictions

### Travel Intent

**Extracts:** destination, departure date, travelers, budget, accommodation type

### Gifting Intent

**Extracts:** recipient, occasion, budget, gift type, relationship

### Cab Booking Intent

**Extracts:** pickup location, destination, date, time, vehicle type

### Other Intent + Web Search

**AI-Powered Web Search for Any Query**

NLParse intelligently handles general knowledge questions by:

- Searching the web for relevant information
- Using AI to synthesize and summarize results
- Providing step-by-step instructions when found
- Including source references for credibility

Examples:

- "How to update address in Aadhaar card" → Step-by-step UIDAI process
- "Apply for passport online procedure" → Complete application guide
- "Income tax filing deadline 2024" → Current deadlines and requirements
- "Reset Windows password" → Technical troubleshooting steps
- "Python installation on Mac" → Platform-specific instructions
- "Latest AI trends 2024" → Summarized industry insights

**How it works:** The AI classifies these as "other" intent, triggers web search, and generates comprehensive responses based on current web information.

---

## Local Setup

### Prerequisites

- Python 3.9+
- Git
- Internet connection (for web search features)

**Note:** All required Python packages including web search dependencies (`requests`, `certifi`, `urllib3`) are automatically installed via `requirements.txt`

### Quick Platform Instructions

#### Windows

```powershell
git clone https://github.com/rishavsingh98/nlparse.git
cd nlparse
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m streamlit run chat_app.py --server.port 8505
```

Open your browser: [http://localhost:8505](http://localhost:8505)

#### Linux/macOS

```bash
git clone https://github.com/rishavsingh98/nlparse.git
cd nlparse
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m streamlit run chat_app.py --server.port 8505
```

Open your browser: [http://localhost:8505](http://localhost:8505)

---

## AI Backend Configuration

### Preference Order:

1. **OpenAI** - Requires `OPENAI_API_KEY`
2. **Ollama (local)** - Pull `llama3.2:3b`
3. **Rule-based fallback** - No setup required

### Ollama Setup (Recommended)

- Download from [https://ollama.com/download](https://ollama.com/download)
- Run `ollama pull llama3.2:3b`
- Test: `ollama run llama3.2:3b "Hello"`

### OpenAI Setup

Set `OPENAI_API_KEY` as an environment variable.

```bash
export OPENAI_API_KEY="your_api_key"
```

---

## Quick Start Without Any AI Setup

Run with rule-based fallback (no config required):

```bash
./run.sh        # Linux/macOS
.\run.bat       # Windows
```

---

## Troubleshooting

### Common Issues

- **Port already in use?**

  - Use another port: `--server.port 8506`
  - Kill processes on port: `lsof -ti:8505 | xargs kill -9` (Linux/macOS)

- **Virtualenv not activating?**

  - Linux/macOS: `source venv/bin/activate`
  - Windows: `venv\Scripts\Activate.ps1`

- **Python version issues?**
  - Check version: `python --version` or `python3 --version`
  - Use specific version: `python3.9 -m streamlit run chat_app.py`

### SSL/Certificate Errors

**For Web Search Feature:**

If you encounter SSL certificate errors during web searches, the app automatically:

1. Falls back to mock search data for testing
2. Continues to work with reduced web search capability
3. Still provides helpful responses based on patterns

To fix SSL issues:

**Windows:**

```powershell
# Update certificates
pip install --upgrade certifi
```

**Linux:**

```bash
# Install ca-certificates
sudo apt-get update && sudo apt-get install ca-certificates
# or for RedHat-based:
sudo yum install ca-certificates
```

**macOS:**

```bash
# Update certificates via Homebrew
brew install ca-certificates
# or
pip install --upgrade certifi
```

### Ollama Issues

- **Check if running:**

  ```bash
  curl http://localhost:11434/api/tags
  ```

- **Restart Ollama:**

  - Windows: `Restart-Service -Name "OllamaService"`
  - Linux: `sudo systemctl restart ollama`
  - macOS: `brew services restart ollama`

- **Model issues:**

  ```bash
  # Re-download model
  ollama rm llama3.2:3b
  ollama pull llama3.2:3b

  # List models
  ollama list
  ```

- **Performance notes:**
  - Needs ~8GB RAM for good performance
  - First response is slower (model loading)
  - Try smaller model if needed: `ollama pull llama3.2:1b`

---

## File Structure

```
nlparse/
├── chat_app.py           # Main Streamlit app
├── assistant_openai.py   # OpenAI integration
├── assistant_ollama.py   # Ollama integration
├── web_search.py         # Web search module
├── run.sh                # Unix/macOS startup
├── run.bat               # Windows startup
├── requirements.txt      # Dependencies
├── .gitignore            # Ignore rules
└── README.md             # This file
```

---

## API Response Format

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

---

## Development Notes

- Built with **Streamlit** for fast UI prototyping
- Works out of the box with rule-based processing
- Stateless by design - no database needed

---

## Known Limitations

- Web search support is basic (DuckDuckGo API with fallbacks)
- Advanced NLP still limited to AI modes
- English-only support currently

---

## Contributing

Found a bug or have a feature request? Pull requests welcome!

---

**Built with ❤️ and probably too much coffee**

_P.S. If you're using this in production, prefer Ollama or OpenAI over rule-based mode._
