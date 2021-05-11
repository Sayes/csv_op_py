#-*- coding=utf-8 -*-
import pandas as pd

pd.set_option('max_columns', 200)
pd.set_option('max_rows', 5000)
pd.set_option('display.float_format', lambda x: '%.2f' %x)

#df = pd.read_excel("./book1.xlsx", sheet_name='Sheet1')
file = pd.read_csv("./hushenA20210225.csv", encoding="GB18030", header=0)
df = pd.DataFrame(file)
items_cnt = len(df)

str_titles = str(df.ix[0])
titles = str_titles.split('\\t')
titles_cnt = len(titles) - 4

for i in range(0, titles_cnt - 1):
    if (str(titles[i]) == '代码'):
        print(titles[i], end='')
    if (str(titles[i]) == '市净率'):
        print(titles[i])


for row_idx in range (1, len(df) - 1):
    for col_idx in range (0, titles_cnt - 1):
        if (str(titles[col_idx]) == '代码'):
            print(str(df.ix[row_idx][0]).split('\t')[col_idx], end='')
        if (str(titles[col_idx]) == '市净率'):
            print(str(df.ix[row_idx][0]).split('\t')[col_idx])

row_idx = 1
column_idx = 0
print(str(df.ix[row_idx][0]).split('\t')[column_idx])

data1 = df.ix[0].values
data2 = df.ix[1].values

print("{0}".format(data1))
print("{0}".format(data2))


