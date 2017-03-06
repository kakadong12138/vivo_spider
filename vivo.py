 #-*- coding: UTF-8 -*-   
#!/usr/bin/python
import requests
import time
import json
import logging
import traceback

logger = logging.getLogger('vivo')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('vivo.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2) Gecko/20100115 Firefox/3.6'}

app_names = []


def call(url,name,times=6):
    for i in xrange(times):
        try:
            response = requests.get(url,headers=headers)
            return response
        except:
            continue
    else:
        logger.error("call %s failed ,url is %s"%(name,url))
        return False


def get_all_app():
    all_app = []
    url = r'http://main.appstore.vivo.com.cn/port/packages_top/?apps_per_page=20&elapsedtime=151191455&screensize=1080_1920&density=3.0&pictype=webp&cs=0&req_id=6&av=22&u=150100434a4e4234520702424e507300&an=5.1.1&app_version=624&imei=863102037519220&nt=WIFI&id=2&cfrom=4&type=6&model=vivo+X7&s=2%7C951964161&page_index='
    for page_index in range(1,11):
         for i in xrange(6):
            response = requests.get(url+str(page_index),headers=headers)
            break
         else:
            logger.error("call failed index is %s"%(page_index))
            return False
         result_json = response.json()
         value = result_json.get("value")
         for v in value:
            all_app.append(v)
    return all_app

def get_app_info(app_id):
    url = "http://info.appstore.vivo.com.cn/port/package/?elapsedtime=174320717&content_complete=1&screensize=1080_1920&density=3.0&pictype=webp&cs=0&av=22&u=150100434a4e4234520702424e507300&an=5.1.1&app_version=624&imei=863102037519220&nt=WIFI&module_id=10&target=local&cfrom=11&need_comment=0&model=vivo+X7&s=2%7C3010041739&id="
    url+=str(app_id)
    for i in xrange(6):
        try:
            response = requests.get(url,headers=headers)
            break
        except:
            continue
    else:
        logger.error("call failed index is %s"%(page_index))
        return False
    result_json = response.json()
    value = result_json.get("value")
    score = value.get("score")
    raters_count = value.get("raters_count")
    download_count = value.get("download_count")
    return (score,raters_count,download_count)

def get_rankings(cpds):
    rankings = {}
    for ranking ,app in enumerate(cpds):
        ranking+=1
        name =  app.get("title_zh")
        #print ranking,name
        if u"饿了么" in name:
            rankings[u"饿了么"] = ranking
        elif u"百度外卖" in name:
            rankings[u"百度外卖"] = ranking
        elif u"美团外卖" in name:
            rankings[u"美团外卖"] = ranking
    return rankings

def get_tuijian_yingyong_ranking():
    urls = {}
    urls["tuijian"] = "http://main.appstore.vivo.com.cn/interface/index_recommend?apps_per_page=40&elapsedtime=416943896&screensize=1080_1920&density=3.0&pictype=webp&cs=0&av=22&u=150100434a4e4234520702424e507300&an=5.1.1&app_version=624&imei=863102037519220&nt=WIFI&cfrom=1&model=vivo+X7&s=2|533979422&page_index="
    urls["yingyong"] = "http://main.appstore.vivo.com.cn/port/recommendApp?apps_per_page=40&elapsedtime=75985868&screensize=1080_1920&density=3.0&pictype=webp&cs=0&av=22&u=150100434a4e4234520702424e507300&an=5.1.1&app_version=624&imei=863102037519220&nt=WIFI&cfrom=35&model=vivo+X7&s=2%7C3496048853&page_index="
    results = {}
    for type_name,url in urls.items():
        f= open(type_name+".txt","w")
        response = call(url+"1", type_name+"1")
        response_json = response.json()
        value = response_json.get("value")
        cpds = value.get("cpds")
        apps = value.get("apps")
        cpdpos = value.get("cpdpos")
        response2 = call(url+"2", type_name+"2")
        apps2 = response2.json().get("value").get("apps")
        apps = apps+apps2

        '''
        for a in cpds:
            print a.get("title_zh")
        print '----------------------------------------------------'

        if type_name == 'tuijian':
            for a in apps:
                print a.get("title_zh")
            print '----------------------------------------------------'
            for a in apps2:
                print a.get("title_zh")
        '''
        current_time = time.time()
        #print "current time is %s"%(current_time)

        cpds_sort = ttt(cpds,apps,cpdpos,type_name)
        f.write(str(current_time)+"\n")
        for a in cpds_sort:
            f.write(a.get("title_zh").encode("utf8")+"\n")
        f.write("---------------------------------------------\n")  

        f.close()
        rankings = get_rankings(cpds)
        results[type_name] = (rankings,cpds)
    return results

def get_yingyong_ranking():
    url = "http://main.appstore.vivo.com.cn/port/recommendApp?apps_per_page=40&elapsedtime=75985868&screensize=1080_1920&density=3.0&pictype=webp&cs=0&av=22&u=150100434a4e4234520702424e507300&an=5.1.1&app_version=624&imei=863102037519220&nt=WIFI&cfrom=35&model=vivo+X7&s=2%7C3496048853&page_index="
    response = call(url, "yinyong")
    cpds = ttt(response.json())
    rankings = get_rankings(cpds)
    return rankings,cpds

def ttt(cpds,apps,cpdpos,type_name):
    max_cpdpos = max(cpdpos)
    cpdpos_set = set(cpdpos)
    fill_index =  set(range(1,max_cpdpos+1)) - cpdpos_set
    #print fill_index
    for i,v in zip(fill_index,apps):
        cpds.insert(i-1,v)
        apps.remove(v)
    if type_name == "tuijian":
        return cpds
    elif type_name == "yingyong":
        return cpds[:max_cpdpos+1-len(fill_index)]+apps

    

if __name__ == '__main__':
    get_tuijian_yingyong_ranking()
    







