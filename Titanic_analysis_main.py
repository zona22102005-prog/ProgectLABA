import numpy as np
import pandas as pd
pd.options.display.max_rows = 10
a=pd.read_csv('gender_submission.csv',engine='pyarrow',nrows=5)
b=pd.Series(a)
print(b)
print(b)

