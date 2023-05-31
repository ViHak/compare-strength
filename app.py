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
    bw = int(request.query_params['val1'])
    bench = int(request.query_params.get('val2'))
    name = (request.query_params.get('name'))
    sex = request.query_params.get('sex')
    score = percentile_of_score(bw, bench, name, sex)
    
    return ({"result":score})

if __name__ == "__main__":
   uvicorn.run("app:app")
    