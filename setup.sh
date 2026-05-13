#!/bin/bash

# RAG + Ollama System Setup Script
echo "🚀 Setting up RAG + Ollama System..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama not found. Please install Ollama first:"
    echo "   Visit: https://ollama.ai/download"
    echo "   Then run: ollama pull llama3.2:latest"
else
    echo "✅ Ollama found"
    # Pull Llama 3.2 model if not already present
    echo "📥 Pulling Llama 3.2 model..."
    ollama pull llama3.2:latest
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p results
mkdir -p logs

echo "✅ Setup complete!"
echo ""
echo "🎯 To run the system:"
echo "   cd scripts"
echo "   python enhanced_rag_ollama_system.py"
echo ""
echo "📊 Results will be saved in the results/ folder" 