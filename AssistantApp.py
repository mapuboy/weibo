#!/usr/bin/env python

import os
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
from tornadohandler.route import handlers


define("port", default=7777, help="run on the given port", type=int)
application = tornado.web.Application(handlers)

def main():
    print("起初工作目录:" + os.getcwd())
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()