Weather Scraping

This project scrapes weather data for Kathmandu from AccuWeather, stores it in a database, analyzes it using Pandas, and visualizes insights using Matplotlib. The entire system is containerized using Docker, making it easy to run locally or in production without environment conflicts.

🛠 Tech Stack

Python (BeautifulSoup, Selenium)

Pandas

Matplotlib

Docker

MySQL

⚙️ Features

Scrapes real-time weather data

Stores structured data in MySQL

Performs data analysis with Pandas

Generates visual insights with Matplotlib

Runs in a containerized environment for easy deployment

📊 Insights

Average temperature trends

Daily temperature comparisons

⚡ Project Structure

Dockerfile – Builds the Python environment with Selenium, Chromium, and required libraries.

docker-compose.yaml – Defines and runs containers for:

Web dashboard (web_dashboard)

Celery worker (celery_worker)

Celery beat scheduler (celery_beat)

MySQL (db)

Redis (redis)

Volumes – Used in development to enable live code updates without rebuilding the image.

Networks – Ensures secure communication between containers.

⚙️ Setup / Installation
1. Build Docker Image
docker compose build
2. Start Containers
docker compose up -d
3. Check Logs
docker compose logs -f web_dashboard
4. Stop Containers
docker compose down
🛠 Development vs Production

Development: Volumes are mounted to allow live code updates without rebuilding the image.

Production: Containers run directly from the image for stability; no volumes are mounted.

🌐 Environment Variables (.env)

MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB – MySQL credentials

REDIS_URL – Redis connection URL

CHROME_BIN, CHROMEDRIVER_PATH – Paths for Selenium Chromium driver

Selenium settings: HEADLESS, IMPLICIT_WAIT, PAGE_LOAD_SLEEP

💡 Tip: For production, consider using secrets management instead of hardcoding sensitive credentials.

🔮 Future Improvements

Add automated tests for scraping functions

Use cloud deployment for scheduled scraping

Implement secrets management for credentials



this is something extra 
3. **Dev vs Production Notes**  
Explain your reasoning about volumes and updates:  
```markdown
- **Development**: Volumes are mounted to allow live code updates without rebuilding the image.
- **Production**: Runs directly from the image for stability; no volumes are mounted.

Docker / Architecture Notes
Briefly explain the Docker structure for clarity:

- **Dockerfile**: Builds the project environment with Python, Selenium, and dependencies.
- **docker-compose.yaml**: Runs containers for the web dashboard, Celery workers, MySQL, and Redis.
- **Volumes**: Used in development for live code updates.
- **Networks**: Ensure containers can communicate securely.


how to restore data backup if disaster happens 
-```docker compose up -d db```
-```docker exec -i weather_db_mysql -u user -ppassword weather_db  <  backups/backup-2026-03-20.sql```