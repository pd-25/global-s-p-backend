**Installation**

- **Prerequisites:** Python 3.10+ installed, Git, and system build tools for any C extensions.

- **Clone repository:**

```bash
git clone 
cd global-s-p-api
```

- **Create and activate a virtual environment:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

- **Install dependencies:**

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

- **Environment variables:**

Create a `.env` file in the project root with at least the database URL. Example contents:

```env
# Example .env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/dbname
# Add other variables as needed (SECRET_KEY, DEBUG, etc.)
```

- **Database migrations:**

Apply Alembic migrations to create/update database schema:

```bash
alembic -c alembic.ini upgrade head
```

- **Run the development server:**

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- **Run tests (if available):**

```bash
pytest
```


