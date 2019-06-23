# -*- coding: utf-8 -*-
import requests
from lxml import etree
import re
import json
import pandas as pd
import time
from multiprocessing import Pool
from functools import partial
from requests.exceptions import RequestException
import threading
#from snownlp import SnowNLP

headers = {
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
	}
domain = 'http://guba.eastmoney.com'
mid1 = '/list,'
mid2 = ',f_'
tail = '.html'
#stkcd = str
# page: str(number)

class OutofdateError(Exception):
	pass


def get_one_page(stkcd,page):
# if error,then the start next stkcd
    url = domain+mid1+stkcd+mid2+page+tail	
    r = requests.get(url,headers=headers)
    if r.status_code ==200:
        r.encoding = 'utf-8' # encode response with utf-8 to represent Chinese.if not, use chardet resulting messy code.
        return r.text
    else:
        raise RequestException
def get_new_page(domain,link):
    url = domain+link
    r = requests.get(url,headers=headers)
    r.encoding = 'utf-8' # encode response with utf-8 to represent Chinese.if not, use chardet resulting messy code.
    return r.text

def check_date(domain,first_link):
# keep crawling if data is later than 2017-12-31
    page = get_new_page(domain,first_link)
    date = parse_new_page(page)[0]
    if date > '2009-12-31':
        return True
    else:
        return False

def parse_new_page(new_page):
    html_new = etree.HTML(new_page)
    time = html_new.xpath("//div[@class='zwfbtime']/text()")[0]
    date = time[4:14] # return str
    content_ls = html_new.xpath("//div[@class='stockcodec .xeditor']//text()") # list
    content = ''
    for i in content_ls:
        content += i
    return date,content.strip()


def parse_one_page(stkcd,page,p):
    # return dataframe contains info in one page
    html = etree.HTML(page)
    # list of elements	
    hrefs = html.xpath("//div[@class='articleh normal_post']/span[3]/a/@href")
    first_link = hrefs[0]
    if check_date(domain,first_link):	
        views = html.xpath("//div[@class='articleh normal_post']/span[1]/text()") 
        replys = html.xpath("//div[@class='articleh normal_post']/span[2]/text()")
        titles = html.xpath("//div[@class='articleh normal_post']/span[3]/a/text()")		
        dates = []
        contents = []
        sentiments = []
        pags = []
        #for each view, collect it's data and reply number into a list,seperately.
        for link in hrefs:
            try:
                new_page = get_new_page(domain=domain,link=link)
                date =  parse_new_page(new_page)[0]
                content = parse_new_page(new_page)[1]
                dates.append(date)
                contents.append(content)
                #s = SnowNLP(content)
                #senti = s.sentiments
                #sentiments.append(round(senti,4))
                pags.append(p)
                #print('finishing new page')
            except IndexError as e:
                dates.append(None)
                contents.append(None)
                #sentiments.append(None)
                pags.append(p)
                continue
                            
        page = pd.DataFrame({'code':[stkcd]*len(views),'dates':dates,'views':views, 'replys':replys, 'titles':titles, 'contents':contents,'page':pags})
        return page

    else:	
        raise OutofdateError
	
def write_to_csv(stkcd,df):
    with open('{}.csv'.format(stkcd),'a') as f:
        df.to_csv(f,header = False)

def get_page_num(stkcd,s,e):
    p = int((s+e)/2)
    if check(stkcd,p)==True and check(stkcd,p+1) ==False:
        return p
    elif check(stkcd,p)==True:
        return get_page_num(stkcd,p+1,e)
    else:
        return get_page_num(stkcd,s,p-1)

def check(stkcd,p):
    page = get_one_page(stkcd,str(p))
    html = etree.HTML(page)
    noarticle = html.xpath('//div[@class="noarticle"]/text()')
    #print(noarticle[0])
    try:
        noarticle[0]
        return False
    except IndexError:
        return True

def main(domain,mid1,mid2,tail,stkcd,p):
    try:			
        print('stkcd',stkcd,'page',p)
        page = get_one_page(stkcd,str(p))
        print('page done')
        content = parse_one_page(stkcd,page,p)
        print('con done')
        write_to_csv(stkcd,content)
        print('write done',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),stkcd,p)
    except Exception:
         pass

class myThread (threading.Thread):
    def __init__(self, threadID,threadName,domain,mid1,mid2,tail,stkcd,p):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName
        self.domain = domain
        self.mid1 = mid1
        self.mid2 = mid2
        self.tail = tail
        self.stkcd = stkcd
        self.p = p
    def run(self):        
        main(self.domain,self.mid1,self.mid2,self.tail,self.stkcd,self.p)
        

def mkThread(p):
    return myThread(p,'Thread%s'%p,domain,mid1,mid2,tail,stkcd,p)
sz50 = pd.read_excel('sz50.xlsx',converters={'stkcds':str})['stkcds']
#print(sz50)
#cods = ['002415','000001']
#cods = ['600000']
#main(domain,mid1,mid2,tail,'002415',110)
#print(cods)	
for stkcd in sz50[:10]:
    try:
        pagenum = get_page_num(stkcd,1,10000)
    except:
        pagenum = 4000
    threads = [mkThread(p) for p in range(2,pagenum+1)]
    n = int(pagenum/900)+1
    for i in range(n):
        if i !=n-1:
            for th in threads[i*900:(i+1)*900]:
                th.start()
            for th in threads[i*900:(i+1)*900]:
                th.join(30)
        else:
            for th in threads[i*900:]:
                th.start()
            for th in threads[i*900:]:
                th.join(30)

