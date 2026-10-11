# Task Management Application

A web-based task management application built with **FastAPI**, **Jinja2 templates**, HTML/CSS/JavaScript, and **Google Firebase Authentication / Cloud Firestore**.

## Features

- User registration and login pages
- Create and view task boards
- Create tasks and track completion status and due dates
- Assign users to boards/tasks and manage board members
- Store task boards, users, and tasks in Cloud Firestore
- Static CSS and JavaScript assets served by FastAPI

> This README describes the structure visible in the repository. Exact functionality depends on the current implementation and Firebase configuration.

## Technology Stack

- Python
- FastAPI and Uvicorn
- Jinja2
- HTML, CSS, and JavaScript
- Google Cloud Firestore and Firebase Authentication

## Project Structure

```text
.
├── app.py
├── requirements.txt
├── static/
│   ├── css/
│   └── js/
└── templates/
    ├── Components/
    ├── index.html
    ├── login.html
    ├── register.html
    ├── createtaskboard.html
    ├── task_boards.html
    ├── view_task_board.html
    └── taskBoardDetails.html
```

## Prerequisites

- Python 3.10 or newer
- A Google Cloud project with Cloud Firestore enabled
- Firebase Authentication configured for the project
- A service-account key for local development, stored locally and **not committed to Git**

## Run Locally

1. Clone the repository and enter the project folder:

   ```bash
   git clone https://github.com/Kiransai006/Task_management.git
   cd Task_management
   ```

2. Create and activate a virtual environment.

   **Windows (Command Prompt):**

   ```bat
   py -m venv .venv
   .venv\Scripts\activate
   ```

   **macOS/Linux:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Configure Google Cloud credentials. Place your own service-account JSON file in the project root for local testing, or configure `GOOGLE_APPLICATION_CREDENTIALS` to point to it. Never use or upload another person's key. The current `app.py` references a specific JSON filename, so either use that filename for your own local key or update the application to read the credential path from an environment variable.

5. Start the development server from the project root:

   ```bash
   uvicorn app:app --reload
   ```

6. Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

## Configuration and Security Notes

- Do not commit service-account JSON files, API secrets, tokens, or local environment files.
- Configure a strong, unique session secret using an environment variable before deploying. The current source contains a hard-coded session secret and should be updated before production use.
- Review authentication and token verification before exposing the app publicly. Do not treat decoded JWT claims as trusted unless the token signature and issuer are verified.
- Restrict CORS origins to the actual frontend domains for production instead of allowing every origin.
- Apply least-privilege IAM permissions to the service account.

## Dependencies

Install the Python packages listed in `requirements.txt` with `pip install -r requirements.txt`.

## License

No license is currently specified. Add a `LICENSE` file if you want to define reuse and distribution terms.
