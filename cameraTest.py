# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 18:12:16 2019

@author: stmor
"""

import directKeys as dk;
import time;

time.sleep(3);
for i in range(10):
    dk.MouseMoveTo(0,-50)
    time.sleep(1);
