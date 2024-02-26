#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/11/23
# @Author  : hehl
# @Software: PyCharm
# @File    : eval.py

import json

"""
    评估整体的性能
    可以先评估无约束的问题

"""


def create_ngram_list(input):
    input_list = input.lower().split(" ")
    ngram_list = []

    for num in range(len(input_list) + 1, -1, -1):
        for tmp in zip(*[input_list[i:] for i in range(num)]):
            tmp = " ".join(tmp)
            ngram_list.append(tmp)
    return ngram_list


if __name__ == '__main__':
    print(create_ngram_list("x y z y"))
