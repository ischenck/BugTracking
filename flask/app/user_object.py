#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 19:05:20 2019

@author: tony
"""

ACCESS = {
        'nonuser':0,
        'user': 1,
        'admin':2
        }

class User():
    def __init__(self, username,level):
        self.username = username
        self.level = level
        