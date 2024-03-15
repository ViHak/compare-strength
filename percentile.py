import pandas as pd
import sqlite3 as sql
import polars as pl
from scipy.stats import percentileofscore
from scipy.stats import scoreatpercentile

WEIGHT_CLASSES = {
    "M":[59, 66, 74, 83, 93, 105, 120, 121],
    "F":[47, 52, 57, 63, 69, 76, 84, 85]
}

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
        # all rows within the range )weight_class] will be chosen.
        case _:
            return hf.filter((pl.col("bodyweight")>weight_classes[weight_classes.index(weight_class)-1]) & (pl.col("bodyweight")<= weight_classes[weight_classes.index(weight_class)]))

# Depending on the lift the user has chosen, the column that consists of the values of said lift
# will be casted to float and also cleaned from null values, so that the percentile can later be calculated.
def correct_field(hf, lift):
    match lift:
        case "bench":
            return hf.filter(pl.col('bench_max')>0).select(pl.col('bench_max'))

        case "squat":
            hf = hf.filter(pl.col("equipment")=="Raw")
            return hf.filter(pl.col("squat_max")>0).select(pl.col('squat_max'))
        case "deadlift":
            return hf.filter(pl.col('deadlift_max')>0).select(pl.col('deadlift_max'))#.drop_nulls(subset=['deadlift_max'])

def percentile_of_score(df, weight_class, lifted_weight, lift, sex, division, calculating_method):
    df = df.filter(pl.col("sex") == sex)
    
    if(division == "tested"):
        df = df.filter(pl.col("drug_tested") == "Yes")

    weight_classes = WEIGHT_CLASSES[sex]

    df = change_data(weight_class, weight_classes, df)
    lift_df = correct_field(df, lift) 
    if(calculating_method == "weight-at-percentile"):
        # Calculates the amount of weight that needs to be lifted in order to be in the top x percentile
        # of the user's chosen weight class, where x is the user's given percentile
            result = scoreatpercentile(lift_df.to_series().to_numpy(), int(lifted_weight))
            return f"You'd have to {lift} more than {round(result)} kg to be stronger than {lifted_weight}% of people in the {weight_class} kg weight class"
    else:
        result = percentileofscore(lift_df.to_series().to_numpy(), int(lifted_weight), kind = "weak")
        return f"You can {lift} more than {round(result)}% of people in the {weight_class} kg weight class"