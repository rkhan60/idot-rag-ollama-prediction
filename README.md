# Enhanced RAG + Ollama System

## 🎯 Quick Start

### 1. Setup
```bash
./setup.sh
```

### 2. Run System
```bash
cd scripts
python enhanced_rag_ollama_system.py
```

### 3. View Results
Check the `results/` folder for Excel files with comprehensive analysis.

## 📁 What's Included

### Data Files (`data/`)
- **firms_data.json**: 415 firms with prequalifications and capacity data
- **prequal_lookup.json**: Prequalification category to firm mapping
- **district_mapping.json**: Illinois district geographic information
- **award_structure.json**: 2,095 historical project awards
- **ptb160-170_docx_text.txt**: PTB bulletin files (excluding PTB164)

### Scripts (`scripts/`)
- **enhanced_rag_ollama_system.py**: Complete system implementation

### Results (`results/`)
- **enhanced_rag_ollama_results_*.xlsx**: Excel files with:
  - Summary metrics
  - Detailed predictions
  - Ollama insights

### Documentation (`documentation/`)
- **SYSTEM_OVERVIEW.md**: Comprehensive system documentation

## 🔧 System Features

✅ **Enhanced Data Extraction**: Job info, DBE requirements, prequalifications  
✅ **Firm Matching**: 266-297 eligible firms per project  
✅ **RAG Integration**: Historical project similarity analysis  
✅ **Ollama AI**: Llama 3.2 powered project insights  
✅ **Excel Export**: Comprehensive results reporting  

## 📊 Current Status

- **Projects Processed**: 10 (PTB160-170, excl. PTB164)
- **Average Eligible Firms**: 280 per project
- **RAG Performance**: 5 similar projects found per query
- **Ollama Integration**: 100% successful analysis
- **Overall Accuracy**: 0.0% (needs optimization)

## 🎯 Next Steps

1. Analyze Excel results for accuracy improvement
2. Refine prediction algorithm
3. Investigate actual winner matching
4. Optimize for 60% accuracy target

## 📋 Requirements

- Python 3.8+
- Ollama with Llama 3.2 model
- See `requirements.txt` for Python packages

---

**System Version**: 1.0  
**Last Updated**: August 3, 2025  
**Status**: Functional, ready for accuracy optimization 