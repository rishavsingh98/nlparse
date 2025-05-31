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
- Git

### Platform-Specific Python Installation

#### 🪟 **Windows**

1. **Download Python from [python.org](https://www.python.org/downloads/)**

   - Make sure to check "Add Python to PATH" during installation
   - Or install via Microsoft Store: `python3`

2. **Alternative - Using Chocolatey**

```powershell
# Install Chocolatey first, then:
choco install python git
```

3. **Alternative - Using winget**

```powershell
winget install Python.Python.3.11
winget install Git.Git
```

#### 🐧 **Linux**

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install python3 python3-pip git
```

**CentOS/RHEL/Fedora:**

```bash
# CentOS/RHEL
sudo yum install python3 python3-pip git

# Fedora
sudo dnf install python3 python3-pip git
```

**Arch Linux:**

```bash
sudo pacman -S python python-pip git
```

#### 🍎 **macOS**

**Using Homebrew (Recommended):**

```bash
brew install python@3.11 git
```

**Using MacPorts:**

```bash
sudo port install python311 git
```

**Direct Download:**
Download from [python.org](https://www.python.org/downloads/macos/)

### Quick Start

#### 🪟 **Windows Setup**

1. **Clone the repository**

```powershell
git clone https://github.com/rishavsingh98/nlparse.git
cd nlparse
```

2. **Create virtual environment (recommended)**

```powershell
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**

```powershell
pip install -r requirements.txt
```

4. **Run the application**

```powershell
# Method 1: Use the provided batch script
.\run.bat

# Method 2: Direct Python
python -m streamlit run chat_app.py --server.port 8505

# Method 3: If you have multiple Python versions
py -3 -m streamlit run chat_app.py --server.port 8505
```

5. **Open your browser**
   Navigate to `http://localhost:8505`

#### 🐧 **Linux Setup**

1. **Clone the repository**

```bash
git clone https://github.com/rishavsingh98/nlparse.git
cd nlparse
```

2. **Create virtual environment (recommended)**

```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Run the application**

```bash
# Method 1: Use the provided script
chmod +x run.sh
./run.sh

# Method 2: Direct Python
python3 -m streamlit run chat_app.py --server.port 8505
```

5. **Open your browser**
   Navigate to `http://localhost:8505`

#### 🍎 **macOS Setup**

1. **Clone the repository**

```bash
git clone https://github.com/rishavsingh98/nlparse.git
cd nlparse
```

2. **Create virtual environment (recommended)**

```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Run the application**

```bash
# Method 1: Use the provided script
./run.sh

# Method 2: Direct Python
python3 -m streamlit run chat_app.py --server.port 8505

# Method 3: Specific Python path (if issues)
/usr/bin/python3 -m streamlit run chat_app.py --server.port 8505
```

5. **Open your browser**
   Navigate to `http://localhost:8505`

### Optional AI Setup

#### OpenAI Setup (All Platforms)

**Windows (PowerShell):**

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
# For permanent setting:
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "your_api_key_here", "User")
```

**Windows (Command Prompt):**

```cmd
set OPENAI_API_KEY=your_api_key_here
```

**Linux/macOS:**

```bash
export OPENAI_API_KEY="your_api_key_here"

# For permanent setting, add to ~/.bashrc or ~/.zshrc:
echo 'export OPENAI_API_KEY="your_api_key_here"' >> ~/.bashrc
```

Get your API key from [OpenAI Platform](https://platform.openai.com/)

#### Ollama Setup (Local & Free)

**🪟 Windows:**

```powershell
# Download and install from https://ollama.com/download/windows
# Or using winget:
winget install Ollama.Ollama

# Start Ollama (runs as service automatically)
# Download the model
ollama pull llama3.2:3b
```

**🐧 Linux:**

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start the service
sudo systemctl start ollama
sudo systemctl enable ollama

# Download the model
ollama pull llama3.2:3b
```

**🍎 macOS:**

```bash
# Using Homebrew
brew install ollama
brew services start ollama

# Or download from https://ollama.com/download/mac

# Download the model
ollama pull llama3.2:3b
```

### Troubleshooting

#### Port Issues

**Windows:**

```powershell
# Check what's using the port
netstat -ano | findstr :8505

# Kill process by PID
taskkill /PID <PID> /F

# Use different port
python -m streamlit run chat_app.py --server.port 8506
```

**Linux/macOS:**

```bash
# Check what's using the port
lsof -ti:8505

# Kill processes on port
lsof -ti:8505 | xargs kill -9

# Use different port
python3 -m streamlit run chat_app.py --server.port 8506
```

#### Python Version Issues

**Windows:**

```powershell
# Check Python version
python --version
py --list

# Use specific version
py -3.9 -m streamlit run chat_app.py --server.port 8505
```

**Linux:**

```bash
# Check available Python versions
ls /usr/bin/python*
python3 --version

# Use specific version
python3.9 -m streamlit run chat_app.py --server.port 8505
```

**macOS:**

```bash
# Check Python versions
python3 --version
/usr/bin/python3 --version

# Use system Python if Homebrew Python has issues
/usr/bin/python3 -m streamlit run chat_app.py --server.port 8505
```

#### Permission Issues

**Linux/macOS:**

```bash
# Make run script executable
chmod +x run.sh

# If pip permission issues
pip install --user -r requirements.txt
```

**Windows:**

```powershell
# If execution policy issues
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# If pip permission issues
pip install --user -r requirements.txt
```

#### SSL/Certificate Errors

These are handled gracefully and won't break the app. The fallback processing still works perfectly on all platforms.

#### Virtual Environment Activation

**Windows:**

```powershell
# PowerShell
venv\Scripts\Activate.ps1

# Command Prompt
venv\Scripts\activate.bat
```

**Linux/macOS:**

```bash
source venv/bin/activate
```

That's it! The app works out of the box with rule-based processing on all platforms.

## File Structure

```
nlparse/
├── chat_app.py           # Main Streamlit application
├── assistant_openai.py   # OpenAI integration
├── assistant_ollama.py   # Ollama integration
├── run.sh               # Unix/Linux/macOS startup script
├── run.bat              # Windows startup script
├── requirements.txt     # Dependencies
├── .gitignore          # Git ignore rules
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
