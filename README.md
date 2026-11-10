# WAEI – Work Agreement Evaluation and Inspection

## Project Overview

WAEI is a software engineering project designed to assist users in reviewing employment contracts against structured labor-law rules. The system extracts information from employment contracts and evaluates relevant clauses to help identify potential compliance issues.

The project combines document processing, rule-based evaluation, and Large Language Model (LLM) capabilities to support employment contract analysis.

**Disclaimer:** WAEI is an academic software project and is not a substitute for professional legal advice. All results should be reviewed by a qualified legal professional.

## Main Features

- **User Management:** User registration, login, profile management, and logout.
- **Password Recovery:** Email-based OTP verification.
- **Contract Management:** Uploading, retrieving, listing, and deleting employment contracts.
- **Document Processing:** Text extraction from PDF and DOCX documents.
- **Contract Analysis:** AI-assisted extraction and evaluation of contract clauses.
- **Labor Law Rules:** Structured labor-law rules stored in JSON format.
- **Compliance Findings:** Identification and management of potential contract compliance issues.
- **Dashboard:** Summary information about contract analysis and findings.
- **Web Interface:** Flask-based application interface.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend development |
| Flask | Web application framework |
| MySQL | Database management |
| HTML | Web interface |
| JSON | Labor-law rule storage |
| LLM | AI-assisted contract analysis |
| llama.cpp | Local language model integration |
| Jupyter Notebook | Rule encoding and experimentation |
| PyPDF | PDF text extraction |
| python-docx | DOCX document processing |

## Project Structure

```text
SE499_WAEI/
│
├── classes/
│   ├── contract.py
│   ├── finding.py
│   ├── legal_source.py
│   ├── rule.py
│   ├── rule_version.py
│   ├── rules_clauses.py
│   ├── rules_manager.py
│   ├── text_extraction_service.py
│   └── user.py
│
├── rules_as_code/
│   └── JSON rule files
│
├── templates/
│   └── preview.html
│
├── tests/
│   └── test_sprint_2.py
│
├── labor_law.pdf
├── labor_rules.json
├── rule_encoder.ipynb
└── server_sprint_3.py
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Rahafalnatheer/SE499_WAEI.git
cd SE499_WAEI
```

### 2. Create a Virtual Environment

For macOS and Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

For Windows:

```bash
py -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
python -m pip install Flask Flask-Mail mysql-connector-python Werkzeug pypdf python-docx huggingface-hub llama-cpp-python
```

### 4. Configure the Database

The application uses MySQL and expects a database named `waei`.

Create the database and configure the required tables and credentials before running the application. The database schema must be obtained from the project team or prepared according to the application code.

### 5. Run the Application

After configuring the database and application settings:

```bash
python server_sprint_3.py
```

Open the local address displayed in the terminal, commonly:

```text
http://127.0.0.1:5000/
```

## Testing

Run the available tests using:

```bash
python -m unittest discover -s tests -v
```

Note: The current test file references an earlier module named `server_sprint_2`. The tests may need updating to match the current application version.

## Security Considerations

- Store passwords, API keys, and secret keys securely.
- Do not commit database credentials or email passwords.
- Use environment variables for sensitive configuration.
- Validate uploaded documents and restrict file sizes.
- Protect user information and uploaded employment contracts.

## Project Information

**Course:** SE499 – Software Engineering Project

**Project Name:** WAEI – Work Agreement Evaluation and Inspection

**Repository:** [SE499_WAEI](https://github.com/Rahafalnatheer/SE499_WAEI)

---

*Developed as part of an academic software engineering project.*
