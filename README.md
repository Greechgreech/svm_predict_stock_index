# 上证50指数历史市场数据+SVM 预测明日指数走势
## 模型代码
数据获取、数据处理、模型训练及预测的代码均在文件：sz50-svm.ipynb中。其中，数据获取部份需要利用joinquant的数据库，因此建议用joinquant研究平台运行代码。
不使用joinquant的替代办法:所有从joinquant上获取的数据、利用数据构建的特征存放于dataset.xlsx中，因此只需：
```
import pandas as pd
df = pd.read_excel('dataset.xlsx')
```
便可跳过获取数据、构建特征的步骤（单元格2-8），开始进行缺失值处理。

## 输出文件 

dataset.xlsx  ： 2010-01-01~2019-06-01 2285个样本，36个特征  
data_stat :  特征的统计性描述（加注释）  
data_stat_raw :  特征的统计性描述（未加注释）  

## 东方新财富-股吧爬虫
### 目的
希望通过爬取股吧发帖内容获得股民情绪指数，将情绪指数作为训练特征用于SVM模型训练，以预测未来指数走势。
### 文件 
eastmoney-craw.py  
### 编写语言 
python3   
### 编写思路  
1、获取某股票股吧的总页数：由函数 get_page_num实现，采用二分法  
2、给定股票代码、页码，抓取该页所有帖子信息的功能: 由函数 main实现。东方新财富股吧的网页链接有规律可循，链接组合为：http://guba.eastmoney.comn/list,+skcdcode+,f_+page+.html, 因此只要知道股票代码及页码，就能爬取该股票股吧在给定页码的网页内容：发帖标题、帖子回复数、帖子浏览数。此时点击帖子标题，就能进入新页面，其中内容包括:发帖内容、发帖时间。  
3、多线程爬虫：  由函数mkThread实现。给定股票代码、算出该股吧总页数后，每一页的爬取任务分配一个线程。  
4、数据储存：  由 函数 write_to_csv实现。每一只股票新建一个csv文件用于存放数据。
