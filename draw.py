# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
# # @Time    : 2023/3/22
# # @Author  : hehl
# # @Software: PyCharm
# @File    : draw.py

import matplotlib.pyplot as plt
import numpy as np

x = [0, 0.1, 0.2, 0.3, 0.4, 0.6, 0.8, 1]
y_1 = [63.17, 68.54, 68.14, 67.40, 66.68, 66.52, 68.18, 65.37]
y_7 = [66.77, 73.67, 73.47, 73.34, 72.63, 72.42, 71.99, 72.02]
y_5 = [67.18, 74.12, 74.21, 74.05, 74.02, 73.48, 73.02, 73.12]
y_3 = [65.42, 72.84, 72.53, 72.47, 72, 71.44, 70.86, 70.87]
y2 = [5966 / 1639, 9044 / 1639, 10390 / 1639, 11729 / 1639, 13866 / 1639, 16370 / 1639, 19846 / 1639, 21389 / 1639]

fig = plt.figure(figsize=(28, 12))
plt.rcParams.update({'font.size': 30})

ax = fig.add_subplot(121)

lns5 = ax.plot(x, y_1, '-', label=r'$\eta$=1.0')
lns1 = ax.plot(x, y_7, '-', label=r'$\eta$=0.7')
lns2 = ax.plot(x, y_5, '-', label=r'$\eta$=0.5')
lns4 = ax.plot(x, y_3, '-', label=r'$\eta$=0.3')

ax2 = ax.twinx()
lns3 = ax2.plot(x, y2, '--r', linewidth=2, label=r'Avg-$G$')

# added these three lines
lns = lns5 + lns1 + lns2 + lns4 + lns3
labs = [l.get_label() for l in lns]
ax.legend(lns, labs, loc=4)

# 画出最高点
ax.scatter(0.2, 74.21, s=100, facecolors='r', edgecolors='r')
ax.annotate(74.2, xy=(0.22, 74.21))

ax.grid()
ax.set_xlabel(r"(a) varied $\xi$ on WebQuestionSP")
ax.set_ylabel(r"Performance evaluation(F1%)")
ax2.set_ylabel(r"Average number of query graphs")
ax2.set_ylim(0, 14)
ax.set_ylim(58, 76)
#


cq_3 = [29.91, 41.09, 41.70, 42.38, 41.93, 41.19, 39.68, 39.85]
cq_5 = [30.79, 41.69, 42.85, 43.18, 42.19, 42.40, 42.11, 42.38]
cq_7 = [31.48, 41.60, 42.04, 42.52, 41.94, 42.09, 41.82, 42.08]
cq_1 = [28.81, 37.05, 37.37, 37.67, 37.37, 36.25, 36.01, 36.28]
cqy2 = [2777 / 800, 4797 / 800, 5315 / 800, 6043 / 800, 6724 / 800, 8333 / 800, 9742 / 800, 10619 / 800]

cq = fig.add_subplot(122)
cq_lns5 = cq.plot(x, cq_1, '-', label=r'$\eta$=1.0')
cq_lns2 = cq.plot(x, cq_7, '-', label=r'$\eta$=0.7')
cq_lns1 = cq.plot(x, cq_5, '-', label=r'$\eta$=0.5')
cq_lns4 = cq.plot(x, cq_3, '-', label=r'$\eta$=0.3')

cq2 = cq.twinx()
cq_lns3 = cq2.plot(x, cqy2, '--r', linewidth=2, label=r'Avg-$G$')

cqlns = cq_lns5 + cq_lns2 + cq_lns1 + cq_lns4 + cq_lns3
cqlabs = [l.get_label() for l in cqlns]
cq.legend(cqlns, cqlabs, loc=4)

cq.grid()
cq.set_xlabel(r"(b) varied $\xi$ on ComplexQuestion ")
cq.set_ylabel(r"Performance evaluation(F1%)")
cq2.set_ylabel(r"Average number of query graphs")
cq2.set_ylim(0, 14)
cq.set_ylim(28, 44)

cq.scatter(0.3, 43.18, s=100, facecolors='r', edgecolors='r')
cq.annotate(43.2, xy=(0.32, 43.18))

plt.subplots_adjust(wspace=0.25, top=0.96, bottom=0.1, left=0.05, right=0.95)
# plt.subplots_adjust()

foo_fig = plt.gcf()  # 'get current figure'
foo_fig.savefig('F1_L.eps', format='eps', dpi=600)
plt.show()
