# Oversight Program

To start the program, follow these steps:

1. **Install Dependencies**:
   In your terminal, run the following commands:
   ```
      pip install -r requirements.txt
      python manage.py makemigrations
      python manage.py migrate
      python manage.py runserver
   ```
3. **Start Redis Server**:
  Open a new terminal and run:
   ```
      redis-server
   ```
4. **Start Celery Worker**:
  In another new terminal, run:
   ```   
      celery -A aviaServer worker -l info
   ```
6. **Start Celery Beat**:
  In yet another new terminal, run:
   ```
      celery -A aviaServer beat -l info
   ```
