from fastapi import FastAPI, HTTPException
from typing import Dict, Any
import subprocess
import importlib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI()

# Example function 1: Simulate calling a Python program to retrieve information
def get_information(area: str) -> Dict[str, Any]:
    # Replace with actual logic or subprocess calls
    result = {"data": f"Information about {area}", "source": "InfoProgram.py"}
    return result

# Example function 2: Simulate calling another Python program for credit score
def get_credit_score(company: str) -> Dict[str, Any]:
    # Replace with actual logic or subprocess calls
    credit_module = importlib.import_module("CreditData")
    result = credit_module.get_current_credit_category(company)
    logger.info(result)
    result = {"data": result, "source": "CreditProgram.py"}
    return result

# Define FastAPI routes
@app.get("/information")
async def retrieve_information(area: str):
    try:
        result = get_information(area)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/credit-score")
async def retrieve_credit_score(company: str):
    try:
        result = get_credit_score(company)
        print(result)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI service!"}