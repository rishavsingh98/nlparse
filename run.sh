#!/bin/bash

echo "🚀 Starting NLParse Intent Parser..."

# Function to kill processes on port (works on Linux and macOS)
kill_port() {
    local port=$1
    if command -v lsof >/dev/null 2>&1; then
        # macOS and some Linux systems
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
    elif command -v fuser >/dev/null 2>&1; then
        # Most Linux systems
        fuser -k $port/tcp 2>/dev/null || true
    elif command -v ss >/dev/null 2>&1; then
        # Modern Linux systems
        local pid=$(ss -tlnp | grep :$port | awk '{print $6}' | cut -d, -f2 | cut -d= -f2)
        [ -n "$pid" ] && kill -9 $pid 2>/dev/null || true
    fi
}

# Clean up existing processes
echo "🧹 Cleaning up existing processes..."
kill_port 8505
kill_port 8506

# Function to check if streamlit is available
check_streamlit() {
    local python_cmd=$1
    $python_cmd -c "import streamlit" 2>/dev/null
}

# Function to install streamlit
install_streamlit() {
    local python_cmd=$1
    echo "📦 Installing streamlit..."
    if $python_cmd -m pip install --user streamlit; then
        echo "✅ Streamlit installed successfully"
        return 0
    else
        echo "❌ Failed to install streamlit"
        return 1
    fi
}

# Function to start the app
start_app() {
    local python_cmd=$1
    local version_name=$2
    echo "Using $version_name with streamlit"
    echo "App will be available at: http://localhost:8505"
    echo "Press Ctrl+C to stop the server"
    $python_cmd -m streamlit run chat_app.py --server.port 8505
}

# Try different Python commands in order of preference
PYTHON_COMMANDS=(
    "/usr/bin/python3:System Python 3"
    "python3:Python 3"
    "python:Python"
)

for cmd_info in "${PYTHON_COMMANDS[@]}"; do
    IFS=':' read -r python_cmd version_name <<< "$cmd_info"
    
    if command -v $python_cmd >/dev/null 2>&1; then
        echo "🔍 Checking $version_name ($python_cmd)..."
        
        if check_streamlit $python_cmd; then
            start_app $python_cmd "$version_name"
            exit 0
        else
            echo "⚠️  Streamlit not found in $version_name"
            if install_streamlit $python_cmd; then
                start_app $python_cmd "$version_name"
                exit 0
            fi
        fi
    fi
done

# If we get here, nothing worked
echo "Could not find a suitable Python installation with streamlit"
echo "Please ensure Python 3.9+ is installed and try:"
echo "pip install streamlit"
echo "python3 -m streamlit run chat_app.py --server.port 8505"
exit 1 