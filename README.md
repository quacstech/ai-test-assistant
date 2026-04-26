# AI Test Scenario Creator

An AI-powered assistant that thinks like a senior QA engineer. Describe a feature or API and get structured, professional test scenarios instantly — across positive, negative, edge, and security categories.

## What it does

You describe something to test. The assistant analyses it and returns structured test scenarios ready to use or turn into code.

**Example:**

```
What would you like to create test scenarios for? > Login API with JWT authentication
```

**Output:**
- Positive cases — happy path scenarios
- Negative cases — invalid inputs, wrong credentials, missing fields
- Edge cases — boundary values, empty inputs, special characters
- Security scenarios — token handling, enumeration prevention, injection

## Tech stack

- Python 3.9+
- LangChain
- Anthropic Claude API (claude-sonnet)
- httpx
- pytest *(for generated API tests — coming soon)*
- Playwright *(for generated GUI tests — coming soon)*

## Project structure

```
ai-test-assistant/
  main.py                  # Entry point — interactive CLI
  agent.py                 # LangChain agent setup
  tools/
    analyser.py            # Scenario analysis tool
    generator.py           # Test code generator
    debugger.py            # Failure debugger
    api_caller.py          # Live API interaction
  prompts/
    system_prompt.py       # QA persona and instructions
    templates.py           # Output format templates
  output/
    generated_tests/       # Generated test files land here
  requirements.txt
  .env                     # API keys — not committed
```

## Setup

**1. Clone the repository:**
```bash
git clone https://github.com/quacstech/ai-test-assistant.git
cd ai-test-assistant
```

**2. Create and activate virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Add your Anthropic API key:**
```bash
cp .env.example .env
# Edit .env and add your key
ANTHROPIC_API_KEY=your_key_here
```

Get your API key at [console.anthropic.com](https://console.anthropic.com)

**5. Run:**
```bash
python3 main.py
```

## Roadmap

### MVP (in progress)
- [x] Project structure and environment setup
- [x] Claude API connection
- [x] QA-focused system prompt
- [x] Interactive CLI input
- [x] Structured scenario analysis
- [ ] pytest test file generator
- [ ] Failure debugger
- [ ] Live API caller

### Post-MVP
- [ ] Web UI (Streamlit)
- [ ] GUI test generation via Playwright DOM analysis
- [ ] Multi-agent review layer
- [ ] OpenAPI spec input support
- [ ] Persistent memory across sessions
- [ ] Docker + cloud deployment

## Cost

Uses the Anthropic API on a pay-as-you-go basis. Typical cost per analysis session is under $0.02. A $5 credit covers hundreds of sessions.

## License

MIT