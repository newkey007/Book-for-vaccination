import ast
import json
import re
import requests
import sys
import io
import random
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')
import time

#定义一个全局量标识timecode
g_timecode=0
#定义一个全局量标识g_appiDate
g_appiDate=0
#定义一个全局量标识找到可预约的时间点
g_avaiable=0
#定义一个全局量表示1个随机数
g_query_num=random.randint(1,10000)
current_milli_time = int(round(time.time() * 1000))
parse_parm=''

Query_Params = {
    'wxid': 'xxxxxx',
    'childCode': 'xxxxx',
    'childName': 'xxxxx',
    'childBirthday': 'xxxx-xx-xx',
    'curdp':'xxxxxxxxx',
    'childCurName':'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    'wxinAppid': 'xxxxxxxxxxxx HTTP/1.1',
    'jQuery':'400010062435737811031',
    'unix_timestamp': ''
}

wxid      = Query_Params["wxid"]
childCode = Query_Params["childCode"]
childName = Query_Params["childName"]
childBirthday = Query_Params["childBirthday"]
curdp = Query_Params["curdp"]
childCurName = Query_Params["childCurName"]
wxinAppid = Query_Params["wxinAppid"]
jQuery    = Query_Params["jQuery"]
unix_timestamp=current_milli_time

firstURL = "https://jkzx.szcdc.cn:8008/wxyyWeb/wxyy_web.html?wxid={}&childCode={}&childName={}&childBirthday={}&curdp={}&childCurName={}&wxinAppid={}".format(
    wxid, childCode, childName,childBirthday,curdp,childCurName,wxinAppid)

secondURL = "https://jkzx.szcdc.cn:8003/AppYmt/Bespeak/wxZxyyFindDateServlet?resultMap=jQuery400010062435737611031_1654048151694&sysMark=YMTHOME&wxinId={}&curdp={}&chilCode={}&_=1654048151695 HTTP/1.1".format(
wxid, curdp, childCode, childName,childBirthday
)

thirdURL =  "https://jkzx.szcdc.cn:8003/AppYmt/Bespeak/wxZxyyAddInfoServlet?resultMap=jQuery{}_{}&sysMark=YMTHOME&wxinId={}&curdp={}&chilCode={}&appiDate={}&timeCode={}&_={} HTTP/1.1".format(
jQuery,unix_timestamp,wxid, curdp, childCode,g_appiDate,g_timecode,unix_timestamp
)

def get_data():
    global  g_query_num
    resule="false"
    unix_timestamp = int(round(time.time() * 1000))
    g_query_num+=1
    secondURL = "https://jkzx.szcdc.cn:8003/AppYmt/Bespeak/wxZxyyFindDateServlet?resultMap=jQuery{}_{}&sysMark=YMTHOME&wxinId={}&curdp={}&chilCode={}&_={} HTTP/1.1".format(
        jQuery+str(g_query_num),unix_timestamp,wxid, curdp, childCode, childName, childBirthday,unix_timestamp
    )
    print(time.strftime("%Y-%m-%d %H:%M:%S: ", time.localtime())+"Request URL1: "+secondURL)
    try:
        data = requests.get(url=secondURL,timeout = (2,4))
        data.encoding='utf-8'
        resule = data.text
        res = data.status_code;
        if res == 200:
            print("get data %s"%res)
            resule =json.dumps(resule)
            p1 = re.compile(r'[(](.*?)[)]', re.S)
            parse_parm = re.findall(p1, data.text)[0]
            str_to_dict = eval(parse_parm)
            print(str_to_dict)
            jsondata(str_to_dict)
            print("g_avaiable=%d" %g_avaiable)
            if g_avaiable == 1:
                send_data()
        else:
            print('get data Fail')
            resule = "false"
            return resule
    except requests.exceptions.ConnectionError:
            print(time.strftime("%Y-%m-%d %H:%M:%S: ", time.localtime()) + "ConnectError -- please wait 3 seconds")
            time.sleep(2)

    except requests.exceptions.ChunkedEncodingError:
        print(time.strftime("%Y-%m-%d %H:%M:%S: ", time.localtime()) + "ChunkedEncodingError -- please wait 3 seconds")
        time.sleep(2)

    except:
        print(time.strftime("%Y-%m-%d %H:%M:%S: ", time.localtime()) + "Unfortunitely --An Unknow Error")
        time.sleep(2)
    return resule


