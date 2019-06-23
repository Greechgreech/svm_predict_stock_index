# 上证50指数历史市场数据+SVM 预测明日指数走势
## 模型代码
数据获取、数据处理、模型训练及预测的代码均在文件：sz50-svm.ipynb中。其中，数据获取部份需要利用joinquant的数据库，因此建议用joinquant研究平台运行代码。
不使用joinquant的替代办法:所有从joinquant上获取的数据、利用数据构建的特征存放于dataset.xlsx中，因此只需：
'''
import pandas as pd
df = pd.read_excel('dataset.xlsx')
'''
便可跳过获取数据、构建特征的步骤（单元格2-8），开始进行缺失值处理。

##输出文件
dataset.xlsx  ： 2010-01-01~2019-06-01 2285个样本，36个特征
data_stat :  特征的统计性描述（加注释）
data_stat_raw :  特征的统计性描述（未加注释）
