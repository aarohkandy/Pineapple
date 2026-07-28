# AI Agent

An AI-powered application that uses specialized models for planning, coding, and checking code to implement solutions based on user requests.

## Overview

This application leverages free AI models from OpenRouter to create a comprehensive development assistant with specialized capabilities:

1. **Planning Agent**: Analyzes requests, researches solutions, and creates detailed plans
2. **Coding Agent**: Implements solutions based on the planning agent's instructions
3. **Checking Agent**: Verifies code functionality and suggests improvements

## Features

- Multi-model orchestration with fallback options
- Virtual code execution environment for testing
- Detailed planning and code analysis
- Simple command-line interface

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/ai-agent.git
   cd ai-agent
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your OpenRouter API key:
   ```
   export OPENROUTER_API_KEY="your_api_key_here"
   ```

## Usage

1. Run the application:
   ```
   python main.py
   ```

2. Enter your coding or development request at the prompt.

3. The system will:
   - Analyze and plan a solution
   - Generate code to implement it
   - Check and test the code
   - Show you the results

4. Type `save` after getting results to save all generated files to your current directory.

## Configuration

Edit the files in the `config` directory to:
- Change the models used by each agent
- Adjust system parameters
- Configure model parameters

## File Structure

```
ai-agent/
├── main.py                     # Entry point
├── core/                       # Core engine components
├── agents/                     # Specialized agents
├── utils/                      # Utility functions
├── config/                     # Configuration files
└── ui/                         # User interface
```

## Requirements

- Python 3.8 or higher
- OpenRouter API key
- Internet connection

## License

MIT License

## Acknowledgements

This project uses models from OpenRouter (https://openrouter.ai/).