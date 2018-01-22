from tornado import gen
import tornado.escape
import tornado.web
import tornado.ioloop
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor
from scraper.weibo_scraper import WeiBoScraper
from pools import cookies

from config import SQLCONFIG,TASK_SAVE_DIR
from tornadohandler.test import Test_all
import pymysql,threadpool,os


class BaseHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(10)
    SUPPORTED_METHODS = ("GET", "POST")

class ResetCookies(tornado.web.RequestHandler):
    def get(self):
        conn=pymysql.connect(**SQLCONFIG)
        cursor=conn.cursor()
        cursor.execute("update cookies set inuse= case when 1 then 0 end where id>0")
        conn.commit()
        cursor.close()
        conn.close()
        self.write("All cookies reset => Standby<br><font color=green>===============<br></font><a href='../test'>Test all function</a>")

class Testhandler(tornado.web.RequestHandler):
    def get(self):
        print ("start check")
        res=Test_all()
        result=res.check()
        self.write("Test result:<br><hr>"+result+"<br><font color=green>Check Finish<br></font>============<br><a href='./reset/cookies'>reset all cookies =>StandBy</a>")
class SetCookies(BaseHandler):
    @gen.coroutine
    def get(self):
        account = self.get_argument("account")
        get_data = {}
        cookies_str = ""
        for key in self.request.arguments:
            get_data[key] = self.get_arguments(key)
            # print(key, "=", get_data[key][0])
            if key == 'account' or key == 'password':
                pass
            else:
                cookies_str += key + '=' + get_data[key][0] + '; '
        print("url get到的数据:", cookies_str)

        result=self._callback(account,cookies_str)
        print (result)
        self.write(result)

    def _callback(self,Account,cookies_str):
        try:
            # save cookies to file
            # result = cookies.set_cookies_from_network(Account, cookies_str)
            # save cookies to Mysql
            result = cookies.set_cookies_to_mysql(Account, cookies_str)
            return (result)
        except Exception as e:
            print(e)
            print (e.args)

class Single(BaseHandler):
    @gen.coroutine
    def get(self):
        account = self.get_argument("account",default="default")
        targetId = self.get_argument("targetId",strip=True);
        startPage = int(self.get_argument("startPage"));
        totalPage = int(self.get_argument("totalPage",default='10000'));
        taskidtxt = str(targetId + ".txt")
        taskidpath = os.path.join(TASK_SAVE_DIR, taskidtxt)
        print(taskidpath)
        if os.path.exists(taskidpath):
            self.write(
                "targetid task is doing ,please check again<br>,or kill this task for restart.<a href='../kill/one?taskid=%s'>Kill %s</a> <br>" % (
                targetId, targetId))
            return False
        with open(taskidpath,'w'):
            pass
        result=("using account=<font color=green>%s</font>,<br>targetId=<font color=green>%s</font>,<br>Page from <font color=red>%s to %s</font>.." %(account,targetId,startPage,startPage+totalPage-1))
        # 异步调用
        tornado.ioloop.IOLoop.instance().add_callback(self._callback,account,targetId,startPage,totalPage)
        self.write(result)
    @run_on_executor()
    def _callback(self,account,targetId,startPage,totalPage):
        try:
            executor=WeiBoScraper(account=account,uuid=targetId,startPage=startPage,totalPage=totalPage)
            result=executor.crawl()
            if result:
                print("="*30)
                print ("||  using account=%s,   ||\n||  targetId=%s,    ||\n||  Page from %s to %s  ||" %(account,targetId,startPage,startPage+totalPage-1))
                print("=" * 30)
                print ()
            else:
                print("------Error-------"*5)

        except Exception as e:
            print (e)
    @gen.coroutine
    def post(self):
        self.write("not yet support post method")
class Multi(BaseHandler):
    @gen.coroutine
    def get(self):
        targetId = self.get_argument("targetId");
        startPage = int(self.get_argument("startPage"));
        totalPage = int(self.get_argument("totalPage"))
        totalAc= int(self.get_argument('useidsize'))
        taskidtxt = str(targetId + ".txt")
        taskidpath = os.path.join(TASK_SAVE_DIR, taskidtxt)
        print(taskidpath)
        if os.path.exists(taskidpath):
            self.write("targetid task is doing ,please check again<br>,or kill this task for restart.<a href='../kill/one?taskid=%s'>Kill %s</a> <br>"% (targetId,targetId))
            return False
        conn = pymysql.connect(**SQLCONFIG)
        cursor = conn.cursor()
        cursor.execute("select account from cookies  where inuse='0'")
        freenum=cursor.rowcount
        if freenum==0:
            info="No enough account to start Multi Mode..."
            conn.commit()
            cursor.close()
            conn.close()
            print (info)
            self.write("<br><font color=red size=8>%s</fonr>"% info)
            return False
        conn.commit()
        cursor.close()
        conn.close()
        result = ("use <font color=red> %s </font> account ,<br>targetId=<font color=green>%s</font>,<br>Page from <font color=red>%s to %s</font>..<br> cookies pool has<font color=red size=10> %s </font> free account for use" % (
        totalAc, targetId, startPage, startPage + totalPage - 1,freenum))
        if freenum<totalAc:
            totalAc=freenum
        if totalPage <= totalAc:
            totalAc=1

        with open(taskidpath,'w'):
            pass

        # 异步调用
        tornado.ioloop.IOLoop.instance().add_callback(self._callback_multi, targetId, startPage, totalPage,totalAc)
        self.write(result)


    @run_on_executor()
    def _callback_multi(self,targetId, startPage, totalPage,totalAc):
        # 以下要开始写多线程

        try:
            m = totalAc
            pp = totalPage // m
            lpage = totalPage - (m - 1) * pp
            dict_vars=[ {
                'uuid': targetId,
                'startPage': startPage,
                'totalPage': pp,
                'actproxy': 'no',
                'acid': 0,
                'totalAc': m,
            }]
            func_var = [(None, dict_vars[0]),]
            sp=startPage+pp
            for n in range(1, m ):
                if n==m-1:
                    pp=lpage
                dict_vars.append({
                    'uuid': targetId,
                    'startPage': sp,
                    'totalPage': pp,
                    'actproxy': 'yes',
                    'acid' : n,
                    'totalAc' : m,
                                  })
                func_var.append((None,dict_vars[n]),)
                sp=sp+pp
            # print (func_var)
            pool = threadpool.ThreadPool(len(func_var))
            print ("开始多线程=> ",m)
            requests = threadpool.makeRequests(self.xxthread, func_var)
            [pool.putRequest(req) for req in requests]
            pool.wait()
        except Exception as e:
            print (e)
    def xxthread(self,uuid,startPage,totalPage,actproxy,acid,totalAc):
        print("xxxxx")
        executor = WeiBoScraper(uuid=uuid, startPage=startPage, totalPage=totalPage, acid=acid, totalAc=totalAc,actproxy=actproxy)
        executor.crawl()
        pass