def jsondata(js):
    global g_avaiable
    data_head=js["message"]
    zxyydate=data_head["zxyydate"]
    print("total date:%s" %(len(zxyydate)))                 #总共有多少个日期
    print( "total time:%s"  %(len(zxyydate[0]['appiTime'])))  #每个日期下的时间点
    for i in range(len(zxyydate)-1,0,-1):
        for j in range(len(zxyydate[i]['appiTime'])):
            if zxyydate[i]['appiTime'][j]['surNum'] != "0":
                g_timecode=zxyydate[i]['appiTime'][j]['timeCode']
                g_appiDate=zxyydate[i]['appiDate']
                print(zxyydate[i]['appiTime'][j]['surNum'])
                print(zxyydate[i]['appiTime'][j]['timeCode'])
                print(zxyydate[i]['appiDate'])
                g_avaiable=1
                break;

def  send_data():
    global g_query_num
    g_query_num += 1
    unix_timestamp=int(round(time.time() * 1000))
    thirdURL = "https://jkzx.szcdc.cn:8003/AppYmt/Bespeak/wxZxyyAddInfoServlet?resultMap=jQuery{}_{}&sysMark=YMTHOME&wxinId={}&curdp={}&chilCode={}&appiDate={}&timeCode={}&_={} HTTP/1.1".format(
        jQuery+str(g_query_num), unix_timestamp, wxid, curdp, childCode, g_appiDate, g_timecode,unix_timestamp)
    print(time.strftime("%Y-%m-%d %H:%M:%S: ", time.localtime()) +thirdURL)
    print(thirdURL)
    try:
        data = requests.get(url=thirdURL,timeout = (2,30))
        data.encoding = 'utf-8'
        resule = data.text  #
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "  " + str(sys._getframe().f_lineno) + " resule=",
              resule)
        res = data.status_code;
        if res == 200:
            print("send_data response:code:%s" %res)
            print(resule)
        else:
            print("send_data response:code:%s" %res)
    except requests.exceptions.ConnectionError:
        print(time.strftime("%Y-%m-%d %H:%M:%S: ", time.localtime()) +"ConnectError -- please wait 3 seconds")
        time.sleep(2)

    except requests.exceptions.ChunkedEncodingError:
        print(time.strftime("%Y-%m-%d %H:%M:%S: ", time.localtime()) + "ChunkedEncodingError -- please wait 3 seconds")
        time.sleep(2)

    except:
        print(time.strftime("%Y-%m-%d %H:%M:%S: ", time.localtime()) + "Unfortunitely --An Unknow Error")
        time.sleep(2)

if __name__ == '__main__':
    print(time.strftime("%Y-%m-%d %H:%M:%S: ", time.localtime())+"预约疫苗程序开始运行 ")
    while True:
        js = get_data()
        try:
            js = ast.literal_eval(js)
            if js =="false":
                time.sleep(0.5)
            else:
                time.sleep(0.9)
        except requests.exceptions.ConnectionError:
            print(time.strftime("%Y-%m-%d %H:%M:%S: ", time.localtime()) + "ConnectError -- please wait 3 seconds")
            time.sleep(2)

        except requests.exceptions.ChunkedEncodingError:
            print(time.strftime("%Y-%m-%d %H:%M:%S: ",
                                time.localtime()) + "ChunkedEncodingError -- please wait 3 seconds")
            time.sleep(2)

        except:
            print(time.strftime("%Y-%m-%d %H:%M:%S: ", time.localtime()) + "Unfortunitely --An Unknow Error")
            time.sleep(2)