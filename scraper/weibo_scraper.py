from config import *
import requests,time,re,pymysql
from pools.cookies import get_cookies_from_mysql,reset_cookies_mysql
from lxml import etree
def is_number(s):
    try:
        a = float(s)
        return True
    except ValueError as e:
        return False

class WeiBoScraper(object):
    def __init__(self,uuid,account="default",  actproxy='no',mode='single', filter_flag=0,acid=1,totalAc=2,totalPage=1,startPage=1,):
        time.sleep(acid*2)
        self.account = account
        self.headers = get_header()
        self.get_cookies()
        self.mode = mode
        self.targetId = uuid
        self.filter = filter_flag
        self.user_name = ''
        self.weibo_num = 0
        self.weibo_scraped = 0
        self.following = 0
        self.followers = 0
        self.weibo_content = []
        self.num_zan = []
        self.num_forwarding = []
        self.num_comment = []
        self.weibo_detail_urls = []
        self.totalPage = totalPage
        self.startPage = startPage
        self.acid = acid
        self.totalac = totalAc
        self.count = 0
        self.maxgetpro = 80
        self.endPage = 0
        self.nowPage = 0
        self.nowurlnum = 0
        self.actproxy = actproxy
        if self.actproxy=="yes":
            self.proxies=self.get_proxies()
        pass
    def get_proxies(self):
        count=self.count
        if count >= self.maxgetpro:
            count = 0
        if int(count) == 0:
            conn = pymysql.connect(**SQLCONFIG)
            cursor = conn.cursor()
            cursor.execute('select id,ip ,port, speed  from proxys order by speed ')
            maxip = cursor.rowcount
            if maxip < self.maxgetpro:
                self.maxgetpro = maxip
            self.proxiesall = cursor.fetchmany(self.maxgetpro)
            print("ippool total has {} > get {} ..".format(maxip, self.maxgetpro))
            conn.commit()
            cursor.close()
            conn.close()

            i = self.acid - 1
            proxies = {
                "http": "http://" + self.proxiesall[i][1] + ":" + str(self.proxiesall[i][2]),
            }
            if self.totalac == 1:
                self.count = self.count+self.totalac
            else:
                # print(self.count,"hhaaaa")
                self.count += self.totalac - 1
            print(self.account,"proxy:",proxies)
            return (proxies)
        elif self.maxgetpro > (count) > 0:

            i = count - 1
            proxies = {
                "http": "http://" + self.proxiesall[i][1] + ":" + str(self.proxiesall[i][2]),
            }
            if self.totalac == 1:
                self.count += self.totalac
            else:
                self.count += self.totalac - 1
            print(self.account,"proxy:", proxies)
            return proxies
    def change_proxy(self,url):
        pro = 0

        while pro == 0:
            try:
                response = requests.get(url, cookies=self.cookies, headers=self.headers,
                                        proxies=self.proxies)
                if response.status_code == 200:
                    pro = 1
                    html = response.content

                    return  html
                if response.status_code == 302:
                    self.proxies = self.get_proxies()
                    self.headers = get_header()
                    # time.sleep(10)
                    pro = 0
                if response.status_code == 403:
                    print (url + '抓取博主信息403错误,5分钟后再请求一次.'+self.account)
                    time.sleep(5 * 60)
                    self.proxies = self.get_proxies()
                    self.headers = get_header()
                    pro = 0

            except Exception as e:
                print(e)
                print(self.account, '==>', '代理出错...')
                self.proxies = self.get_proxies()
                self.headers = get_header()
                # time.sleep(1 * 60)

    def report_error(self,errinfo):
        try:
            data = ({'usingaccount': self.account,
                     'exception':errinfo})
            r = requests.post(URLPOST, data=data, cookies=COOKIESPOST)
            print(r.text)
        except Exception as e:
            print (e)
            print ( self.account,"Error Report=>fault")

    def get_cookies(self):
        cookies=get_cookies_from_mysql(self.account)
        for i in cookies:
            self.account=i
            self.cookies={"cookies":cookies[i]}

    # def get_headers(self):
    #     return (get_header())


    def get_html(self):
        # 首页信息.html
        d=self.check_task(self.targetId)
        if not d:
            print("get_html......")
            return
        if is_number(self.targetId):
            url = 'http://weibo.cn/u/%s?filter=%s&page=1' % (self.targetId, self.filter)
            print(url)
        else:
            url = 'http://weibo.cn/%s?filter=%s&page=1' % (self.targetId, self.filter)
            print(url)
        try:
            if self.actproxy == "no":
                print(self.account, ":", self.cookies)
                self.html = requests.get(url, cookies=self.cookies, headers=self.headers,).content
            else:
                self.html=self.change_proxy(url)
            print('success load html..')
            print("get user name")
            try:
                selector = etree.HTML(self.html)
                self.user_name = selector.xpath('//table//div[@class="ut"]/span[1]/text()')[0]
                print('current user name is: {}'.format(self.user_name))
                print('-- getting user info')
                selector = etree.HTML(self.html)
                pattern = r"\d+\.?\d*"
                str_wb = selector.xpath('//span[@class="tc"]/text()')[0]
                guid = re.findall(pattern, str_wb, re.S | re.M)
                for value in guid:
                    num_wb = int(value)
                    break
                self.weibo_num = num_wb

                str_gz = selector.xpath("//div[@class='tip2']/a/text()")[0]
                guid = re.findall(pattern, str_gz, re.M)
                self.following = int(guid[0])

                str_fs = selector.xpath("//div[@class='tip2']/a/text()")[1]
                guid = re.findall(pattern, str_fs, re.M)
                self.followers = int(guid[0])
                print('current user all weibo num {}, following {}, followers {}'.format(self.weibo_num, self.following,
                                                                                         self.followers))
            except Exception as e:
                print (e)
                print("get user name or weibo counts Error")

        except Exception as e:
            print (e)
        pass
    def get_target_info(self):
        pass
    def weibo_url(self):
        print('-- getting weibo info--')
        selector = etree.HTML(self.html)

        try:
            print('开始')
            if len(selector.xpath('//input[@name="mp"]')) == 0:
                endpage = 1
            else:
                endpage = int(selector.xpath('//input[@name="mp"]')[0].attrib['value'])

            pattern = r"\d+\.?\d*"
            print(self.account, '--- all weibo page {}'.format(endpage))
            # a=self.totalPage + self.startPage
            # print(a,"  aaaaa")
            if (self.totalPage + self.startPage)> endpage:
                print("you get more than actually page, adjust end page:",endpage)
            else:
                endpage = self.totalPage + self.startPage-1
            if self.endPage == 0:
                self.endPage = endpage

            # print('endpage', self.endPage)
            startPage = 1
            if self.startPage > endpage:
                print("you start page:",self.startPage,"exceed end page:", endpage,"Now start form page 1.")
                pass
            else:
                startPage = self.startPage
            # 出错后,调用self变量来继续让捉取
            if self.nowPage > 0:
                startPage = self.nowPage
            print(startPage, "===>", self.endPage)

            try:
                # traverse all weibo, and we will got weibo detail urls
                # TODO: inside for loop must set sleep avoid banned by official.
                # page = sP
                for page in range(startPage, self.endPage+1):
                    # print(page, "page start")
                    self.nowPage = page
                    url2 = 'http://weibo.cn/%s?filter=%s&page=%s' % (self.targetId, self.filter, page)
                    if self.actproxy == "no":
                        html2 = requests.get(url2, cookies=self.cookies, headers=self.headers).content
                    else:
                        html2=self.change_proxy(url2)
                    selector2 = etree.HTML(html2)
                    info = selector2.xpath("//div[@class='c']")
                    # print(self.account, ' ---- current solving page {}'.format(page))

                    if page % 10 == 0:
                        print(
                            '[ATTEMPTING] solving {} rest for {} seconds to cheat weibo site, 5 minutes avoid being banned.'.format(page,
                                SCRAPER_WEIBO_SLEEPTIME))
                        time.sleep(SCRAPER_WEIBO_SLEEPTIME)

                    if len(info) > 3:
                        for i in range(0, len(info) - 2):
                            detail = info[i].xpath("@id")[0]
                            self.weibo_detail_urls.append('http://weibo.cn/comment/{}?uid={}&rl=0'.
                                                          format(detail.split('_')[-1], self.targetId))

                            self.weibo_scraped += 1
                            str_t = info[i].xpath("div/span[@class='ctt']")
                            weibos = str_t[0].xpath('string(.)')
                            self.weibo_content.append(weibos)
                            # print(weibos) 打印这个没有什么作用 先注释

                            str_zan = info[i].xpath("div/a/text()")[-4]
                            guid = re.findall(pattern, str_zan, re.M)
                            num_zan = int(guid[0])
                            self.num_zan.append(num_zan)

                            forwarding = info[i].xpath("div/a/text()")[-3]
                            guid = re.findall(pattern, forwarding, re.M)
                            num_forwarding = int(guid[0])
                            self.num_forwarding.append(num_forwarding)

                            comment = info[i].xpath("div/a/text()")[-2]
                            guid = re.findall(pattern, comment, re.M)
                            num_comment = int(guid[0])
                            self.num_comment.append(num_comment)
            except etree.XMLSyntaxError as e:
                print(self.account, '==>', 'get weibo info finished.')
            if self.filter == 0:
                print(self.account, '==>', '共' + str(self.weibo_scraped) + '条微博')

            else:
                print(self.account, '==>',
                      '共' + str(self.weibo_num) + '条微博，其中' + str(self.weibo_scraped) + '条为原创微博')


        except Exception as e:
            print(e)
            print(self.account, '==>',
                  'get weibo info done, current user {} has no weibo yet.'.format(self.targetId))
            info=('get weibo info done, current user {} has no weibo yet.'.format(self.targetId))
            self.report_error(info)
        pass
    def title_comment(self):
        for i, url in enumerate(self.weibo_detail_urls):
            #每条微博暂停个10秒
            try:
                d = self.check_task(self.targetId)
                if not d:
                    print("no task file")
                    return
                time.sleep(10)
                print ('solving weibo detail from {}'.format(url))
                if self.weibo_content[i].startswith("抱歉,此微博已被作者删除"):
                    print(self.account, '==>', '正在爬取第 {} of {} 条微博\n'.format(i + 1, self.weibo_scraped),"此条微博已被作者删除,...跳过这条...")
                    continue
                if self.actproxy=="no":
                    html_detail = requests.get(url, cookies=self.cookies, headers=self.headers).content
                else:
                    html_detail=self.change_proxy(url)
                selector_detail = etree.HTML(html_detail)
                #查找评论页面的页数(少于2页查不到)
                allCommontList = selector_detail.xpath('//*[@id="pagelist"]/form/div/input[1]/@value')
                # all_comment_pages = selector_detail.xpath('//*[@id="pagelist"]/form/div/input[1]/@value')[0]
                weibo_comments_save_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),'details/%s -%s.txt' % (self.targetId, self.acid))

                # # if not os.path.exists('./weibo_detail/'): 下面根据assistantapp的目录转的绝对路径
                # weibo_comments_save_path = os.path.join(os.path.dirname(sys.argv[0]), 'weibo_terminater/weibo_detail/{}
            except Exception as e:
                print(e)
                continue
            print(self.account, '==>', '这是 {} 的微博：'.format(self.user_name))
            print(self.account, '==>', '正在爬取第 {} of {} 条微博'.format(i + 1, self.weibo_scraped))
            print(self.account, '==>', '微博内容： {}'.format(self.weibo_content[i]))
            print(self.account, '==>', '接下来是下面的评论：\n')
            if not os.path.exists(os.path.dirname(weibo_comments_save_path)):
                os.makedirs(os.path.dirname(weibo_comments_save_path))
            print(self.account, "save to => " , weibo_comments_save_path)
            all_comment_pages = 1
            if len(allCommontList)==0:
                pass
                # print ("评论单页或没有评论")
                # print (len(selector_detail.xpath('//div[starts-with(@id, "C_")]')))
            else:
                all_comment_pages = allCommontList[0]
                print (all_comment_pages,"页")

            # write weibo content
            f=open(weibo_comments_save_path, 'a', encoding='utf-8')
            f.writelines('EE\n')
            f.writelines(self.weibo_content[i] + '\n')
            f.writelines('EE\n')
            f.writelines('FF\n')
            for page in range(1,int(all_comment_pages)+1):
                try:
                    d = self.check_task(self.targetId)
                    if not d:
                        f.writelines('FF\n')
                        f.close()
                        return
                    if (page-1) % 10 == 0 and page>10:
                        print('[ATTEMPTING] crawl {} page, now must rest for {} seconds to crawl,\n (5 minutes better) avoid being banned.'.format(page,SCRAPER_WEIBO_SLEEPTIME))
                        time.sleep(SCRAPER_WEIBO_SLEEPTIME)
                    # print(self.account, "------------- ", page)
                    # we crawl from page 2, cause front pages have some noise
                    detail_comment_url = url + '&page=' + str(page)
                    # from every detail comment url we will got all comment
                    if self.actproxy == "no":
                        html_detail_page = requests.get(detail_comment_url, cookies=self.cookies, headers=self.headers).content
                    else:
                        html_detail_page=self.change_proxy(detail_comment_url)
                    selector_comment = etree.HTML(html_detail_page)

                    comment_div_element = selector_comment.xpath('//div[starts-with(@id, "C_")]')

                    for child in comment_div_element:
                        try:
                            if child.xpath('a[1]/text()'):
                                single_comment_user_name = child.xpath('a[1]/text()')[0]
                            else:
                                single_comment_user_name = "None"

                            if child.xpath('span[1][count(*)=0]'):
                                single_comment_content = child.xpath('span[1][count(*)=0]/text()')[0]

                            else:
                                span_element = child.xpath('span[1]')[0]
                                # 获取转发@名字
                                # at_user_name = span_element.xpath('a/text()')[0]
                                # at_user_name = '$' + at_user_name.split('@')[-1] + '$'
                                single_comment_content = span_element.xpath('text()[1]')
                                # single_comment_content.insert(1, at_user_name)
                                single_comment_content = ' '.join(single_comment_content)

                                # print(single_comment_content)
                            if single_comment_content.startswith("转发此微博:"):
                                single_comment_content = single_comment_content.split("转发此微博:")[1]
                            if single_comment_content.endswith('//'):
                                single_comment_content = single_comment_content.split("//")[0]
                            if single_comment_content == "":
                                pass
                            else:
                                full_single_comment = '<' + single_comment_user_name + '>' + ': ' + single_comment_content
                                f.writelines(full_single_comment + '\n')
                        except Exception as errinfo:
                            print (errinfo)
                            self.report_error(errinfo)
                            continue
                except Exception as e:
                    print (e)
                    try:
                        errinfo=(detail_comment_url+'<br>读取这页的评论不完整,但是继续下一微博的抓取')
                        self.report_error(errinfo)
                    except Exception:
                        pass
                    continue

                # except etree.XMLSyntaxError as e:
                #     print (e)
                #     print('-'*20)
                #     print('user id {} all done!'.format(self.targetId))
                #     print('all weibo content and comments saved into {}'.format(weibo_comments_save_path))


            f.writelines('FF\n')
            f.close()
        print (self.account," =========all comment get Finsh============")
        reset_cookies_mysql(self.account)
        print (self.account,"now ready for using")

    def check_task(self,targetId):
        taskidpath=os.path.join(TASK_SAVE_DIR,"%s.txt" % self.targetId )
        if os.path.exists(taskidpath):
            return True
        else:
            return False

    def crawl(self):
        try:
            print ("start crawl")
            self.get_html()
            self.get_target_info()
            self.weibo_url()
            self.title_comment()
            print ("--finish!!!--")
            return True
        except Exception as e:
            self.report_error(e)
            return False
