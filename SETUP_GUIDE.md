# AI Research Assistant Setup Guide

This guide provides detailed instructions for setting up the AI Research Assistant project, with special attention to common issues and their solutions.

## Environment Setup

### Setting Up the .env File

The `.env` file contains important configuration variables for the application. It's crucial that this file is created with the correct encoding to avoid issues.

#### Creating the .env File with UTF-8 Encoding

**Windows:**
1. Open Notepad
2. Copy the content from `.env.sample`
3. Click "File" > "Save As"
4. Choose the project root directory
5. Name the file `.env` (including the dot)
6. In the "Encoding" dropdown at the bottom, select "UTF-8"
7. Click "Save"

**macOS/Linux:**
```bash
# Copy the sample file
cp .env.sample .env

# Edit with a text editor that supports UTF-8
nano .env
# or
vim .env
```

#### Required Environment Variables

Your `.env` file should contain the following variables:

```
# API Keys
TAVILY_API_KEY=your_tavily_api_key_here

# LangChain Configuration (optional for tracing)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langchain_api_key_here
LANGCHAIN_PROJECT=default
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com

# LLM Configuration
LOCAL_LLM=deepseek-r1:14b
TEMPERATURE=0.1
MAX_TOKENS=1024
NUM_THREADS=4
```

### Virtual Environment Setup

It's recommended to use a virtual environment to avoid dependency conflicts:

**Windows:**
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -e .
pip install langgraph-cli[inmem]
```

**macOS/Linux:**
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -e .
pip install langgraph-cli[inmem]
```

## Ollama Setup

### Installing Ollama

1. Download Ollama from [https://ollama.com/download](https://ollama.com/download)
2. Install following the instructions for your operating system

### Pulling Required Models

After installing Ollama, pull the required model:

```bash
ollama pull deepseek-r1:14b
```

You can verify the model is installed with:

```bash
ollama list
```

## Running the Application

### Starting the LangGraph Server

```bash
# Default port (2024)
langgraph dev

# Alternative port if 2024 is in use
langgraph dev --port 3000
```

### Accessing the Application

When the server is running, you can access:
- API documentation: http://127.0.0.1:2024/docs (or your custom port)
- LangGraph Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024 (adjust URL for custom port)

## Troubleshooting

### Common Issues and Solutions

#### "Module not found" Errors

**Problem:** Python cannot find required modules.
**Solution:** 
- Ensure you've activated the virtual environment
- Install the project in development mode: `pip install -e .`
- Install all dependencies: `pip install -r requirements.txt`

#### LangGraph Server Won't Start

**Problem:** The server fails to start or crashes immediately.
**Solution:**
- Check if another process is using the same port
- Try a different port: `langgraph dev --port 3000`
- Look for error messages in the console output

#### Ollama Connection Issues

**Problem:** The application cannot connect to Ollama.
**Solution:**
- Verify Ollama is running: `ollama list`
- Check if the model is downloaded: `ollama pull deepseek-r1:14b`
- Restart Ollama service

#### Environment Variable Issues

**Problem:** The application cannot read environment variables.
**Solution:**
- Ensure `.env` file is in the project root directory
- Verify the file is saved with UTF-8 encoding
- Check variable names match those expected by the application

#### Windows-Specific Issues

**Problem:** File path or encoding issues on Windows.
**Solution:**
- Use forward slashes (/) in configuration paths
- Ensure files are saved with UTF-8 encoding
- Run PowerShell as administrator if needed 