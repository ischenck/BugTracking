#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 22:15:38 2019

@author: tony
"""

def write_file(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    with open(filename, 'wb') as file:
        file.write(data)
        
#read the file to input to db
def read_file(filename):
    print(filename)
    with open(filename, 'rb') as f:
        dat = f.read()
    return dat
