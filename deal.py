#-*- coding=utf-8 -*-
import sys
import pandas as pd
from io import StringIO, BytesIO
import json

pd.set_option('display.width', 120)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', 16)
pd.set_option('display.precision', 2)

f = open(sys.argv[1], 'r')
json_txt = f.read()
f.close()

T = json.loads(json_txt)

data = pd.read_csv(sys.argv[2], sep=",", encoding="GB18030", header=0, dtype={'代码':str})

df = pd.DataFrame(data, columns=['代码', '名称', '市盈(TTM)','资产负债率%','每股净资','现价','地区','细分行业','每股收益','每股未分配','每股公积','总资产(亿)'])
print(df.shape)

df = df[(df['市盈(TTM)'] != '--  ')]
print(df.shape)

df['每股收益'] = df['每股收益'].str.replace('㈠','')
df['每股收益'] = df['每股收益'].str.replace('㈢','')
df['每股收益'] = df['每股收益'].str.replace('㈣','')
df[['市盈(TTM)','每股净资','每股收益','每股未分配','每股公积']] = df[['市盈(TTM)','每股净资','每股收益','每股未分配','每股公积']].apply(pd.to_numeric)
df['实价比'] = (df['每股净资'] + df['每股收益'] + df['每股未分配'] + df['每股公积'])/df['现价']
df = df[(df['实价比'] > float(T['MIN_SJB'])) & (df['实价比'] < float(T['MAX_SJB']))]
print(df.shape)

df = df[(df['资产负债率%'] > T['MIN_FZ']) & (df['资产负债率%'] < T['MAX_FZ'])]
print(df.shape)
df[['市盈(TTM)','每股净资','每股收益','每股未分配','每股公积']] = df[['市盈(TTM)','每股净资','每股收益','每股未分配','每股公积']].apply(pd.to_numeric)
df = df[(df['总资产(亿)'] > T['MIN_ZZC'])]
print(df.shape)
df['市盈(TTM)'] = df['市盈(TTM)'].apply(pd.to_numeric)
df = df[(df['市盈(TTM)'] > T['MIN_TTM']) & (df['市盈(TTM)'] < T['MAX_TTM'])]
print(df.shape)
df = df.sort_values(by = '市盈(TTM)')

print(df[T['DISP_COLS']])
