"""
Model configurations for the AI agent application.
"""

# Planning agent models (free models from OpenRouter)
# These need to be powerful for research and planning
PLANNING_MODELS = [
    "mistralai/mistral-7b-instruct",
    "openai/gpt-3.5-turbo",
    "meta-llama/llama-2-13b-chat",
    "google/palm-2-chat-bison",
    "anthropic/claude-instant-1"
]

# Coding agent models (free models from OpenRouter)
# These should be good at following instructions precisely
CODING_MODELS = [
    "openai/gpt-3.5-turbo",
    "meta-llama/llama-2-13b-chat",
    "mistralai/mistral-7b-instruct",
    "google/palm-2-chat-bison",
    "anthropic/claude-instant-1"
]

# Checking agent models (free models from OpenRouter)
# These should be good at critical analysis
CHECKING_MODELS = [
    "openai/gpt-3.5-turbo",
    "anthropic/claude-instant-1",
    "meta-llama/llama-2-13b-chat",
    "mistralai/mistral-7b-instruct",
    "google/palm-2-chat-bison"
]

# Model request parameters
DEFAULT_MODEL_PARAMS = {
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 4000
}

# Model parameters by task type
TASK_PARAMS = {
    "planning": {
        "temperature": 0.5,
        "top_p": 0.9,
        "max_tokens": 4000
    },
    "coding": {
        "temperature": 0.3,
        "top_p": 0.95,
        "max_tokens": 8000
    },
    "checking": {
        "temperature": 0.2,
        "top_p": 0.9,
        "max_tokens": 4000
    }
}