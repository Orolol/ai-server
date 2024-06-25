# AI Server

## Overview

This project is a Python-based Machine Learning/AI API application. It supports multiple AI providers including OpenAI, Anthropic, and DeepSeek. The application features a long-term memory system, a silent agent for background processing, and a Streamlit-based user interface. It is designed to be modular, extensible, and easy to use.

## Folder Structure

```
ml_api_app/
│
├── app/
│   ├── agents/
│   │   ├── base_agent.py
│   │   ├── chat_session.py
│   │   ├── silent_agent.py
│   ├── memory/
│   │   ├── long_term_memory.py
│   ├── models/
│   │   ├── base_model.py
│   │   ├── model.py
│   ├── routes.py
│   ├── utils/
│   │   ├── preprocess.py
│   │   ├── postprocess.py
│   │   ├── logger.py
│   ├── templates/
│   │   ├── silent_agent_preprompt.jinja
│   ├── __init__.py
│   ├── main.py
│
├── config/
│   ├── config.py
│   ├── ai_providers_config.py
│   ├── __init__.py
│
├── data/
│   ├── raw/
│   ├── processed/
│
├── tests/
│   ├── test_main.py
│   ├── test_model.py
│   ├── __init__.py
│
├── streamlit_app/
│   ├── app.py
│
├── requirements.txt
├── setup.py
├── README.md
├── LICENSE
├── .gitignore
```

## Setup

1. **Clone the repository:**
   ```sh
   git clone <repository_url>
   cd ml_api_app
   ```

2. **Create a virtual environment and activate it:**
   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory and add your API keys:
   ```sh
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   DEEPSEEK_API_KEY=your_deepseek_api_key
   CHROMADB_HOST=your_chromadb_host
   CHROMADB_PORT=your_chromadb_port
   ```

5. **Run the application:**
   ```sh
   python -m app.main
   ```

## Running the Streamlit Frontend

To run the Streamlit frontend, use the following command:

```sh
streamlit run ml_api_app/streamlit_app/app.py
```

## Features

- Multi-provider support (OpenAI, Anthropic, DeepSeek)
- Long-term memory system using ChromaDB
- Silent agent for background processing
- Chat sessions with conversation history
- Streamlit-based user interface
- Configurable AI provider settings

## Usage

The Streamlit interface allows users to:
- Start new chat sessions
- Send messages to the AI
- View conversation history
- Clear the long-term memory
- Configure AI provider and model strength

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.
