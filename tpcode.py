# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 20:23:23 2019

@author: nehap
"""

import time
start_time = time.time()
# your script
t = 0
for i in range(1,10000000000):
    t = t+1

elapsed_time = time.time() - start_time
print(elapsed_time)