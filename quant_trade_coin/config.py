"""
@author: 邢不行
配置文件，配置文件根目录
"""
import os

# 获取当前程序的地址
current_file = __file__

# 程序根目录地址
root_path = os.path.abspath(os.path.join(current_file, os.pardir, os.pardir))
