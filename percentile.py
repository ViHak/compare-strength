import pandas as pd
import sqlite3 as sql
import numpy as np
import matplotlib.pyplot as plt
import polars as pl
from scipy.stats import percentileofscore
from scipy.stats import scoreatpercentile

WEIGHT_CLASSES = {
    "M":[59, 66, 74, 83, 93, 105, 120, 121],
    "F":[47, 52, 57, 63, 69, 76, 84, 85]
}

db_path = 'powerlifting.db'
conn = 'sqlite://'+db_path

query = """SELECT 
sex, 
equipment, 
bodyweight, 
squat_max, 
deadlift_max, 
bench_max, 
drug_tested
FROM openpowerlifting"""

df = pl.read_database(query, conn).with_columns(pl.col('bodyweight').cast(pl.Float32, strict=False))

def change_data(weight_class, weight_classes, hf):
    match weight_class:
        # Edge cases where the chosen weight class is either the smallest or largest
        # weight class of the chosen sex.
        case 59:
            return hf.filter((pl.col("bodyweight")<=59))
        case 121:
            return hf.filter((pl.col("bodyweight")>120))
        case 47:
            return hf.filter((pl.col("bodyweight")<=47))
        case 85:
            return hf.filter((pl.col("bodyweight")>84))
        
        # If the chosen weight class is between two weight classes (i.e., not the smallest or highest weight class),
        # all rows between )weight_class_
        case _:
            return hf.filter((pl.col("bodyweight")>weight_classes[weight_classes.index(weight_class)-1]) & (pl.col("bodyweight")<= weight_classes[weight_classes.index(weight_class)]))

# Depending on the lift the user has chosen, the column that consists of the values of said lift
# will be casted to float and also cleaned from null values, so that the percentile can later be calculated.
def correct_field(hf, lift):
    match lift:
        case "bench":
            return hf.select(pl.col('bench_max').cast(pl.Float32, strict=False)).filter(pl.col('bench_max')>0).drop_nulls(subset=['bench_max'])
        case "squat":
            hf = hf.filter(pl.col("equipment")=="Raw")
            return hf.select(pl.col('squat_max').cast(pl.Float32, strict=False)).filter(pl.col("squat_max")>0).drop_nulls(subset=['squat_max'])
        case "deadlift":
            return hf.select(pl.col('deadlift_max').cast(pl.Float32, strict=False)).filter(pl.col('deadlift_max')>0).drop_nulls(subset=['deadlift_max'])

def select_sex(sex):
    return df.filter(pl.col("sex") == sex)

def percentile_of_score(weight_class, lifted_weight, lift, sex, division, calculating_method):
    df = select_sex(sex)
    if(division == "tested"):
        df =  df.filter(pl.col("drug_tested") == "Yes")

    weight_classes = WEIGHT_CLASSES[sex]

    df = change_data(weight_class, weight_classes, df)
    lift_df = correct_field(df, lift) 
    if(calculating_method == "weight-at-percentile"):
        # Calculates the amount of weight that needs to be lifted in order to be in the top x percentile
        # of the user's chosen weight class, where x is the user's given percentile
        result = scoreatpercentile(lift_df.to_pandas().squeeze(), int(lifted_weight))
        return f"You'd have to {lift} more than {round(result)} kg to be stronger than {lifted_weight}% of people in the {weight_class} kg weight class"
    else:
        result = percentileofscore(lift_df.to_pandas().squeeze(), int(lifted_weight), kind = "weak")
        return f"You can {lift} more than {round(result)}% of people in the {weight_class} kg weight class"