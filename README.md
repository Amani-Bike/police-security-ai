# Police Security AI Platform

A comprehensive platform designed to enhance community safety by connecting citizens with law enforcement through secure, real-time communication channels.

## Features

- **Secure Reporting**: Submit anonymous reports with end-to-end encryption
- **Real-Time Action**: Immediate dispatch alerts to the nearest patrol units
- **Emergency Notifications**: Receive immediate notifications about safety incidents
- **Incident Reporting**: Submit detailed reports with location, photos, and descriptions
- **AI-Powered Assistance**: Built-in chatbot for security advice and emergency detection
- **Location Tracking**: Real-time tracking for civilians and police officers
- **Role-Based Access**: Separate interfaces for civilians and police officers

## Technology Stack

- **Backend**: FastAPI
- **Database**: SQLite (with SQLAlchemy ORM)
- **Frontend**: HTML/CSS/JavaScript
- **Authentication**: JWT-based with role-based access control
- **AI/ML**: LangChain, Sentence Transformers, FAISS for RAG (Retrieval-Augmented Generation)
- **Security**: bcrypt for password hashing

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with the following variables:
   ```
   SECRET_KEY=your_secret_key_here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   ```

## Running the Application

### Method 1: Simple startup with automatic browser opening (Recommended)
Use the new startup script to install dependencies, initialize the database, run the server, and automatically open your browser:

```bash
# Full setup and run with browser automatically opening (recommended)
python startup.py

# Or install dependencies only
python startup.py --install

# Or initialize database only
python startup.py --init-db

# Or run server with browser automatically opening
python startup.py --run --with-browser

# Or run complete setup (install + init-db + run with browser)
python startup.py --setup
```

### Method 2: Using npm-like commands
With the included package.json, you can use npm commands (requires Node.js):

```bash
# Install dependencies
npm install

# Start the application (after installing dependencies)
npm start

# Alternative startup command
npm run dev
```

### Method 4: Windows Batch File (Windows only)
For Windows users, there's also a batch file that automates the entire process:

```bash
# Double-click start_app.bat or run from command line:
start_app.bat
```

### Method 5: Manual setup
For advanced users who prefer manual control:

1. To create a fresh database:
   ```bash
   python create_fresh_db.py
   ```

2. To start the server:
   ```bash
   python -m backend.app
   # Or with uvicorn directly:
   uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
   ```

## API Endpoints

- `/auth/signup` - Register new users
- `/auth/login` - User login
- `/users/signup` - Civilian signup
- `/users/signup/police` - Police signup
- `/users/login/police` - Police login
- `/emergency/report-emergency` - Report emergencies
- `/emergency/emergencies` - Get emergencies (police only)
- `/chat/send` - Send messages to the AI assistant
- `/chat-history/sessions` - Manage chat history

## Database Models

- **User**: Stores user information (civilians and police officers)
- **EmergencyReport**: Stores emergency reports
- **ChatSession**: Stores AI chat sessions
- **ChatMessage**: Stores individual chat messages

## Project Structure

```
police_security_ai/
├── backend/
│   ├── app.py              # Main application
│   ├── database/           # Database setup
│   ├── models/             # Database models
│   ├── routes/             # API routes
│   ├── schemas/            # Pydantic schemas
│   ├── utils/              # Utility functions
│   └── templates/          # Prompt templates (if any)
├── frontend/
│   ├── civilian/           # Civilian frontend
│   ├── police/             # Police frontend
│   └── landing.html        # Main landing page
├── knowledge_base/         # Security knowledge documents
├── alembic/               # Database migration files
├── requirements.txt       # Python dependencies
├── alembic.ini           # Alembic configuration
├── .env                  # Environment variables
├── create_fresh_db.py    # Database creation script
└── README.md             # This file
```

## Security Features

- Passwords are hashed using bcrypt
- JWT tokens for authentication
- Role-based access control (civilian vs police)
- Input validation for all user inputs
- Coordinate validation for Malawi region
- Email format validation

## Emergency Numbers (Malawi)

- Police: 997
- Fire: 998
- Medical: 999
- Child Protection: 116