Cashually — Backend API
A personal budget tracking app built with FastAPI. Track your expenses, set budgets per category, and manage your spending all in one place.
Features
JWT-based authentication (register, login, logout)
Add, update, and delete expenses
Categorize expenses with custom categories
Set monthly budgets per category
View expense history with filters (date, category, amount)
Budget tracking with overspend detection
Tech Stack
Framework — FastAPI
ORM — SQLAlchemy
Database — SQLite (local) / PostgreSQL (production)
Auth — JWT via `python-jose` + `passlib`
Server — Uvicorn
Project Structure
```
expense_tracker/
├── app/
│   ├── main.py          # App entry point, middleware
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   ├── database.py      # DB connection
│   ├── auth.py          # JWT logic
│   └── routers/
│       ├── auth.py
│       ├── expenses.py
│       ├── categories.py
│       └── budgets.py
├── requirements.txt
└── .env
```
Run Locally
Clone the repo
```bash
   git clone https://github.com/your-username/expense-tracker.git
   cd expense-tracker
   ```
Create and activate a virtual environment
```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # Mac/Linux
   ```
Install dependencies
```bash
   pip install -r requirements.txt
   ```
Set up environment variables — create a `.env` file in the root:
```
   SECRET_KEY=your_secret_key
   DATABASE_URL=sqlite:///./expense_tracker.db
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```
Run the server
```bash
   uvicorn app.main:app --reload
   ```
Open the API docs
```
   http://localhost:8000/docs
   ```
API Overview
Method	Endpoint	Description	Auth
POST	`/auth/register`	Create account	Public
POST	`/auth/login`	Login, get JWT	Public
GET	`/expenses`	List expenses	Required
POST	`/expenses`	Add expense	Required
PUT	`/expenses/{id}`	Update expense	Required
DELETE	`/expenses/{id}`	Delete expense	Required
GET	`/categories`	List categories	Required
POST	`/categories`	Add category	Required
GET	`/budgets`	List budgets	Required
POST	`/budgets`	Set budget	Required
Deployment
Backend is deployed on Render.  
Frontend (Next.js) is deployed on Vercel — cashually.vercel.app
