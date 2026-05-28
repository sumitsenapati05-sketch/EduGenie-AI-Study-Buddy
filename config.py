# config.py - Centralized configuration for EduGenie project

# Groq API configuration
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama3-8b-8192"

# Text limits
ONLINE_MODE_MAX_CHARS  = 150000
ONLINE_MODE_MAX_WORDS  = 1500
OFFLINE_MODE_MAX_CHARS = 500000
OFFLINE_MODE_MAX_WORDS = 50000

# Output directory
OUTPUT_DIR = "output"
