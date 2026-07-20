import pandas as pd

def selectData(students: pd.DataFrame) -> pd.DataFrame:
    col = students['student_id']
    bools = col == 101
    result = students.loc[bools, ['name', 'age']]
    return result