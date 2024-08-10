# %%
import os
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import datetime
import pytz
import re
import time

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数から認証情報を取得
CREDENTIALS_FILE = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
SPREADSHEET_KEY = os.environ.get('SPREADSHEET_KEY')
WORKSHEET_NAME = os.environ.get('WORKSHEET_NAME')

# 2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
scope = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']

# 環境変数から取得したファイルパスを使用
credentials = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scope)

# OAuth2の資格情報を使用してGoogle APIにログイン。
gs = gspread.authorize(credentials)

def get_df():
    # 環境変数から取得したスプレッドシートキーを使用
    workbook = gs.open_by_key(SPREADSHEET_KEY)
    worksheet = workbook.worksheet(WORKSHEET_NAME)
    # スプレッドシートをDataFrameに取り込む
    return pd.DataFrame(worksheet.get_all_values()[4:], columns=worksheet.get_all_values()[3])

# %%
# dfの月日コラムからdatetime型の月日（年は1900）のリストを返す
def get_date(df):
    return pd.to_datetime(df['月日'], format='%m月%d日')

# %%
# 今年度は何年度か求める
def get_thisyear():
    dt_now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    if 4 <= dt_now.month <=12:
        return dt_now.year
    else:
        return dt_now.year - 1

# datetime型のリストを引数に、月日に応じた適切な年を設定したリストを返す
def set_year(dt):
    thisyear = get_thisyear()
    #月から年を越してるか判断し、年を設定していく
    for i in range(len(dt)):
        if 4 <= dt[i].month <=12:
            dt[i] = dt[i].replace(year=thisyear)
        else:
            dt[i] = dt[i].replace(year=thisyear + 1)
    
    return dt

# %%
# datetime型のインデックスを設定したDataFrameを返す
def set_datetime_index(df):
    dt = get_date(df)
    dt = set_year(dt)
    df = df.drop("月日", axis=1)
    df = df.set_index(dt)
    return df

# %%
# 第一引数に特定の日付をdate型、もしくはdatetime型で記入
# 第二引数に開始させたい曜日を"Sunday", "Monday"などで記入
# "Sunday", "Monday"など以外は入力を受け付けない。
# 戻り値はタプルで("開始日","終了日")を返す。
# 戻り値のデータ型は第一引数と同じ
def get_thisweek(date_,start_weekday=""):
    date_weekday=date_.weekday()
    weekdays = {"Monday":0, "Tuesday":1, "Wednesday":2, "Thursday":3, "Friday":4, "Saturday":5, "Sunday":6}
    try:
        start_weekday_num = weekdays[start_weekday]
    except:
        start_weekday_num = weekdays["Saturday"]
        # if start_weekday == "":
        #     print("開始曜日は省略されたので土曜日としました。")
        # else:
        #     print("開始曜日が\"Sunday\"などではなかったので土曜日としました。")
    if start_weekday_num <= date_weekday:
        dif_date = start_weekday_num - date_weekday
    else:
        dif_date = start_weekday_num - date_weekday - 7
    start_day = date_ + datetime.timedelta(days=dif_date)
    last_day = start_day + datetime.timedelta(days=6)
    return start_day,last_day

# %%
# dfのうちインデックスが日付dtstrと同じ週であるものを抽出したDataFrameを返す
# dtstrは西暦-月-日の形式。形式外の場合は今日の日付になる。
def get_thisweek_df(df, dtstr="", start_weekday=""):
    try:
        dt = datetime.datetime.strptime(dtstr,"%Y-%m-%d")
    except:
        try:
            dt = datetime.datetime.strptime(dtstr,"%m-%d")
            if 4 <= dt.month <=12:
                dt = dt.replace(year=get_thisyear())
            else:
                dt = dt.replace(year=get_thisyear() + 1)
        except:
            dt_now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
            dt = dt_now + datetime.timedelta(hours=6)
            dt = dt.date()
            # if dtstr == "":
            #     print("日付は省略されたので今日の日付を用いました。")
            # else:
            #     print("日付の値が様式\"西暦-月-日\"に従っていないので今日の日付を用いました。")
    df = set_datetime_index(df)
    thisweek = get_thisweek(dt,start_weekday)
    df = df[thisweek[0]:thisweek[1]]
    return df

# %%
# dfから不要な列を削除したDataFrameを返す
def del_colums(df):
    del df["講座名"]
    del df["担当教員名"]
    del df["職名"]
    del df[""]
    del df["講義題目"]
    return df

# %%
def join_sameclass(df):
    df = df.reset_index()
    i = 0
    while i < len(df) - 1:
        j = i + 1
        while j < len(df) and \
              df.loc[i, "科目名"] == df.loc[j, "科目名"] and \
              df.loc[i, "曜日"] == df.loc[j, "曜日"] and \
              df.loc[i, "実施場所"] == df.loc[j, "実施場所"]:
            j += 1
        
        if j - i > 1:
            df.loc[i, "時限"] = df.loc[i, "時限"] + "-" + df.loc[j-1, "時限"]
            df = df.drop(index=range(i+1, j))
            df = df.reset_index(drop=True)
        
        i += 1
    
    # return df.set_index("月日")
    return df

# %%
# dfのindex行目の直後にリストvalueをnum行挿入する。
# リストvalueの要素数はdfの列数と同数にせよ。
def insert(df, index, value, num=1):
    # index 行目までを抽出し、その直後に行を追加する。
    df1 = df.iloc[:index+1]
    blankrow = pd.DataFrame(data=[value]*num,columns=df.columns)
    df1 = pd.concat((df1,blankrow), ignore_index=True, axis=0)
    # index + 1 行目以降を抽出する。
    df2 = df.iloc[index+1:]
    # 縦方向に結合する。
    df_concat = pd.concat((df1, df2)).reset_index(drop=True)
    
    return df_concat

