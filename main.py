# All expenses page

# Monthly summary form and result
from fastapi.responses import RedirectResponse
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
import json
from typing import List
from typing import Optional
from fastapi import Form
app = FastAPI(title="Expense Tracker API")




# Templates & static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

DATA_FILE = "data.json"

class Expense(BaseModel):
    amount: float
    category: str
    date: Optional[str] = None
    
    
    
@app.get("/all-expenses", response_class=HTMLResponse)
def all_expenses(request: Request):
    data = load_data()
    return templates.TemplateResponse("all_expenses.html", {"request": request, "expenses": data})
@app.get("/monthly-summary", response_class=HTMLResponse)
def monthly_summary_form(request: Request):
    return templates.TemplateResponse("monthly_summary.html", {"request": request})

@app.post("/monthly-summary", response_class=HTMLResponse)
def monthly_summary_post(request: Request, month: str = Form(...)):
    data = load_data()
    # Filter expenses for the selected month (YYYY-MM)
    filtered = [exp for exp in data if exp.get("date", "").startswith(month)]
    total_expenses = sum(exp["amount"] for exp in filtered)
    transaction_count = len(filtered)
    # Category breakdown
    category_breakdown = {}
    for exp in filtered:
        cat = exp["category"]
        category_breakdown[cat] = category_breakdown.get(cat, 0) + exp["amount"]
    # Top category
    top_category = max(category_breakdown, key=category_breakdown.get) if category_breakdown else None
    summary = {
        "month": month,
        "total_expenses": total_expenses,
        "transaction_count": transaction_count,
        "top_category": top_category,
        "category_breakdown": category_breakdown
    }
    return templates.TemplateResponse("monthly_summary.html", {"request": request, "summary": summary})



def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@app.post("/expenses")
def add_expense(expense: Expense):
    data = load_data()
    expense_dict = expense.dict()

    if not expense_dict.get("date"):
        expense_dict["date"] = datetime.now().strftime("%Y-%m")

    data.append(expense_dict)
    save_data(data)

    return {"status": "success", "expense": expense_dict}


@app.get("/expenses", response_model=List[Expense])
def get_expenses():
    return load_data()


@app.get("/summary/monthly/{month}")
def monthly_summary(month: str):
    total = sum(
        exp["amount"] for exp in load_data() if exp.get("date") == month
    )
    return {"month": month, "total": total}


@app.get("/summary/category")
def category_summary():
    summary = {}
    for exp in load_data():
        cat = exp["category"]
        summary[cat] = summary.get(cat, 0) + exp["amount"]
    return summary

# -------------------- AUTHENTICATION (JWT) --------------------
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import timedelta

SECRET_KEY = "change-this-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
USERS_FILE = "users.json"


def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)


def authenticate_user(username: str, password: str):
    users = load_users()
    for u in users:
        if u["username"] == username and verify_password(password, u["password"]):
            return u
    return None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    users = load_users()
    for u in users:
        if u["username"] == username:
            return u
    raise credentials_exception


@app.post("/register")
def register(username: str = Form(...), password: str = Form(...)):
    users = load_users()

    for u in users:
        if u["username"] == username:
            raise HTTPException(status_code=400, detail="User already exists")

    users.append({
        "username": username,
        "password": hash_password(password)
    })

    save_users(users)
    return {"message": "User registered successfully"}


@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_access_token({"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


# -------------------- PROTECTED EXPENSE ENDPOINT --------------------
@app.post("/secure/expenses")
def add_expense_secure(
    amount: float = Form(...),
    category: str = Form(...),
    user: dict = Depends(get_current_user)
):
    data = load_data()

    expense_dict = {
        "amount": amount,
        "category": category,
        "date": datetime.now().strftime("%Y-%m"),
        "user": user["username"]
    }

    data.append(expense_dict)
    save_data(data)

    return {"status": "saved", "expense": expense_dict}

@app.get("/secure/expenses")
def get_expenses_secure(user: dict = Depends(get_current_user)):
    data = load_data()
    user_expenses = [exp for exp in data if exp.get("user") == user["username"]]
    return user_expenses

