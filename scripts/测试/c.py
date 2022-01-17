# nums = [2,3,4,5,6,2,3,45,]


# counts, temp_nums = [], []


# for num in nums:
#     current_index = 0
#     for index, temp_num in  enumerate(temp_nums):
#         if num == temp_num:
#             counts[num] += 1
#         current_index = index
#     if current_index == len(temp_nums) - 1:
#         temp_nums.append(num) 
#         counts.append(1)

# max_index = None
# max_count = None
# for index, count in enumerate(counts):
#     if max_index is None:
#         max_count = count
#         max_index = index
#         continue
#     if max_count > max_index:
#         max_count = count
#         max_index = index


# def bbb():
#     a = yield
#     b = yield
#     yield 100
#     # yield 200
#     # yield 300
#     print(a, b)
#     for i in range(a, b):
#         yield i


# b = bbb()
# b.send(None) # 第一个send必须是None， 会覆盖第一个返回yield的值， 且会默认调用一次next
# b.send(3)
# b.send(6)
# print(list(b))

# [None, 200, 300, 3, 4, 5]


# async abc():
#     b = await requests.get('https://www.baidu.com')
#     print('b start')
#     print(b.content())
#     c = await request.get('https://www.jd.com')
#     print('c start')
#     print(c.content())
# import asyncio

# async def a():
#     async for i in range(100):
#         print(i)
# # print(a())
# loop = asyncio.get_event_loop()
# loop.run_until_complete(a())
# a = [1,2,3]
# b = [4,5,6]
# c = (i for i in b)

# print(c)

# print(a, id(a))
# # a += b
# # a.extend(c)
# a += c
# print(a, id(a))
# a = dict()
# 异常栈打印
import logging


def a():
    raise Exception('abcd')

def b():
    a()

def c():
    b()

def d():
    c()

import traceback


def e():
    try:
        d()
    except Exception as e:
        print("=============================", traceback.format_exc().split("\n"))
        logging.exception(f"avcd-------------{e}")
        print('ccc')
    return {} or "bbb"

print(e())

# class A:
#     __a = 1
#     def b(self):
#         self.__a = 2
#         print(self.__a)
#         print(A.__name__)

# a = A()
# a.b()



