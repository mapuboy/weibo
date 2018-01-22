import time,requests
import os,pickle,pymysql
from config import SQLCONFIG,URLPOST,COOKIESPOST

def set_cookies_to_mysql(account,cookies):
    try:
        conn=pymysql.connect(**SQLCONFIG)
        cursor = conn.cursor()
        try:
            sql=("""CREATE TABLE cookies (id INT(6) AUTO_INCREMENT PRIMARY KEY,account VARCHAR(100) UNIQUE NOT NULL,cookies VARCHAR(1000) NOT NULL,valid INT(1) DEFAULT 0,inuse INT(1) DEFAULT 0) engine=innodb""")
            cursor.execute(sql)
        except Exception as e:
            print (e)
            conn.rollback()
        try:
            sql=("insert into cookies(account,cookies) value ('%s','%s') on duplicate key UPDATE account='%s', cookies='%s',valid=0" %(account,cookies,account,cookies))
            cursor.execute(sql)
            result=('set cookies to mysql success')
        except Exception as e:
            print(e)
            result=("set cookies Error!!!")
        conn.commit()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        print (e)
        return 'set cookies Error'
def reset_cookies_mysql(account):
    try:
        conn = pymysql.connect(**SQLCONFIG)
        cursor = conn.cursor()
        cursor.execute("update cookies set inuse=0 where account='%s'" %account)
        conn.commit()
        cursor.close()
        conn.close()
        print ("ok")
    except Exception as e:
        print (e)
        return 'set cookies Error'
    pass
# def set_cookies_from_network(account,cookies):
#     try:
#         cookie_string = cookies
#         if os.path.exists(COOKIES_SAVE_PATH):
#             with open( COOKIES_SAVE_PATH, 'rb') as f:
#                 cookies_dict = pickle.load(f)
#                 cookies_dict[account] = cookie_string
#                 with open( COOKIES_SAVE_PATH, 'wb') as f:
#                     pickle.dump(cookies_dict, f)
#                 print('333successfully save cookies into {}. \n'.format(COOKIES_SAVE_PATH))
#                 return ('set cookie success1')
#
#         else:
#             cookies_dict = dict()
#             cookies_dict[account] = cookie_string
#             with open(COOKIES_SAVE_PATH, 'wb') as f:
#                 pickle.dump(cookies_dict, f)
#             print('4444successfully save cookies into {}. \n'.format(COOKIES_SAVE_PATH))
#             return ('set cookie success2')

    #
    # except Exception as e:
    #     print(e)
    #     return ('set cookie error3')

def get_cookies_from_mysql(account='default'):
    conn=pymysql.connect(**SQLCONFIG)
    cursor = conn.cursor()
    try:
        if account == ("default"):
            sql=("select account,cookies from cookies where inuse='0'" )
        else:
            sql=("select account,cookies from cookies where account='%s'" % account)

        cursor.execute(sql)
        res= cursor.fetchone()
        if res:
            account=res[0]
            cookie=res[1]
            cookies = {account: cookie}
        else:
            cursor.close()
            conn.close()
            print ("No free account or cann't find account what you choosed.Please check your Cookies pool...Try again in 10 mins...")
            try:
                data = ({'using_account': account,
                         'exception': 'No free account or cannot find <font color=red>%s</font>,try again in 10 mins...'% account})
                r = requests.post(URLPOST, data=data, cookies=COOKIESPOST,timeout=10)
                print(r.text)
            except Exception:
                pass
            time.sleep(10*60)
            print("get Cookies again!")
            get_cookies_from_mysql(account)
            return ("oh, No")
        sql=("update cookies set inuse='1' where account='%s'" % account)
        cursor.execute(sql)
        conn.commit()
        cursor.close()
        conn.close()
        # print(cookies)
        return cookies
    except Exception as e:
        print (e)


if __name__ == "__main__":
    reset_cookies_mysql("15505910556")
