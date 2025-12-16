# Deployment Guide for Police Security AI

This document provides instructions for deploying the Police Security AI application to various platforms.

## Deployment Options

### 1. Heroku Deployment

1. Create a `Procfile` (already included):
   ```
   web: uvicorn backend.app:app --host=0.0.0.0 --port=${PORT:-8000}
   ```

2. Create a `runtime.txt` file with your Python version:
   ```
   python-3.11.5
   ```

3. Add gunicorn to your requirements.txt for production:
   ```
   gunicorn
   ```

4. Deploy using Heroku CLI:
   ```bash
   heroku create your-app-name
   heroku buildpacks:set heroku/python
   git push heroku main
   ```

### 2. Railway Deployment

1. Connect your GitHub repository to Railway
2. Select Python as your project type
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn backend.app:app --host=0.0.0.0 --port=$PORT`

### 3. Render Deployment

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set runtime to Python
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn backend.app:app --host=0.0.0.0 --port=$PORT`

### 4. Docker Deployment

Build and run the Docker container:

```bash
# Build the image
docker build -t police-security-ai .

# Run the container
docker run -p 8000:8000 police-security-ai
```

Or using docker-compose:

```bash
docker-compose up -d
```

### 5. Production Server Deployment

For production deployment on a VPS, follow these steps:

1. Set up the server with:
   - Ubuntu/Debian
   - Python 3.11+
   - Git
   - Nginx
   - Gunicorn
   - Systemd (for service management)

2. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/police-security-ai.git
   cd police-security-ai
   ```

3. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Setup the database:
   ```bash
   python init_db.py
   ```

5. Install and configure Gunicorn:
   ```bash
   pip install gunicorn
   ```

6. Create Gunicorn configuration file (`gunicorn.conf.py`):
   ```python
   bind = "0.0.0.0:8000"
   workers = 4
   worker_class = "uvicorn.workers.UvicornWorker"
   timeout = 120
   max_requests = 1000
   max_requests_jitter = 100
   ```

7. Create a systemd service file (`/etc/systemd/system/police-security-ai.service`):
   ```ini
   [Unit]
   Description=Police Security AI
   After=network.target

   [Service]
   Type=notify
   User=www-data
   Group=www-data
   WorkingDirectory=/path/to/police-security-ai
   Environment=PATH=/path/to/police-security-ai/venv/bin
   ExecStart=/path/to/police-security-ai/venv/bin/gunicorn backend.app:app -c gunicorn.conf.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

8. Start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable police-security-ai
   sudo systemctl start police-security-ai
   ```

9. Configure Nginx to proxy requests to Gunicorn:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

## Environment Variables for Production

For production deployment, you'll need to set these environment variables:

- `SECRET_KEY`: A strong secret key for JWT tokens
- `ALGORITHM`: Should be "HS256"
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (e.g., 1440 for 24 hours)
- `GEMINI_API_KEY`: Your Google Gemini API key for AI features

## Notes for Production

1. **Database**: For production, consider using PostgreSQL instead of SQLite for better performance and reliability.

2. **Security**: 
   - Use HTTPS in production
   - Set secure CORS policies
   - Don't expose the server to all origins in production

3. **Performance**: Consider adding Redis for caching and session management.

4. **Monitoring**: Add logging and monitoring for production deployments.

5. **Backups**: Implement regular backups of your database and important files.