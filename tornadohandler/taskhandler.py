from tornado import gen
import tornado.escape
import tornado.web
import os,time
from config import TASK_SAVE_DIR

class Killone(tornado.web.RequestHandler):

    @gen.coroutine
    def get(self):
        try:
            taskid=self.get_argument("taskid")
            fi=str(taskid+".txt")
            fi_d = os.path.join(TASK_SAVE_DIR, fi)
            os.remove(fi_d)
            print ("kill task %s success" % taskid)
            self.write("kill task %s success" % taskid)
        except Exception as e:
            print (e)
            self.write("kill task Error")

class Killall(tornado.web.RequestHandler):

    @gen.coroutine
    def get(self):
        files = os.listdir(TASK_SAVE_DIR)
        print(files)
        for fi in files:
            print ("xxxxxx")
            print(fi)
            fi_d = os.path.join(TASK_SAVE_DIR, fi)
            os.remove(fi_d)
        print ("kill all task finish")
        self.write("kill all task finish")

class Killlist(tornado.web.RequestHandler):

    @gen.coroutine
    def get(self):
        files = os.listdir(TASK_SAVE_DIR)
        print(files)
        reshead='Now doing task list:<br><hr><br>'
        reslist=""
        resfoot="<hr><br>stop and<font color=red><a href='./all'> <font color=red size=5> kill all</font></a></font>task..... <br>"

        if files:

            for fi in files:
                links=fi.rsplit(".txt")
                taskid=links[0]
                # fi_d = os.path.join(TASK_SAVE_DIR, fi)
                res=("<br>%s    <a href='./one?taskid=%s'>Kill %s</a> <br>"% (taskid,taskid,taskid))
                reslist +=res
        else:
            print ("ttttthere")
        resl=reshead+reslist+resfoot
        self.write(resl)
