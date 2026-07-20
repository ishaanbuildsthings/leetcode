import pandas as pd

def pivotTable(weather: pd.DataFrame) -> pd.DataFrame:
    # this means:
    # go to the month row
    # go to the city column
    # write the temperature there
    return weather.pivot(index="month", columns="city", values="temperature")