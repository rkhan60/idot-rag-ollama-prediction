# Enhanced RAG + Ollama System - Comprehensive Overview

## 🎯 System Purpose
This system combines Retrieval-Augmented Generation (RAG) with Ollama (Llama 3.2) to predict winning firms for construction projects listed in PTB (Professional and Technical Bulletin) files. The goal is to achieve 60%+ accuracy in predicting the top 5 firms most likely to win each project.

## 🏗️ System Architecture

### Core Components:
1. **Enhanced Data Extraction** - Extracts critical project information from bulletins
2. **Firm Matching Engine** - Matches firms based on prequalifications and distance
3. **RAG Knowledge Base** - Historical project similarity analysis
4. **Ollama Integration** - AI-powered project understanding
5. **Prediction Algorithm** - Multi-factor scoring system
6. **Excel Export** - Comprehensive results reporting

## 📁 Folder Structure

```
RAG+Ollama/
├── data/                          # All input data files
│   ├── firms_data.json           # 415 firms with prequalifications
│   ├── prequal_lookup.json       # Prequalification to firm mapping
│   ├── district_mapping.json     # Geographic district information
│   ├── award_structure.json      # Historical award data (2,095 records)
│   └── ptb160_docx_text.txt      # PTB bulletin files (160-170, excl. 164)
│   └── ptb161_docx_text.txt
│   └── ptb162_docx_text.txt
│   └── ptb163_docx_text.txt
│   └── ptb165_docx_text.txt
│   └── ptb166_docx_text.txt
│   └── ptb167_docx_text.txt
│   └── ptb168_docx_text.txt
│   └── ptb169_docx_text.txt
│   └── ptb170_docx_text.txt
├── scripts/                       # Main system scripts
│   └── enhanced_rag_ollama_system.py  # Complete system implementation
├── results/                       # Output files
│   └── enhanced_rag_ollama_results_*.xlsx  # Excel results with multiple sheets
└── documentation/                 # System documentation
    └── SYSTEM_OVERVIEW.md         # This file
```

## 🔧 Key Features

### 1. Enhanced Data Extraction
- **Job Information**: Job number, description, region/district
- **DBE Requirements**: Disadvantaged Business Enterprise participation %
- **Contract Duration**: Project timeline in months/years
- **Prequalification Requirements**: Required firm categories (CRITICAL)
- **Personnel Requirements**: Key personnel and qualifications

### 2. Firm Matching Process
```
Step 1: Extract prequalification requirements from bulletin
Step 2: Use prequal_lookup.json to find eligible firms
Step 3: Filter by distance using district_mapping.json
Step 4: Get complete firm data from firms_data.json
```

### 3. RAG Integration
- **Knowledge Base**: 2,088 historical projects
- **TF-IDF Vectorization**: Semantic similarity analysis
- **Similar Projects**: Top 5 most similar historical projects per current project

### 4. Ollama Integration
- **Model**: Llama 3.2 (latest)
- **Analysis**: Project complexity, challenges, recommendations
- **Output**: 2,480-3,930 characters of insights per project

### 5. Prediction Algorithm
- **Base Score**: 100 points per firm
- **Distance Penalty**: Closer firms get better scores
- **Capacity Bonus**: Large/Medium firms get bonuses
- **Historical Performance**: Based on total awards
- **Similar Project Experience**: Bonus for firms with similar project wins

## 📊 Current Performance

### Test Results (PTB160-170, excluding PTB164):
- **Total Projects**: 10
- **Average Eligible Firms**: 280 per project
- **Distance Filter Success**: 100% (all firms within range)
- **Similar Projects Found**: 5 per project
- **Ollama Insights**: Generated for all projects
- **Overall Accuracy**: 0.0% (needs refinement)

### Data Statistics:
- **Firms Database**: 415 active firms
- **Prequalification Categories**: 61 categories
- **Historical Awards**: 2,095 records
- **Districts**: 9 Illinois districts mapped

## 🚀 Usage Instructions

### Prerequisites:
1. Python 3.8+
2. Required packages: `pandas`, `numpy`, `scikit-learn`, `openpyxl`
3. Ollama installed with Llama 3.2 model

### Running the System:
```bash
cd RAG+Ollama/scripts
python enhanced_rag_ollama_system.py
```

### Output:
- Excel file with 3 sheets:
  1. **Summary**: Overall metrics and performance
  2. **Detailed Results**: Project-by-project predictions
  3. **Ollama Insights**: AI analysis for each project

## 🔍 Key Insights

### Strengths:
1. **Comprehensive Extraction**: Captures all critical project requirements
2. **Robust Firm Matching**: 266-297 eligible firms per project
3. **RAG Integration**: Leverages historical project similarity
4. **AI Enhancement**: Ollama provides project insights
5. **Scalable Architecture**: Easy to extend and modify

### Areas for Improvement:
1. **Prediction Algorithm**: Needs refinement for better accuracy
2. **Actual Winner Matching**: Investigate why winners aren't being found
3. **Firm Filtering**: May need more selective criteria
4. **Scoring Weights**: Optimize the scoring formula

## 🎯 Next Steps

1. **Analyze Excel Results**: Review detailed predictions vs actual winners
2. **Refine Prediction Algorithm**: Improve scoring methodology
3. **Investigate Winner Matching**: Fix actual winner identification
4. **Implement Additional Filters**: Add more sophisticated filtering
5. **Optimize for 60% Accuracy**: Target achievement

## 📋 File Descriptions

### Data Files:
- **firms_data.json**: Complete firm database with prequalifications, capacity, location
- **prequal_lookup.json**: Mapping of prequalification categories to eligible firms
- **district_mapping.json**: Geographic information for Illinois districts
- **award_structure.json**: Historical project awards and winners
- **ptb*_docx_text.txt**: Extracted text from PTB bulletins

### Scripts:
- **enhanced_rag_ollama_system.py**: Complete system implementation with all features

### Results:
- **enhanced_rag_ollama_results_*.xlsx**: Comprehensive Excel output with analysis

## 🔗 Dependencies

### Python Packages:
```python
import json
import re
import os
import glob
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import subprocess
from datetime import datetime
import math
from difflib import SequenceMatcher
```

### External Dependencies:
- **Ollama**: Local LLM server with Llama 3.2 model
- **Excel**: For comprehensive results export

## 📈 Performance Metrics

### Current Metrics:
- **Data Processing**: 100% successful extraction
- **Firm Matching**: 266-297 firms per project
- **RAG Performance**: 5 similar projects found per query
- **Ollama Integration**: 100% successful analysis
- **Export Success**: Excel files generated with all data

### Target Metrics:
- **Accuracy**: 60% (current: 0%)
- **Processing Speed**: <30 seconds per project
- **Coverage**: 100% of available projects
- **Reliability**: 100% successful processing

---

**Last Updated**: August 3, 2025
**System Version**: 1.0
**Status**: Functional, needs accuracy optimization 