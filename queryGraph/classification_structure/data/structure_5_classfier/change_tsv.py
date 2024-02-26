#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/13
# @Author  : hehl
# @Software: PyCharm
# @File    : change_tsv.py


# with open('train_e_data_oversampling_shuffle.csv',encoding="utf-8") as f:
#     data = f.read().replace(',', '\t')
# with open('train_e_data_oversampling_shuffle.tsv','w',encoding="utf-8") as f:
#     f.write(data)
#
# with open('test_e.csv',encoding="utf-8") as f:
#     data = f.read().replace(',', '\t')
# with open('test_e.tsv','w',encoding="utf-8") as f:
#     f.write(data)

with open('WQ_test_all_2032.csv',encoding="utf-8") as f:
    data = f.read().replace(',', '\t')
with open('WQ_test_all_2032.tsv','w',encoding="utf-8") as f:
    f.write(data)
"""
    用replace方法将,替换成\t
    然后在写入文件的时候，后缀名为tsv即可
"""