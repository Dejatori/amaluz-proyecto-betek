## Project Overview

**Online Candle Shop Management** is an application designed to manage and operate an online candle store. The system provides a robust API built with Flask with a future migration plan to FastAPI (Python). It enables management of products, employees, and orders, and displays key metrics, integrating technologies such as MySQL, Redis, and Power BI for advanced analytics.

---

## Global Prerequisites

Before getting started, make sure the following are installed on your system:

- [Git](https://git-scm.com/)
- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js 18+ and npm](https://nodejs.org/)
- [MySQL 8+](https://dev.mysql.com/downloads/mysql/)
- [Redis](https://redis.io/download)
- (Optional) [Power BI Desktop](https://powerbi.microsoft.com/desktop/) for advanced visualization

---

## Cloning the Repository

Clone the repository from GitHub:

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

---

## Backend Setup

### Installing Dependencies

1. Create and activate a virtual environment:

    ```bash
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On Linux/Mac:
    source venv/bin/activate
    ```

2. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    pip install -r dev-requirements.txt
    ```

### Database Configuration

1. Ensure MySQL and Redis are running on your local machine.
2. There is a sample MySQL database script at `db/amaluz_ddl.sql`. You can create the database by running the provided SQL script.
3. Copy the `.env.example` file to `.env` and configure the required environment variables, especially the database connection string:

    ```
    DATABASE_URL="mysql+aiomysql://candle_user:your_secure_password@localhost:3306/candle_management"
    ```
4. (Optional) Apply initial migrations if the project includes them:

    ```bash
    alembic upgrade head
    ```

### Running the Backend Server

Using FastAPI (work in progress). Start the FastAPI server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Access the interactive API docs at: [http://localhost:8000/docs](http://localhost:8000/docs)

Using Flask (if migration to FastAPI hasn't been completed yet):

```bash
cd app
flask run
```
---

### Running the Tkinter Interface

```bash
cd app
python gui.py
```

---

## Next Steps (Suggestions)

- Run additional database migrations or seeders if the project requires them.
- Configure Redis for caching and session storage if needed.
- Complete the backend migration to FastAPI to take advantage of its modern features.
- Review the application documentation in `/docs` for more details about routes and available features.
- Inspect configuration files and additional documentation to customize the environment to your needs.

## License

This project is licensed under the GPL-3.0 License. See the [LICENSE](LICENSE) file for more details.
