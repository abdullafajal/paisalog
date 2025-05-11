# Paisalog - Personal Finance Tracker

A Django-based personal finance tracking application that helps you monitor your income and expenses.

## Features

- User authentication (signup, login, logout)
- Dashboard with financial overview
- Income and expense tracking
- Monthly summaries and reports
- Beautiful UI using Tabler
- Interactive charts with Chart.js

## Prerequisites

- Python 3.8 or higher
- uv package manager

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/paisalog.git
cd paisalog
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies using uv:
```bash
uv pip install -e .
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000 to access the application.

## Project Structure

- `paisalog/` - Main project directory
  - `core/` - Core application with models and views
  - `templates/` - HTML templates
  - `static/` - Static files (CSS, JS, images)
  - `manage.py` - Django management script

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.