# AI Server

## Overview

This project is a Python-based Machine Learning/AI API application. It supports both online models from OpenAI and local models from Hugging Face. The application is designed to be modular and extensible, with a focus on ease of use and flexibility.

## Folder Structure

```
ml_api_app/
│
├── app/
│   ├── agents/
│   │   ├── base_agent.py
│   ├── memory/
│   │   ├── long_term_memory.py
│   ├── models/
│   │   ├── base_model.py
│   │   ├── model.py
│   ├── routes.py
│   ├── utils/
│   │   ├── preprocess.py
│   │   ├── postprocess.py
│   ├── __init__.py
│   ├── main.py
│
├── config/
│   ├── config.py
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

4. **Run the application:**
   ```sh
   python -m app.main
   ```

## Usage

### API Endpoints

- **POST /predict**
  - **Description:** Predict using the specified model and agent.
  - **Request Body:**
    ```json
    {
      "data": "your input data",
      "model_type": "openai" or "huggingface",
      "model_name_or_key": "model name or API key",
      "agent_type": "coding" or "chat"
    }
    ```
  - **Response:**
    ```json
    {
      "prediction": "model prediction"
    }
    ```

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.
