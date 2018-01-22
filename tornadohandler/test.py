import time,pymysql,os
from  config import *
class Test_all(object):
    def __init__(self):
        pass
    def check(self):
        try:
            res=(self.test_mysql())
            print (res)
            res +=self.test_proxy()
            res +=self.test_cookies()
            res +=self.test_header()
            return(str(res))
        except Exception:
            return(str(res))
    def test_mysql(self):
        try:
            conn=pymysql.connect(**SQLCONFIG)
        except Exception:
            return ("mysql connect <font color=red size=12>Error!</font>,chect <font color=red>config.py</font> <br>")
        try:
            cursor=conn.cursor()
            cursor.execute("show tables from assistant")
            res = cursor.fetchall()
            print(res)
            conn.commit()
            cursor.close()
            conn.close()
            return ("MySQL connect OK <br>")
        except Exception:
            cursor.close()
            conn.close()
            return ("mysql connect Error,chect <font color=red>config.py</font> <br>")
    def test_proxy(self):
        try:
            conn = pymysql.connect(**SQLCONFIG)
            cursor = conn.cursor()
            cursor.execute('select id,ip ,port, speed  from proxys order by speed ')
            maxip = cursor.rowcount
            cursor.fetchone()
            print("ippool total has %s" % maxip)
            conn.commit()
            cursor.close()
            conn.close()
            return ("%s proxies are ready! <br>" % maxip)
        except Exception:

            cursor.close()
            conn.close()
            return ("proxy is not ready!!!! <font color=red size=12>Error!</font> <br>")

    def test_cookies(self):
        try:
            conn = pymysql.connect(**SQLCONFIG)
            cursor = conn.cursor()

            sql = ("select account,cookies from cookies where inuse='0'")
            cursor.execute(sql)
            maxid = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()
            res=('cookies pool has <font color=red size=12>%s</font> account free for using<br>' %maxid)
            return (res)
        except Exception:
            cursor.close()
            conn.close()
            return ('cookies pool <font color=red size=12>Error!</font><br>')
    def test_header(self):
        if get_header():
            return("header get OK<br>")
        else:
            return("Header get <font color=red size=12>Error!</font><br>")

