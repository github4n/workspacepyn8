"""
程序开头注释
author: xingbuxing
date: 2018年01月11日
功能：本程序主要介绍python的函数
"""

"""
函数是编程当中最常用的概念，其目的是将一段功能完整的代码封装起来，方便之后的反复使用。
"""


# =====基本函数的定义
def print_two_var(str_var1, str_var2='hello world'):
    # 以下是函数内容
    # 函数的功能：将str_var1，str_var12变量的内容打印出来
    print(str_var1)
    print(str_var2)

    return '打印完成'

# 以def开头，代表define
# print_two_var是函数名，可以自己随便取，但是要有意义
# str_var是参数，参数的数量可以有很多个，可以带上默认参数
# 函数首行的最后需要带上冒号，初学最容易忘记
# 函数内容需要使用tab键进行缩进，在键盘左边
# 函数的输出，通过return来返回。运行到return语句之后，整个函数运行结束。return可以不加


# =====调用函数
# 直接使用函数名，即可调用函数。
# print_two_var(str_var1='你好，世界')
# print_two_var(str_var1='你好，世界', str_var2='你好，数字货币')

# 函数名不能拼错

# 函数需要先定义，再调用

# 函数的return值
temp = print_two_var(str_var1='你好，世界')
print(temp)


