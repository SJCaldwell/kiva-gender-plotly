import numpy as np
import pandas as pd
import pandas_profiling
import matplotlib.pyplot as plt

df = pd.read_csv("./data/kiva_loans.csv", parse_dates=True)

def split_borrower_gender(l):
    m = 0
    f = 0
    if type(l) != list:
        return np.nan
    for i in l:
        if i== 'male':
            m += 1
        else:
            f += 1
    if m == 0:
        return 'female'
    elif f == 0:
        return 'male'
    else:
        return 'both'

df.borrower_genders = df.borrower_genders.str.split(', ').apply(split_borrower_gender)

gensec = df.groupby('borrower_genders')['sector'].value_counts()
gensec = gensec.unstack().transpose()

df['disbursed_year'] = pd.to_datetime(df.disbursed_time).dt.year

fig = plt.figure(figsize=(12,6))
plt.plot(gensec.apply(lambda row: row/gensec.sum(1)));
plt.legend(['both', 'female', 'male']);
plt.xticks(rotation=60);
plt.show()
