
# 🎬 Netflix Data Pipeline

This is a containerized data pipeline for ingesting, preprocessing, and analyzing Netflix titles data.

The aim of this project is to transform raw CSV data on Netflix titles into a structured PostgreSQL database to enable analysis of content over time, such as the ratio of Movies to TV Shows or the most common TV categories.

---

## 🚀 Technologies Used

* **Docker / Docker Compose** → containerization and multi-service orchestration
* **Python (Pandas)** → data preprocessing and cleaning
* **PostgreSQL** → structured data storage and validation
* **Bash Scripting** → pipeline automation
* **Cron** → scheduling periodic pipeline runs

---

## 📂 Project Structure

```
netflix-analysis/
├── data/
│   └── netflix_titles.csv
├── scripts/
│   └── preprocessing.py
├── sql/
│   ├── create_tables.sql
│   └── queries.sql
├── Dockerfile
├── docker-compose.yml
├── run_pipeline.sh
├── cronjob
├── requirements.txt 
└── README.md
```

* `data/` → Contains the raw input CSV file
* `scripts/preprocessing.py` → Python logic for cleaning and transforming data
* `sql/create_tables.sql` → DDL(Data Definition Language) script to set up the database schema
* `sql/queries.sql` → Example analytical queries on the processed data
* `Dockerfile` → Defines the Python environment
* `docker-compose.yml` → Defines the multi-container setup (Python + Postgres)
* `run_pipeline.sh` → Main entrypoint script for the pipeline
* `cronjob` → Configuration for scheduled automation
* `requirements.txt` → Python dependencies

---

## ⚙️ Setup & Installation

This guide will help you set up and run the Netflix Data Analysis pipeline on your local machine.

### ✅ Prerequisites

Make sure you have the following installed:

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Mac/Windows) or [Docker Engine](https://docs.docker.com/engine/install/) (Linux)
* [Docker Compose](https://docs.docker.com/compose/install/) (bundled with Docker Desktop, separate install on Linux)
* [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

---

### 🔹 Step 1: Clone the Repository

```bash
git clone <your-github-repository-url>
cd netflix-analysis
```

---

### 🔹 Step 2: Environment Variables

By default, the database credentials are defined inside `docker-compose.yml`:

```yaml
environment:
  POSTGRES_DB: ${POSTGRES_DB:-netflix_db}
  POSTGRES_USER: ${POSTGRES_USER:-postgres}
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-mypassword}
  POSTGRES_HOST: ${POSTGRES_HOST:-db}
  POSTGRES_PORT: ${POSTGRES_PORT:-5432}
```

#### What this means

* **Out of the box** → If you do nothing, Docker Compose will use the defaults:

  * Database: `netflix_db`
  * User: `postgres`
  * Password: `mypassword`
  * Host: `db`
  * Port: `5432`

* **Optional customization** → If you want to change these values, create a `.env` file in the project root:

```bash
POSTGRES_DB=my_own_db
POSTGRES_USER=custom_user
POSTGRES_PASSWORD=supersecret
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

⚠️ Make sure to add `.env` to `.gitignore` so you don’t commit your secrets.

---

### 🔹 Step 3: (Optional) Prepare the Data File

Place your `netflix_titles.csv` file into the `data/` directory. If the dataset is already in the repo, you can skip this step.

---

### 🔹 Step 4: Build and Launch the Services

```bash
docker-compose up --build -d
```

**What happens?**

* The `app` (Python) container is built from your `Dockerfile` with dependencies installed.
* The `db` (PostgreSQL) container starts from the official image.
* A Docker network is created so the two containers can communicate.

---

### 🔹 Step 5: Run the Data Pipeline

Run the preprocessing and loading steps inside the Python container:

```bash
docker-compose run app /bin/bash -c "chmod +x ./run_pipeline.sh && ./run_pipeline.sh"
```

---

### 🔹 Step 6: Verify the Installation (Optional)

Connect to the Postgres container:

```bash
docker-compose exec db psql -U postgres -d netflix_db
```

Inside the `psql` prompt, run:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';
```

You should see your created tables. Exit with `\q`.

---

## 🛑 Stopping the Services

To stop and remove running containers:

```bash
docker-compose down
```

To also remove the database volume (fresh start):

```bash
docker-compose down -v
```

⚠️ `-v` will delete all database data. Use only if you want to reset completely.

---

## 🔄 Running the Pipeline Again

```bash
docker-compose up -d   # Start services if not running
docker-compose run app ./run_pipeline.sh
```

---

## 💾 Volumes & Persistence

* PostgreSQL data is stored in a **named volume** (`db_data`) so it persists across container restarts.
* The raw CSV dataset is **mounted** from your host into the Python container.

## Example Usage & Analysis Queries

Once the pipeline has loaded the data into PostgreSQL, you can run queries to explore Netflix content. Here are some sample queries you can use to explore the data. 

* 1. Total number of titles
``` sql
SELECT COUNT(*) FROM movies;
```

* 2. Movies vs TV Shows
``` sql 
SELECT movie_type, COUNT(*) AS count
FROM movies
GROUP BY movie_type;
```

3. Content growth over time
```sql 
SELECT release_year, COUNT(*) AS titles
FROM movies
GROUP BY release_year
ORDER BY release_year;
```
Expected result: See how Netflix’s catalog expands year by year.

## Automation with Cronjob

The pipeline is automated using the `cronjob` file in the repo.  
This will schedule the pipeline to run every day at midnight **inside your container's environment** (not on your host machine).  

You can also modify the cron expression in the file to suit your own schedule.