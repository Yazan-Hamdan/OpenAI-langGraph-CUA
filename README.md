# Operator

playwright version of OpenAI’s Operator.

## Getting Started

Follow these instructions to set up and run the project locally.

### 1. Clone the Repository

```bash
git clone https://github.com/Yazan-Hamdan/OpenAI-langGraph-CUA.git
cd OpenAI-langGraph-CUA
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright

```bash
playwright install
```

### 5. Set Up Environment Variables
Copy the example `.env` file and fill in the required values:
```bash
cp .env.example .env
```
Edit `.env` and update the placeholders with your actual configuration.

## Starting Points
After setup, you can begin using the project by running one of the following entry points:

### `structured_output.py`
Use this file to extract structured data or perform specific tasks with predefined schema.
```bash
python structured_output.py
```

### `query_answering.py`
Use this file for running queries and receiving answers based on automated interactions
```bash
python query_answering.py
```
