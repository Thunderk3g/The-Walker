# The-Walker: AI Research Assistant

The-Walker is a lightweight, efficient web research assistant optimized for resource-constrained environments. It leverages local LLMs hosted by [Ollama](https://ollama.com/search) with GGUF quantization to provide powerful research capabilities even on modest hardware.

## 🚀 Key Features

- **Resource-Optimized**: Designed to run efficiently on laptops and desktops with limited GPU resources
- **Local LLM Integration**: Uses quantized models via Ollama for privacy and reduced resource usage
- **GGUF Quantization Support**: Optimized to work with GGUF quantized models for better performance
- **Iterative Research Process**: Conducts multi-step research with reflection and refinement
- **Modern React Frontend**: Clean, responsive UI for easy interaction
- **Fully Local Operation**: All processing happens on your machine for privacy and control

## 📊 Performance Optimization

The-Walker is specifically designed to work efficiently with:

- **DeepSeek R1 14B**: Optimized as the default model for balanced performance and quality
- **Reduced Thread Count**: Minimizes parallel operations to avoid overwhelming system resources
- **Memory-Efficient Processing**: Carefully manages memory usage during research iterations
- **Adaptive Resource Usage**: Scales resource utilization based on available system capacity

## 🖥️ System Requirements

**Minimum:**
- CPU: 4-core processor
- RAM: 8GB
- Storage: 20GB free space
- GPU: Not required, but integrated graphics helpful

**Recommended:**
- CPU: 6-core processor or better
- RAM: 16GB
- Storage: 30GB free space
- GPU: Entry-level dedicated GPU (4GB VRAM)

## 🚀 Quickstart

### Windows

1. Download the Ollama app for Windows [here](https://ollama.com/download).

2. Pull the optimized DeepSeek R1 14B model:
```powershell
ollama pull deepseek-r1:14b
```

3. For free web search (up to 1000 requests), [sign up for Tavily](https://tavily.com/). 

4. Set the `TAVILY_API_KEY` environment variable in Windows (via System Properties or PowerShell). Restart your terminal after setting it.

5. Create a virtual environment:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

6. Clone the repository and launch the assistant:
```powershell
git clone https://github.com/Thunderk3g/The-Walker.git
cd The-Walker
pip install -e .
pip install langgraph-cli[inmem]
langgraph dev
```

7. Start the React frontend:
```powershell
cd frontend/the-walker-ui
npm install
npm start
```

### Mac/Linux

1. Download the Ollama app for your platform [here](https://ollama.com/download).

2. Pull the optimized DeepSeek R1 14B model:
```bash
ollama pull deepseek-r1:14b
```

3. For free web search (up to 1000 requests), [sign up for Tavily](https://tavily.com/). 

4. Set the `TAVILY_API_KEY` environment variable:
```bash
export TAVILY_API_KEY=<your_tavily_api_key>
```

5. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

6. Clone the repository and launch the assistant:
```bash
git clone https://github.com/Thunderk3g/The-Walker.git
cd The-Walker
pip install -e .
pip install langgraph-cli[inmem]
langgraph dev
```

7. Start the React frontend:
```bash
cd frontend/the-walker-ui
npm install
npm start
```

## 🧠 How it works

The-Walker uses an optimized research workflow:

1. Given a user-provided topic, it uses a local quantized LLM to generate a focused web search query
2. Uses Tavily search API to efficiently gather relevant sources
3. Processes and summarizes the findings with minimal resource usage
4. Reflects on the summary to identify knowledge gaps
5. Generates targeted follow-up queries to address those gaps
6. Iteratively improves the summary while maintaining low resource usage
7. Provides a comprehensive markdown summary with all sources

## 🔧 GGUF Quantization

The-Walker is optimized to work with GGUF quantized models, which offer several advantages:

- **Reduced Memory Usage**: Models use significantly less RAM and VRAM
- **Faster Inference**: Quantized models run faster on the same hardware
- **Minimal Quality Loss**: Carefully balanced quantization preserves most capabilities
- **CPU Compatibility**: Can run on systems without dedicated GPUs

The default configuration uses DeepSeek R1 14B, which offers an excellent balance of performance and resource usage.

## 🌐 React Frontend

The modern React frontend provides:

- **Intuitive Interface**: Clean, responsive design for easy interaction
- **Model Selection**: Choose between different quantized models based on your hardware
- **Research Configuration**: Set the depth and focus of your research
- **Progress Tracking**: Monitor the research process in real-time
- **Results Display**: View formatted research summaries with source attribution

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [LangChain](https://github.com/langchain-ai/langchain) for the LangGraph framework
- [Ollama](https://ollama.com/) for local LLM hosting
- [Tavily](https://www.tavily.com/) for web search capabilities
- [DeepSeek](https://deepseek.ai/) for the optimized R1 models 