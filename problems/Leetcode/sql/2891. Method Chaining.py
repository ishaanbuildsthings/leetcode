import pandas as pd

def findHeavyAnimals(animals: pd.DataFrame) -> pd.DataFrame:
    weightSeries = animals['weight']
    bools = weightSeries > 100 # boolean series of if we are >100kg
    heavyFullData = animals[bools] # all rows * columns when that row-th value is true from the boolean mask

    ordered = heavyFullData.sort_values('weight',ascending=False)
    result = ordered[ ['name'] ]
    return result
