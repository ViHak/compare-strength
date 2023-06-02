import pandas as pd
import sqlite3 as sql
import numpy as np
import matplotlib.pyplot as plt
import polars as pl
from scipy.stats import percentileofscore

db_path = 'powerlifting.db'
conn = 'sqlite://'+db_path

query = """SELECT field2, field4, field8, field14, field24, field19
FROM openpowerlifting"""

df = pl.read_sql(query, conn)
df = df[1:,:]

# TODO: Do this with SQL instead
df = df.filter((pl.col("field4")=="Raw") | (pl.col("field4")=="Wraps"))
df = df.with_columns(pl.col('field8').cast(pl.Float32, strict=False))

#df = df.filter(pl.col("field2")=="M")

def pick_weight_class(body_weight, sex):
    weight_class = 40
    if(sex=="M"):
        weight_classes = [59, 66, 74, 83, 93, 105, 120, 121]
    else:
        weight_classes = [47, 52, 57, 63, 69, 76, 84, 85]    

    index = 0
    for i in range(len(weight_classes)-1):
        if body_weight > weight_classes[i]:
            weight_class = weight_classes[i+1]
            index = i+1
        
    return index, weight_class

def change_data(index, weight_classes, hf, lift):
    if(index==0):
        return hf.filter((pl.col("field8")<=53))
    
    elif(index == len(weight_classes)-1):
        return hf.filter((pl.col("field8")>120))
    
    else:
        return hf.filter((pl.col("field8")>weight_classes[index-1]) & (pl.col("field8")<= weight_classes[index]))


def correct_field(hf, lift):
    match lift:
        case "bench":
            hf = hf.with_column(pl.col('field19').cast(pl.Float32, strict=False))
            hf = hf.filter(pl.col("field19")>0)
            hf = hf.drop_nulls(subset=['field19'])
            
            return hf.select("field19")
        
        case "squat":
            hf = hf.with_column(pl.col('field14').cast(pl.Float32, strict=False))
            hf = hf.filter((pl.col("field14")>0))
            hf = hf.filter((pl.col("field4")=="Raw"))
            
            hf = hf.drop_nulls(subset=['field14'])
            
            return hf.select("field14")
        
        case "deadlift":
            hf = hf.with_column(pl.col('field24').cast(pl.Float32, strict=False))

            hf = hf.filter((pl.col("field24")>0))
            hf = hf.drop_nulls(subset=['field24'])
            return hf.select("field24")

def select_sex(sex):
    if(sex == "M"):
        return df.filter(pl.col("field2")=="M")
    else:
        return df.filter(pl.col("field2")=="F")

# TODO: Passing DF as an argument here doesn't really make sense (?) since it can be accessed
# from inside the function anyways, remove it
def percentile_of_score(body_weight, bench, lift, sex):

    df = select_sex(sex)
    weight_class = 0
    weight_classes = [53, 59, 66, 74, 83, 93, 105, 120, 121]
    index, weight_class = pick_weight_class(body_weight, sex)

    df = change_data(index, weight_classes, df, lift)

    correctField = correct_field(df, lift)

    percentile = percentileofscore(correctField.to_pandas().squeeze(), int(bench), kind = "weak")

    return round(percentile, 0)