# %%
# 日付が異なる連続行の間に空行を挿入する。
# さらに同じ日付が連続して表示される文を削除する。
def make_blankrow(df, num=1):
    i = 0
    ls = [0]
    while i < len(df) - 1:
       #連続の行で日付が異なるならば
        if df.loc[i,"日付"] != df.loc[i+1,"日付"]:
            df = insert(df,i,[None]*len(df.columns),num)
            # 空行の先の行目を記録
            ls.append(i+num+1)
            i += num
        i += 1
    # つぎに同じ日付の連続は最初だけ表示する。
    for j in range(len(ls)):
        df.iloc[ls[j]+1:ls[j+1] if j < len(ls)-1 else None,0]= None
    return df

# %%
# get_calender(df,dtstr)の形で記述。dtstrは省略可
# 日付dtstrが含まれる週の簡素時間割をDataFrameで出力する
# 引数dfはNUCT時間割のDataFrame。省略不可
# 引数dtstrは月-日の形式。形式外や省略した場合は今日の日付になる
def get_calender(df,dtstr=None):
    df = get_thisweek_df(df, dtstr, "Saturday")
    df = del_colums(df)
    df = join_sameclass(df)
    df["月日"] = [df.loc[i,"月日"].strftime("%m月%d日") + df.loc[i,"曜日"] for i in range(len(df))]
    del df["曜日"]
    df = df.rename(columns={"月日": "日付"})
    df = make_blankrow(df,2)
    return df

# %%
def get_the_calender():
    dtstr = input("日付を\"西暦-月-日\"の形式で入力してください（西暦は省略可）")
    return get_calender(get_df(),dtstr)

# %%
def update_spreadsheet(thisweek_df):
    # スプレッドシートIDを変数に格納する。
    SPREADSHEET_KEY = '1wlaknyDTFavd-k-YITlGyrFuIDn-XzhSp45QIysNriM'
    # ワークブックを開く
    workbook = gs.open_by_key(SPREADSHEET_KEY)

    # 存在するワークシートの情報を全て取得
    worksheets = workbook.worksheets()
    # 現在のワークシートのタイトルをリストへ格納
    tmp_worksheets_title_list = [worksheet.title for worksheet in worksheets]
    # 今週の月曜日の日付を求める。
    dt_now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    dt = dt_now + datetime.timedelta(hours=6)
    dt = dt.date()
    Saturday = get_thisweek(dt)[0]
    Monday = Saturday + datetime.timedelta(days=2)
    Monday = Monday.strftime("%Y/%m/%d")
    # 今週分のシートが作成済みなら中断
    if Monday not in tmp_worksheets_title_list:    
        # 月曜日の日付をタイトルにシート作成
        workbook.add_worksheet(title=Monday,rows=0,cols=0)

    # 存在するワークシートの情報を全て取得
    worksheets = workbook.worksheets()
    # 現在のワークシートのタイトルをリストへ格納
    tmp_worksheets_title_list = [worksheet.title for worksheet in worksheets]
    # タイトルを降順ソート
    worksheets_title_list = sorted(tmp_worksheets_title_list, reverse=True)
    # Worksheet型オブジェクトをソートした順序でリストへ格納
    worksheets_obj_list = [worksheet for title in worksheets_title_list for worksheet in worksheets if worksheet.title == title]
    # ワークシートをソート
    workbook.reorder_worksheets(worksheets_obj_list)

    # 新規作成分のシートを開く
    worksheet = workbook.worksheet(Monday)

    # ワークシートをクリアする
    worksheet.clear()

    start_cell = 'A3' # 列はA〜Z列まで
    start_cell_col = re.sub(r'[\d]', '', start_cell)
    start_cell_row = int(re.sub(r'[\D]', '', start_cell))

    def toAlpha(num):
        if num<=26:
            return chr(64+num)
        elif num%26==0:
            return toAlpha(num//26-1)+chr(90)
        else:
            return toAlpha(num//26)+chr(64+num%26)
    
    col_lastnum = len(thisweek_df.columns) # DataFrameの列数
    row_lastnum = len(thisweek_df.index)   # DataFrameの行数

    # アルファベットから数字を返すラムダ式(A列～Z列まで)
    # 例：A→1、Z→26
    alpha2num = lambda c: ord(c) - ord('A') + 1

    # 展開を開始するセルからA1セルの差分
    row_diff = start_cell_row-1
    col_diff = alpha2num(start_cell_col)-alpha2num('A')

    # DataFrameのヘッダーと中身をスプレッドシートのA2セルから展開する
    cell_list = worksheet.range(start_cell+':'+toAlpha(col_lastnum+col_diff)+str(row_lastnum+1+row_diff))
    for cell in cell_list:
        if cell.row == 1+row_diff:
            val = thisweek_df.columns[cell.col-(1+col_diff)]
        else:
            val = thisweek_df.iloc[cell.row-(2+row_diff)][cell.col-(1+col_diff)]
        cell.value = val

    worksheet.update_cells(cell_list)
    
    # 新しいセルの位置を計算
    today = datetime.datetime.now()

    # 日付と曜日を挿入
    worksheet.update('A1', [[today.strftime('%m/%d (%a)')]])
    # 時刻を挿入
    worksheet.update('B1', [[today.strftime('%H:%M 時点')]])
    # # from Lecunを挿入
    # worksheet.update('C1', [['from LeCun']])


# %%
# 無限ループでスケジュールされたタスクを実行

while True:
    df = get_df()
    calendar = get_calender(df)
    update_spreadsheet(calendar)
    del df
    del calendar
    time.sleep(3600)


