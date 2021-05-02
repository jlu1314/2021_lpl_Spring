# -*- coding = utf-8 -*-
# @Time :2021/1/16 22:53
# @AUthor : 王俊庆
# @File : lpl2021rank.py
# @Software : PyCharm
import requests
import re
from bs4 import BeautifulSoup
import xlwt
import sqlite3
import os


#正则表达式，字符串规则
#排名字符串规则
findpaiming=re.compile(r'<div.*?data-a-0147e6fc="">(\d*)?</div>')
#战队名称字符串规则
findname=re.compile(r'<div.*?data-a-0147e6fc="">([A-Z]\w*?)</div>')
#战队积分字符串规则
findscore=re.compile(r'<span.data-a-0147e6fc="">(\d*?|-\d.*?)</span>')

#<div class="c-span3 no1" data-a-0147e6fc="">1</div>
def askurl(url):
    try:
        kv={'user-agent':'Mozilla/5.0'}
        r=requests.get(url, headers=kv)
        r.raise_for_status()
        r.encoding=r.apparent_encoding
        return r.text
    except:
        return ''
def getdata(datalist,html):
    soup=BeautifulSoup(html,'html.parser')
    for item in soup.find_all('div',class_="c-row c-blocka"):
        data=[]
        item=str(item)
        # print(item)    #测试
        paiming=re.findall(findpaiming,item)
        # print(paiming)     #测试
        data.append(paiming[0])
        name=re.findall(findname,item)
        # print(name)
        data.append(name[0])
        score=re.findall(findscore,item)
        # print(score)
        data.append(score[3])
        datalist.append(data)
    # print(datalist)
    return datalist


def printdata(datalist):
    print('{:^5}\t{:^5}\t{:^13}'.format('排名','战队','积分'))
    for i in range(len(datalist)):
        #print(str(datalist[i][j]))
        print('{:^5}\t{:^5}\t{:^13}'.format(datalist[i][0],datalist[i][1],datalist[i][2]))


def SavetoExcel(datalist,savepath):
    workbook = xlwt.Workbook(encoding='utf-8',style_compression=0)  # 创建wookbook对象
    worksheet = workbook.add_sheet('2021lpl',cell_overwrite_ok=True)  # 创建工作表
    # wooksheet.write(0,0,'hello!这是第一个测试数据表')       #写入数据，第一个参数为行，第二个参数为列，第三个参数为写入的内容
    col=('排名','战队','积分')
    for i in range(len(col)):
        worksheet.write(0,i,col[i])     #列名
    for i in range(0,17):
        print("这是第%d条"%(i+1,))
        for j in range(len(col)-1):
            worksheet.write(i+1,j,datalist[i][j])
            worksheet.write(i + 1, 2, datalist[i][2][3])
    workbook.save(savepath)  # 保存数据表

def SavetoDB(datalist,DBpath):
    init_db(DBpath)
    conn=sqlite3.connect('lpl.db')
    cur=conn.cursor()
    for item in datalist:
        for i in range(len(item)):
            item[i]="'"+item[i]+"'"
        #print(item)
        #print(item[0],type(item[0]),item[1],type(item[1]),item[2],type(item[2]))
        # sql = '''
        # insert into lpl_rank (num,name,score)
        # values (eval(item[0]), "'"+item[1]+"'",eval(item[2]))
        # '''
        # insert into lpl_rank (num,name,score) values (item[0],item[1],item[2])
        # values ({},{},{})'''.format(item[0],item[1],item[2])
        sql='''
        insert into lpl_rank(num,name,score) values (%s)'''%','.join(item)
        #print(sql)
        cur.execute(sql)
        conn.commit()
    cur.close()
    conn.close()


def init_db(DBpath):
    sql1 = '''
    create table lpl_rank
    (
    id integer primary key autoincrement,
    num numeric ,
    name varchar ,
    score numeric 
    )
    '''
    sql2='''
    drop table lpl_rank
    '''
    if not os.path.exists(DBpath):
        conn=sqlite3.connect(DBpath)
        cur=conn.cursor()
        cur.execute(sql1)
        conn.commit()
        conn.close()
    else:
        conn = sqlite3.connect(DBpath)
        cur = conn.cursor()
        cur.execute(sql2)
        cur.execute(sql1)
        conn.commit()
        conn.close()

def main():
    url="https://tiyu.baidu.com/match/LPL/tab/%E6%8E%92%E5%90%8D/from/baidu_aladdin"
    datalist=[]
    html=askurl(url)
    savepath='2021lpl.xls'
    DBpath='lpl.db'
    getdata(datalist,html)
    # printdata(datalist)
    #SavetoExcel(datalist,savepath)
    SavetoDB(datalist, DBpath)
main()
print("数据库建立成功!")