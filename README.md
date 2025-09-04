# Django Project
## Clinical Lab Management System

<img width="1920" height="1080" alt="Screenshot from 2025-09-04 16-54-01" src="https://github.com/user-attachments/assets/a0488b12-fb3f-4b43-b4c0-b20265bf2058" />



## Overview
This is a Django-based web application that includes functionality related to accounts, patients, reports, and more. The project uses SQLite as its default database with a backup file included. It is designed for easy setup, testing, and development.

## Prerequisites
- Python 3.x installed on your system
- pip package manager
- (Optional but recommended) Virtual environment tool (`venv` or `virtualenv`)

## Installation

1. Clone this repository:

git clone <your-repo-url>
cd <project-folder>

text

2. (Optional) Create and activate a virtual environment:
- On Windows:
  ```
  python -m venv venv
  venv\Scripts\activate
  ```
- On macOS/Linux:
  ```
  python3 -m venv venv
  source venv/bin/activate
  ```

3. Install dependencies:

pip install -r requirements.txt

text

4. Apply database migrations:

python manage.py migrate

text

## Running the Project

To start the Django development server, run:

python manage.py runserver

text

Then open your browser and navigate to:

http://127.0.0.1:8000

text
You should see the running application.

## Notes

- If the app throws errors related to `ALLOWED_HOSTS` or you want to switch off debug messages, edit `settings.py`:
  - Set `DEBUG = False` for production.
  - Add your domain or IP address to the `ALLOWED_HOSTS` list. Example:
    ```
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'yourdomain.com']
    ```
- When `DEBUG = False`, make sure to run:

python manage.py collectstatic

text
and configure static file serving appropriately for production.

## Running Tests

To run the included tests:

python manage.py test

text

## Project Structure

- `manage.py`: Django management CLI tool
- `requirements.txt`: Python dependencies list
- `venv/`: (Optional) Virtual environment directory
- `accounts/`, `patients/`, `reports/`, `tests/`: Django app directories
- `templates/`: HTML templates for views
- `db.sqlite3.bak`: Database backup file
- Other scripts like `build.sh` and documentation files (`srcdoc.pdf`)

## Contributing

Contributions and improvements are welcome! Feel free to fork the repository and submit pull requests. Please follow existing code style and testing practices.

## License

MIT

## Screenshots

<img width="1920" height="1080" alt="Screenshot from 2025-09-04 16-54-26" src="https://github.com/user-attachments/assets/c4d78376-2d87-4838-930a-095283131876" />


---

This README provides instructions to get this Django project up and running locally for development and testing purposes.
