# agent-s2-example

Example Python code for running the Agent S2 computer use agent locally or remotely. Agent S2 is a state-of-the-art GUI automation agent that can control your computer through natural language.

Learn more: https://github.com/simular-ai/Agent-S

## Requirements

- Python 3.11 (3.7-3.11 supported)
- macOS/Windows/Linux
- OpenAI + Anthropic API keys

## Local Setup

### 1. Clone and Install

```bash
git clone https://github.com/spencerkinney/agent-s2-example.git
cd agent-s2-example

# Create virtual environment
python3.11 -m venv venv # On Mac/Linux
py -3.11 -m venv .venv # On Windows
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
# Copy template
cp .env.example .env

# Edit .env and add your API key
nano .env  # Or open in any text editor
```

Get API keys from:
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/

### 3. macOS Permissions

**System Settings → Privacy & Security → Accessibility**
- Add Terminal (or your IDE)

### 4. Run

```bash
# Interactive mode
python agent_s2.py

# Single command
python agent_s2.py "Take a screenshot"
```

## Example Commands

```
"Open Chrome"
"Type Hello World"
"Click on the search bar"
"Close this window"
```

## .env Template

```env
# ===== REQUIRED =====
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# ===== OPTIONAL =====

# Web Search (Perplexica) - Disabled by default
# To enable web search capabilities:
# 1. Follow setup at: https://github.com/simular-ai/Agent-S#setup-retrieval-from-web-using-perplexica
# 2. Set PERPLEXICA_URL=http://localhost:3000/api/search
# 3. Change SEARCH_ENGINE from "none" to "Perplexica"
SEARCH_ENGINE=none
PERPLEXICA_URL=

# Remote execution (requires orgo.ai account)
USE_CLOUD_ENVIRONMENT=false
ORGO_API_KEY=...

# Model settings
AGENT_MODEL=gpt-4o
AGENT_MODEL_TYPE=openai
GROUNDING_MODEL=claude-3-7-sonnet-20250219
GROUNDING_MODEL_TYPE=anthropic

# Other settings
EMBEDDING_TYPE=openai
MAX_STEPS=10
STEP_DELAY=0.5
```

## Python Code Update

Make sure your `agent_s2.py` disables the search engine by default:

```python
# When initializing Agent S2, use the environment variable
search_engine = "Perplexica" if os.getenv("USE_SEARCH_ENGINE", "false").lower() == "true" else None

agent = AgentS2(
    engine_params,
    grounding_agent,
    platform=current_platform,
    action_space="pyautogui",
    observation_type="screenshot",
    search_engine=search_engine,  # Now defaults to None unless enabled
    embedding_engine_type="openai"
)
```

## Remote Setup

To control a cloud Linux desktop instead of your local machine:

1. Sign up at https://www.orgo.ai
2. Add `ORGO_API_KEY` to `.env`
3. Run with `USE_CLOUD_ENVIRONMENT=true python agent_s2.py`

## Web Search Setup (Optional)

Agent S2 can use web search for better performance. To enable:

1. Install Docker Desktop
2. Follow the [Perplexica setup guide](https://github.com/simular-ai/Agent-S#setup-retrieval-from-web-using-perplexica)
3. Set `USE_SEARCH_ENGINE=true` and `PERPLEXICA_URL` in `.env`

## Troubleshooting

**"PERPLEXICA_URL environment variable not set"** → Set `SEARCH_ENGINE=none` in `.env` or follow the web search setup

**"Module not found"** → `pip install -r requirements.txt`

**Nothing happens** → Check Terminal has Accessibility permissions

**Python version error** → Use Python 3.11: `python3.11 -m venv venv`

---

⚠️ This gives AI control of your computer. Supervise it.