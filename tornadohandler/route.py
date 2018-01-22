from tornadohandler.handlercenter import Testhandler,Single,Multi,SetCookies,ResetCookies
from tornadohandler.taskhandler import Killone,Killall,Killlist

__author__ = 'HQ'

'''
项目路由文件
'''


handlers = [
    (r"/task/single", Single),
    (r"/set/cookies", SetCookies),
    (r"/reset/cookies",ResetCookies),
    (r"/task/multi", Multi),
    (r"/test", Testhandler),
    (r"/kill/one",Killone),
    (r"/kill/all",Killall),
    (r"/kill/list",Killlist),


    # (r"/story/([0-9]+)", StoryHandler),
]
