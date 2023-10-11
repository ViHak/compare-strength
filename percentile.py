import pandas as pd
import sqlite3 as sql
import numpy as np
import matplotlib.pyplot as plt
import polars as pl
from scipy.stats import percentileofscore
from scipy.stats import scoreatpercentile


db_path = 'powerlifting.db'
conn = 'sqlite://'+db_path

query = """SELECT field2, field4, field8, field14, field24, field19, field31
FROM openpowerlifting"""

df = pl.read_database(query, conn)[1:,:]

# The field8 column has the lifter's bodyweight. Other columns (lifts) are casted to float
# later as needed. Only one lift is looked at a time so float casting all of them
# would be unnecessary
df = df.with_columns(pl.col('field8').cast(pl.Float32, strict=False))

def pick_weight_class(sex):
    if(sex=="M"):
        weight_classes = [59, 66, 74, 83, 93, 105, 120, 121]
    else:
        weight_classes = [47, 52, 57, 63, 69, 76, 84, 85]    

    return weight_classes

def change_data(weight_class, weight_classes, hf):
    match weight_class:
        # Since 59 is the smallest male weight class and there are no weight classes below that,
        # all rows, in which the field8 (Bodyweight) column's values are smaller than or equal to 59,
        # will be chosen. Same logic with the super heavyweight weight-classes. 
        case 59:
            return hf.filter((pl.col("field8")<=59))
        case 121:
            return hf.filter((pl.col("field8")>120))
        case 47:
            return hf.filter((pl.col("field8")<=47))
        case 85:
            return hf.filter((pl.col("field8")>84))
        # Example: If the 74kg weight class is chosen, the lifters bodyweight can be anything in the range of ]66, 74] kg.
        case _:
            return hf.filter((pl.col("field8")>weight_classes[weight_classes.index(weight_class)-1]) & (pl.col("field8")<= weight_classes[weight_classes.index(weight_class)]))

# Depending on the lift the user has chosen, the column that consists of the values of said lift
# will be casted to float and also cleaned from null values, so that the percentile can later be calculated.
def correct_field(hf, lift):
    match lift:
        case "bench":
            hf = hf.with_columns(pl.col('field19').cast(pl.Float32, strict=False))
            hf = hf.filter(pl.col("field19")>0)
            hf = hf.drop_nulls(subset=['field19'])
            
            return hf.select("field19")
        
        case "squat":
            hf = hf.with_columns(pl.col('field14').cast(pl.Float32, strict=False))
            hf = hf.filter((pl.col("field14")>0)&(pl.col("field4")=="Raw"))
            hf = hf.drop_nulls(subset=['field14'])
            
            return hf.select("field14")
        
        case "deadlift":
            hf = hf.with_columns(pl.col('field24').cast(pl.Float32, strict=False))
            hf = hf.filter((pl.col("field24")>0))
            hf = hf.drop_nulls(subset=['field24'])

            return hf.select("field24")

def select_sex(sex):
    return df.filter(pl.col("field2") == sex)

def percentile_of_score(weight_class, lifted_weight, lift, sex, division, calculating_method):
    df = select_sex(sex)
    if(division == "tested"):
        df =  df.filter(pl.col("field31") == "Yes")

    weight_classes = pick_weight_class(sex)

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