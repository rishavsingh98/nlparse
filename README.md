# NLParse - Smart Natural Language Intent Processor

A conversational AI assistant that transforms messy human requests into clean, structured JSON data. Think of it as a smart parser that actually understands what people are asking for.

> **Quick Start:** Want the best experience? [Set up Ollama (free)](#ollama-setup) for local AI processing, or just [run it immediately](#quick-start-without-any-ai-setup) with rule-based processing. No OpenAI API key required!

---

## What does this thing do?

Ever tried to build a system that needs to understand user requests like "book me a table for Italian food tonight" or "find a gift for my mom's birthday"? That's exactly what NLParse handles. It takes natural language input and returns structured JSON with:

* Intent classification
* Entity extraction
* Confidence scoring
* Conversational follow-ups (when needed)

---

## Features

### Smart Intent Classification

Automatically categorizes requests into 5 main types:

* **Dining**: Restaurant bookings, food orders, table reservations
* **Travel**: Trip planning, hotel bookings, flight searches
* **Gifting**: Present suggestions, occasion-based shopping
* **Cab Booking**: Ride requests, transportation planning
* **Other**: Everything else (with web search support)

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

Fallback to web search for generic or unsupported queries.

### Multiple AI Backends

* **Ollama (Recommended)**: Local, free, private, accurate (Llama 3.2)
* **OpenAI GPT-3.5**: Premium accuracy, requires API key (\$)
* **Rule-based**: Basic keyword matcher (no setup needed)

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

Handles general queries with contextual search.

---

## Local Setup

### Prerequisites

* Python 3.9+
* Git

### Quick Platform Instructions

```powershell
git clone https://github.com/rishavsingh98/nlparse.git
cd nlparse
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m streamlit run chat_app.py --server.port 8505
```

Open your browser: [http://localhost:8505](http://localhost:8505)

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

* Download from [https://ollama.com/download](https://ollama.com/download)
* Run `ollama pull llama3.2:3b`
* Test: `ollama run llama3.2:3b "Hello"`

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

* **Port already in use?**

  * Use another port: `--server.port 8506`
* **Virtualenv not activating?**

  * Linux/macOS: `source venv/bin/activate`
  * Windows: `venv\Scripts\Activate.ps1`

### Ollama Issues

* Restart Ollama:

  * Windows: `Restart-Service -Name "OllamaService"`
  * Linux: `sudo systemctl restart ollama`
  * macOS: `brew services restart ollama`

---

## File Structure

```
nlparse/
├── chat_app.py           # Main Streamlit app
├── assistant_openai.py   # OpenAI integration
├── assistant_ollama.py   # Ollama integration
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

* Built with **Streamlit** for fast UI prototyping
* Works out of the box with rule-based processing
* Stateless by design - no database needed

---

## Known Limitations

* Web search support is basic
* Advanced NLP still limited to AI modes

---

## Contributing

Found a bug or have a feature request? Pull requests welcome!

---

**Built with ❤️ and probably too much coffee**

*P.S. If you're using this in production, prefer Ollama or OpenAI over rule-based mode.*
