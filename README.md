# compare-strength

## Description

This project was built with one particular goal in mind: To provide lifters from all around the world an objective way to determine how strong they are. The internet is full of strength standards that are more or less arbitrary, whereas the numbers here are based on actual data from thousands of powerlifting competitions from the past 50 years or so.

Only data from "raw" powerlifting competitions is included - raw meaning that no assisting equipment, such as [bench shirts](https://en.wikipedia.org/wiki/Bench_shirt) or squats suits, are allowed to be used in the competition.

This project can be ran locally but you can also try it [here](https://comparestrength.com/). The website is hosted on an Ubuntu-based VPS and it's built on [FastAPI](https://github.com/tiangolo/fastapi). [Gunicorn](https://github.com/benoitc/gunicorn) is being used as a process manager for the Uvicorn workers.

Data source: [https://www.kaggle.com/datasets/open-powerlifting/powerlifting-database](https://www.kaggle.com/datasets/open-powerlifting/powerlifting-database)

## Installing and running the project

```
git clone https://github.com/ViHak/compare-strength.git
cd compare-strength
pip install -r requirements.txt
python -m uvicorn app:app
```
You can also run the project programmatically with the IDE of your choice - simply just run the app.py file.

### Features

- [x] Choose gender
- [x] Filter results from tested and un-tested competitions
- [x] A toggle switch with the option to input percentile instead of a weight value. E.g. the user can choose to input a number x from the range [0, 100] to see how much they'd have to lift to be stronger than x% of people in their chosen weight class.
