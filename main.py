from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
import json
from typing import List
from typing import Optional

app = FastAPI(title="Expense Tracker API")

# Templates & static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

DATA_FILE = "data.json"

class Expense(BaseModel):
    amount: float
    category: str
    date: Optional[str] = None


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
def add_expense(
    amount: float = Form(...),
    category: str = Form(...)
):
    data = load_data()

    expense_dict = {
        "amount": amount,
        "category": category,
        "date": datetime.now().strftime("%Y-%m")
    }

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
