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

import sys
import pandas as pd
from io import StringIO, BytesIO
import json
from enum import Enum

class SectionID(Enum):
    SECTION_SH_A   = 1
    SECTION_SZ_A   = 2
    SECTION_SZ_ZXB = 3
    SECTION_SZ_CYB = 4
    SECTION_SH_KCB = 5


def get_section(stock_code):
    if (stock_code[:2] in {"60"}):
        return SectionID.SECTION_SH_A, "SH"
    if (stock_code[:3] in {"000", "001"}):
        return SectionID.SECTION_SZ_A, "SZ"
    if (stock_code[:3] in {"002", "003"}):
        return SectionID.SECTION_SZ_ZXB, "SZ"
    if (stock_code[:3] in {"300", "301", "302"}):
        return SectionID.SECTION_SZ_CYB, "SZ"
    if (stock_code[:2] in {"68"}):
        return SectionID.SECTION_SH_KCB, "SH"
    return -1, ""


def main(csv_fn, strategy_fn):
  pd.set_option('display.max_rows', None)
  pd.set_option('display.max_columns', None)
  pd.set_option('display.max_colwidth', 16)
  pd.set_option('display.precision', 2)
  pd.set_option('display.unicode.ambiguous_as_wide', True)
  pd.set_option('display.unicode.east_asian_width', True)
  pd.set_option('display.width', 160)

  # open strategy file, with json
  f = open(strategy_fn, 'r')
  json_txt = f.read()
  f.close()
  T = json.loads(json_txt)

  # read preselect data, with csv, 文件标题栏格式: 代码,名称
  preselected = pd.read_csv("preselected.csv", sep=",", encoding="utf8", header=0, dtype={'代码':str})
  df_preselected = pd.DataFrame(preselected)

  # read stock data, with csv
  data = pd.read_csv(csv_fn, sep=",", encoding="GB18030", header=0, dtype={'代码':str,'员工人数':str})
  # df = pd.DataFrame(data, columns=['代码', '名称', '市盈(TTM)','资产负债率%','每股净资','现价','股息率%','净益率%','地区','细分行业','每股收益','每股未分配','每股公积',MC_COLUMN_NAME,'总资产(亿)','应收账款(亿)','上市日期','市净率','净利润率%','毛利率%','利润同比%'])
  df = pd.DataFrame(data)

  df['代码'] = df['代码'].astype(str).str.zfill(6)
  print(f"{df.shape[0]}\tINITIAL")

  MC_COLUMN_NAME = 'AB股总市值'
  if not MC_COLUMN_NAME in df:
      MC_COLUMN_NAME = '总市值'

  #df['上市日期'] = pd.to_datetime(df['上市日期'])

  # elimit 市盈(TTM) == '-- '
  df = df[(df['市盈(TTM)'] != '--  ')]
  print(f"{df.shape[0]}\tTTM elim --")

  # 如果 MIN_JYL = 0, 则不考虑这项指标
  if T['MIN_JYL'] > 0:
    df = df[(df['净益率%'] != '--  ')]
    print(f"{df.shape[0]}\tJYL elim --")


  # 如果 MIN_MLL = 0, 则不考虑这项指标
  if T['MIN_MLL'] > 0:
    df = df[(df['毛利率%'] != '--  ')]
    print(f"{df.shape[0]}\tMLL elim --")

  df['净益率%'] = df['净益率%'].str.replace('㈠','')
  df['净益率%'] = df['净益率%'].str.replace('㈡','')
  df['净益率%'] = df['净益率%'].str.replace('㈢','')
  df['净益率%'] = df['净益率%'].str.replace('㈣','')

  df['每股收益'] = df['每股收益'].str.replace('㈠','')
  df['每股收益'] = df['每股收益'].str.replace('㈡','')
  df['每股收益'] = df['每股收益'].str.replace('㈢','')
  df['每股收益'] = df['每股收益'].str.replace('㈣','')

  df[MC_COLUMN_NAME] = df[MC_COLUMN_NAME].str.replace('亿','')

  df[['市盈(TTM)','股息率%',MC_COLUMN_NAME,'总资产(亿)','应收账款(亿)','每股净资','每股收益','每股未分配','每股公积','市净率']] = df[['市盈(TTM)','股息率%',MC_COLUMN_NAME,'总资产(亿)','应收账款(亿)','每股净资','每股收益','每股未分配','每股公积','市净率']].apply(pd.to_numeric)

  df[['净益率%']] = df[['净益率%']].apply(pd.to_numeric)

  # 如果 MIN_MLL = 0, 则不考虑这项指标
  if T['MIN_MLL'] > 0:
    df[['毛利率%']] = df[['毛利率%']].apply(pd.to_numeric)

  df['未分比'] = df['每股未分配'] / df['每股净资']
  df['净价比'] = 1/df['市净率']
  df['应总比'] = df['应收账款(亿)'] / df['总资产(亿)']

  df = df[(df['未分比'] > float(T['MIN_WFB'])) & (df['未分比'] < float(T['MAX_WFB']))]
  print(f"{df.shape[0]}\tWFB")

  df = df[(df['净价比'] > float(T['MIN_JJB'])) & (df['净价比'] < float(T['MAX_JJB']))]
  print(f"{df.shape[0]}\tJJB")

  df = df[(df['应总比'] < float(T['MAX_YZB']))]
  print(f"{df.shape[0]}\tYZB")

  df = df[(df['股息率%'] > float(T['MIN_GXL']))]
  print(f"{df.shape[0]}\tGXL")

  df = df[(df['净益率%'] > float(T['MIN_JYL']))]
  print(f"{df.shape[0]}\tJYL")

  df = df[(df['资产负债率%'] > T['MIN_FZ']) & (df['资产负债率%'] < T['MAX_FZ'])]
  print(f"{df.shape[0]}\tFZ")

  df = df[(df[MC_COLUMN_NAME] > T['MIN_ZSZ']) & (df[MC_COLUMN_NAME] < T['MAX_ZSZ'])]
  print(f"{df.shape[0]}\tZSZ")

  df = df[(df['市盈(TTM)'] > T['MIN_TTM']) & (df['市盈(TTM)'] < T['MAX_TTM'])]
  print(f"{df.shape[0]}\tTTM")

  df = df[(df['利润同比%'] > T['MIN_LRTB'])]
  print(f"{df.shape[0]}\tLRTB")

  # 如果 MIN_MLL = 0, 则不考虑这项指标
  if T['MIN_MLL'] > 0:
    df = df[(df['毛利率%'] > T['MIN_MLL']) & (df['毛利率%'] < T['MAX_MLL'])]
    print(f"{df.shape[0]}\tMLL")

  df = df[~df['地区'].isin(T['OUT_AREA'])]
  print(f"{df.shape[0]}\tAREA")

  df = df[~df['细分行业'].isin(T['OUT_INDUS'])]
  print(f"{df.shape[0]}\tINDUS")

  # 预选股票过滤
  preselected_code = df_preselected['代码'].unique()
  mask = df['代码'].isin(preselected_code)
  df = df[mask]
  print(f"{df.shape[0]}\tPRESELECTED")

  # 排序
  df = df.sort_values(by = T['ORDER_BY'], ascending=T['ASCENDING'])
  # 输出结果
  print('-------------------------')
  print(df[T['DISP_COLS']].to_string(index=False))

  print('=========================')


if __name__ == '__main__':
  main(sys.argv[1], sys.argv[2])
