#-*- coding=utf-8 -*-
#
# MIN_FZ       最小负债率 （资产负债率 = 负债/资产）
# MIN_ZSZ      最小总市值
# MIN_GXL      最小股息率
# MIN_JJB      最小净价比 （净值/价格）
# MIN_JYL      最小净益率
# MIN_WFB      最小未分比 （未分配利润/价格）
# MIN_LRTB     最小利润同比
# MIN_MLL      最小毛利率
# MAX_MLL      最大毛利率
# MAX_YZB      最大应总比（应收账款/总资产）
#
# 更新说明
# 2023年5月5日（包含）之后的title中，“AB股总市值”改为“总市值”

import sys
import pandas as pd
from io import StringIO, BytesIO
import json

def main(csv_fn, strategy_fn):
  pd.set_option('display.width', 120)
  pd.set_option('display.max_rows', None)
  pd.set_option('display.max_columns', None)
  pd.set_option('display.max_colwidth', 16)
  pd.set_option('display.precision', 2)
  pd.set_option('display.unicode.ambiguous_as_wide', True)
  pd.set_option('display.unicode.east_asian_width', True)
  pd.set_option('display.width', 160)


  f = open(strategy_fn, 'r')
  json_txt = f.read()
  f.close()
  T = json.loads(json_txt)

  data = pd.read_csv(csv_fn, sep=",", encoding="GB18030", header=0, dtype={'代码':str})
  df = pd.DataFrame(data, columns=['代码', '名称', '市盈(TTM)','资产负债率%','每股净资','现价','股息率%','净益率%','地区','细分行业','每股收益','每股未分配','每股公积','总市值','总资产(亿)','应收账款(亿)','上市日期','市净率','净利润率%','毛利率%','利润同比%'])
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

  df['总市值'] = df['总市值'].str.replace('亿','')

  df[['市盈(TTM)','股息率%','总市值','总资产(亿)','应收账款(亿)','每股净资','每股收益','每股未分配','每股公积','市净率']] = df[['市盈(TTM)','股息率%','总市值','总资产(亿)','应收账款(亿)','每股净资','每股收益','每股未分配','每股公积','市净率']].apply(pd.to_numeric)

  df[['净益率%']] = df[['净益率%']].apply(pd.to_numeric)

  # 如果 MIN_MLL = 0, 则不考虑这项指标
  if T['MIN_MLL'] > 0:
    df[['毛利率%']] = df[['毛利率%']].apply(pd.to_numeric)

  df['未分比'] = df['每股未分配'] / df['每股净资']
  df['净价比'] = 1/df['市净率']
  df['应总比'] = df['应收账款(亿)'] / df['总资产(亿)']

  df = df[(df['未分比'] > float(T['MIN_WFB'])) & (df['未分比'] < float(T['MAX_WFB']))]
  print(df.shape[0:1], ' WFB')

  df = df[(df['净价比'] > float(T['MIN_JJB'])) & (df['净价比'] < float(T['MAX_JJB']))]
  print(df.shape[0:1], 'JJB')

  df = df[(df['应总比'] < float(T['MAX_YZB']))]
  print(df.shape[0:1], 'YZB')

  df = df[(df['股息率%'] > float(T['MIN_GXL']))]
  print(df.shape[0:1], 'GXL')

  df = df[(df['净益率%'] > float(T['MIN_JYL']))]
  print(df.shape[0:1], ' JYL')

  df = df[(df['资产负债率%'] > T['MIN_FZ']) & (df['资产负债率%'] < T['MAX_FZ'])]
  print(df.shape[0:1], ' FZ')

  df = df[(df['总市值'] > T['MIN_ZSZ']) & (df['总市值'] < T['MAX_ZSZ'])]
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

  print('=========================')

if __name__ == '__main__':
  main(sys.argv[1], sys.argv[2])
