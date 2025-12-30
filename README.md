# DishaPath - Career Guidance Platform

DishaPath is a comprehensive career guidance platform designed to help users discover their ideal career paths through assessments, enroll in relevant courses, and find job opportunities.

## Features

- **Smart Career Assessment**: A detailed assessment to evaluate user skills and interests, providing tailored career path recommendations.
- **Course Management**:
    - Browse and enroll in courses.
    - Track active enrollments.
    - Strict enrollment rules (one active course at a time).
- **User Dashboard**: A central hub for users to view their assessment results, active course progress, and recommended next steps.
- **Job Board**: Explore job listings relevant to your career path.
- **Profile Management**: Comprehensive user profiles with education and location details.
- **Responsive Design**: Built with Tailwind CSS for a seamless mobile-first experience.

## Tech Stack

- **Backend**: Django 5.2
- **Frontend**: Django Templates, Tailwind CSS (v3), Alpine.js
- **Database**: SQLite (Development), PostgreSQL (Production)
- **Authentication**: Django Allauth (Google OAuth support)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Node.js and npm (for Tailwind CSS)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Recjvenik/careerhub.git
    cd careerhub
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Copy the sample environment file and update it with your credentials.
    ```bash
    cp .env.sample .env
    ```

5.  **Apply database migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Install Node.js dependencies (for Tailwind):**
    ```bash
    npm install
    ```

7.  **Build Tailwind CSS:**
    ```bash
    npm run build
    ```
    For development (watch mode):
    ```bash
    npm run watch
    ```

8.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```

    Visit `http://127.0.0.1:8000` in your browser.

## Deployment

For detailed production deployment instructions, please refer to [DEPLOYMENT.md](DEPLOYMENT.md).

## Contributing

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/YourFeature`).
3.  Commit your changes (`git commit -m 'Add some feature'`).
4.  Push to the branch (`git push origin feature/YourFeature`).
5.  Open a Pull Request.
