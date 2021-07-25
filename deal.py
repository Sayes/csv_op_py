#-*- coding=utf-8 -*-
#
# MIN_FZ	最小负债率 （资产负债率 = 负债/资产）
# MIN_GXL	最小股息率
# MIN_JJB	最小净价比 （净价/价格）
# MIN_JYL	最小净益率
# MIN_WFB	最小未分比 （未分配利润/价格）
# MIN_LRTB	最小利润同比
# MIN_MLL	最小毛利率
# MAX_MLL	最大毛利率
#

import sys
import pandas as pd
from io import StringIO, BytesIO
import json

pd.set_option('display.width', 120)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', 16)
pd.set_option('display.precision', 2)
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.width', 160)


f = open(sys.argv[2], 'r')
json_txt = f.read()
f.close()
T = json.loads(json_txt)

data = pd.read_csv(sys.argv[1], sep=",", encoding="GB18030", header=0, dtype={'代码':str})
df = pd.DataFrame(data, columns=['代码', '名称', '市盈(TTM)','资产负债率%','每股净资','现价','股息率%','净益率%','地区','细分行业','每股收益','每股未分配','每股公积','AB股总市值','上市日期','市净率','净利润率%','毛利率%','利润同比%'])
print(df.shape[0:1])

#df['上市日期'] = pd.to_datetime(df['上市日期'])

df = df[(df['市盈(TTM)'] != '--  ')]
print(df.shape[0:1], ' TTM elim --')

# 如果 MIN_JYL = 0, 则不考虑这项指标
if T['MIN_JYL'] > 0:
	df = df[(df['净益率%']   != '--  ')]
	print(df.shape[0:1], ' JYL elim --')


# 如果 MIN_MLL = 0, 则不考虑这项指标
if T['MIN_MLL'] > 0:
	df = df[(df['毛利率%']   != '--  ')]
	print(df.shape[0:1], ' MLL elim --')

df['净益率%'] = df['净益率%'].str.replace('㈠','')
df['净益率%'] = df['净益率%'].str.replace('㈡','')
df['净益率%'] = df['净益率%'].str.replace('㈢','')
df['净益率%'] = df['净益率%'].str.replace('㈣','')

df['每股收益'] = df['每股收益'].str.replace('㈠','')
df['每股收益'] = df['每股收益'].str.replace('㈡','')
df['每股收益'] = df['每股收益'].str.replace('㈢','')
df['每股收益'] = df['每股收益'].str.replace('㈣','')

df['AB股总市值'] = df['AB股总市值'].str.replace('亿','')

df[['市盈(TTM)','股息率%','AB股总市值','每股净资','每股收益','每股未分配','每股公积']] = df[['市盈(TTM)','股息率%','AB股总市值','每股净资','每股收益','每股未分配','每股公积']].apply(pd.to_numeric)

# 如果 MIN_JYL = 0, 则不考虑这项指标
if T['MIN_JYL'] > 0:
	df[['净益率%']] = df[['净益率%']].apply(pd.to_numeric)
# 如果 MIN_MLL = 0, 则不考虑这项指标
if T['MIN_MLL'] > 0:
	df[['毛利率%']] = df[['毛利率%']].apply(pd.to_numeric)

df['未分比'] = df['每股未分配'] / df['现价']
df['净价比'] = df['每股净资'] / df['现价']

df = df[(df['未分比'] > float(T['MIN_WFB'])) & (df['未分比'] < float(T['MAX_WFB']))]
print(df.shape[0:1], ' WFB')

df = df[(df['净价比'] > float(T['MIN_JJB'])) & (df['净价比'] < float(T['MAX_JJB']))]
print(df.shape[0:1], 'JJB')

df = df[(df['股息率%'] > float(T['MIN_GXL']))]
print(df.shape[0:1], 'GXL')

# 如果 MIN_JYL = 0, 则不考虑这项指标
if T['MIN_JYL'] > 0:
	df = df[(df['净益率%'] > float(T['MIN_JYL']))]
	print(df.shape[0:1], ' JYL')

df = df[(df['资产负债率%'] > T['MIN_FZ']) & (df['资产负债率%'] < T['MAX_FZ'])]
print(df.shape[0:1], ' FZ')

df = df[(df['AB股总市值'] > T['MIN_ZSZ'])]
print(df.shape[0:1], ' ZSZ')

df = df[(df['市盈(TTM)'] > T['MIN_TTM']) & (df['市盈(TTM)'] < T['MAX_TTM'])]
print(df.shape[0:1], ' TTM')

df = df[(df['利润同比%'] > T['MIN_LRTB'])]
print(df.shape[0:1], ' LRTB')

# 如果 MIN_MLL = 0, 则不考虑这项指标
if T['MIN_MLL'] > 0:
	df = df[(df['毛利率%'] > T['MIN_MLL']) & (df['毛利率%'] < T['MAX_MLL'])]
	print(df.shape[0:1], ' MLL')

df = df[~df['地区'].isin(T['OUT_AREA'])]
print(df.shape[0:1], ' AREA')

df = df[~df['细分行业'].isin(T['OUT_INDUS'])]
print(df.shape[0:1], ' INDUS')

# 排序
df = df.sort_values(by = T['ORDER_BY'], ascending=T['ASCENDING'])

print(df[T['DISP_COLS']])
#print(df[T['DISP_CODE']])
