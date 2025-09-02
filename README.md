# Prodigal debt conversation analytics tool

## Features

### Dual Detection Approaches
- **Regex-based Detection**: Fast pattern matching for profanity and privacy violations
- **LLM-powered Analysis**: Advanced AI detection using OpenAI's GPT models for nuanced analysis

### Content Analysis
- **Profanity Detection**: Identifies inappropriate language from both agents and customers
- **Privacy Violation Detection**: Flags instances where sensitive information is shared without proper verification
- **Speaker-specific Analysis**: Separate detection for agents vs. customers

### Acoustic Analysis
- **Overtalk Detection**: Measures conversation interruptions and simultaneous speaking
- **Silence Analysis**: Identifies awkward pauses and engagement gaps
- **Interactive Visualizations**: Real-time pie charts with acoustic insights
- **Quality Metrics**: Automatic assessment of call quality with actionable feedback

### Interactive Web Interface
- **File Upload**: Supports JSON and YAML conversation transcript formats
- **Real-time Processing**: Instant analysis results upon file upload
- **Method Comparison**: Switch between detection approaches to compare results
- **Visual Dashboard**: Comprehensive results display with charts and metrics

## Requirements

- Python 3.8+
- OpenAI API key (for LLM detection features)

## 🛠️ Installation

1. **Clone or download this repository**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up OpenAI API (for LLM detection):**
   
   Create a `.env` file in the project root:
   ```bash
   OPENAI_KEY=your_api_key_here
   ```


4. **Verify dataset:**
   
   Ensure the `All_Conversations/` directory contains the conversation files (250 JSON files included)

## HOW TO USE

1. **Start the application:**
   ```bash
   streamlit run app.py
   ```
   
   The app will launch automatically at [http://localhost:5001](http://localhost:5001)

2. **Upload a conversation file:**
   - Use the file uploader to select a JSON or YAML file
   - Files from the `All_Conversations/` directory work great for testing

3. **Choose detection method:**
   - **Regex**: Fast, rule-based detection
   - **LLM**: AI-powered analysis (requires OpenAI API key)

4. **Analyze results:**
   - View acoustic metrics (overtalk/silence percentages) with interactive charts
   - Click "Run Detection" to analyze content violations
   - Review profanity and privacy violation results

## What You'll Get

### Acoustic Analysis (Automatic)
- **Overtalk Percentage**: How much speakers interrupt each other
- **Silence Percentage**: Amount of awkward pauses in the conversation
- **Quality Insights**: Automatic interpretation of metrics with actionable feedback
- **Interactive Charts**: Visual representation of call quality metrics

### Content Detection Results
- **Profanity Detection**: Separate flags for agent and customer inappropriate language
- **Privacy Violations**: Detailed list of compliance issues with timestamps
- **Speaker Attribution**: Clear identification of who said what and when

## Data Format

The tool expects conversation files with this structure:

```json
[
  {
    "speaker": "Agent",
    "text": "Hello, this is Emma from XYZ Collections, how are you today?",
    "stime": 0,
    "etime": 7
  },
  {
    "speaker": "Customer", 
    "text": "I'm fine, but I really don't have time for this right now.",
    "stime": 7,
    "etime": 12
  }
]
```

**Supported formats:** YAML (.yml, .yaml)

## Architecture

```
├── app.py                          # Main Streamlit application
├── logic/
│   ├── regex_detection.py          # Pattern-based detection algorithms
│   ├── llm_detection.py           # OpenAI-powered detection
│   ├── acoustic_analysis.py       # Overtalk and silence calculations
│   └── acoustic_visualization.py  # Interactive charts and insights
├── All_Conversations/             # Dataset (250 conversation files)
├── requirements.txt              # Python dependencies
└── .env                         # API keys (create this file)
```

## Detection Methods Explained

### Regex Detection
- **Speed**: Instant results
- **Method**: Pattern matching against predefined word lists and rules
- **Best for**: Consistent, rule-based detection

### LLM Detection  
- **Speed**: 2-3 seconds (API call)
- **Method**: LLM analysis using GPT-3.5-turbo with SYSTEM prompts
- **Best for**: Context-aware, nuanced detection

## Dataset Information

The included dataset contains:
- **250 conversation files** in JSON format
- **Real debt collection call transcripts** (anonymized)
- **Varied conversation lengths** and scenarios
- **Multiple speakers** per conversation
- **Timestamp information** for acoustic analysis

## Use Cases

- **Compliance Monitoring**: Ensure debt collection calls meet regulatory standards
- **Quality Assurance**: Identify training opportunities for agents
- **Risk Assessment**: Flag potential legal or reputational risks
- **Performance Analytics**: Measure conversation quality metrics

## Contributing

Feel free to submit issues, feature requests, or improvements. This tool is designed to be extensible and welcomes enhancements.

## Notes

- **Manual Testing**: Currently tested through the Streamlit UI
- **API Costs**: LLM detection uses OpenAI API (small cost per analysis)
- **Privacy**: All analysis happens locally; only LLM detection sends data to OpenAI
- **Performance**: Regex detection is instant; LLM detection takes a few seconds
# Prodigal-assignment-repo
