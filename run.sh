#!/bin/bash

echo "🚀 Starting Intent Parser..."

# Kill any existing streamlit processes on these ports
lsof -ti:8505 | xargs kill -9 2>/dev/null
lsof -ti:8506 | xargs kill -9 2>/dev/null

# Try different Python versions to find the one with streamlit
if /usr/bin/python3 -c "import streamlit" 2>/dev/null; then
    echo "✓ Using Python 3.9 with streamlit"
    /usr/bin/python3 -m streamlit run chat_app.py --server.port 8505
elif python3 -c "import streamlit" 2>/dev/null; then
    echo "✓ Using system python3 with streamlit"
    python3 -m streamlit run chat_app.py --server.port 8505
else
    echo "❌ Streamlit not found. Installing..."
    /usr/bin/python3 -m pip install --user streamlit
    echo "✓ Installed. Starting app..."
    /usr/bin/python3 -m streamlit run chat_app.py --server.port 8505
fi 