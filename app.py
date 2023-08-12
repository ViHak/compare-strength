from flask import Flask, request, jsonify, render_template, url_for
import sqlite3 as sql
from percentile import *
from fastapi import FastAPI
from starlette.requests import Request
import starlette
from fastapi.templating import Jinja2Templates
import uvicorn
from fastapi.staticfiles import StaticFiles

templates = Jinja2Templates(directory="templates")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get('/')
async def index(request: Request):
    return templates.TemplateResponse('index.html', {"request":request})

@app.get('/get_percentile')
def get_percentile(request: Request):
    weight_class = int(request.query_params.get('weight_class'))
    lifted_weight = (request.query_params.get('lifted_weight'))
    lift = (request.query_params.get('lift'))
    sex = request.query_params.get('sex')
    division = request.query_params.get('division')
    
    # Used for determining whether the user wants to calculate the % of a given lift/weight or the other way around
    calculating_method = request.query_params.get('calculating_method')

    score = percentile_of_score(weight_class, lifted_weight, lift, sex, division, calculating_method)
    
    return ({"result":score})

if __name__ == "__main__":
   uvicorn.run("app:app")