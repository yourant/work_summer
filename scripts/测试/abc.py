# def my_sort(origin_list):
#     for i in range(len(origin_list)):
#         for j in range(i+1, len(origin_list)):
#             if origin_list[i] > origin_list[j]:
#                 origin_list[i], origin_list[j] = origin_list[j], origin_list[i]
#     return origin_list

# if __name__ == '__main__':
#     print(my_sort([3,2, 4, 1]))
#     print(list(reversed([4,3,1,2])))
#     print(list([2,1,4,3][-1::-1]))
#     sort_dict = {
#         'depart': 4,
#         'name': 2,
#         'age': 1,
#         'sex': 3
#     }
#     print(dict(sorted(sort_dict.items(), key=lambda item: item[1])))


# import threading
# import asyncio

# async def hello():
#     print('Hello world! (%s)' % threading.currentThread())
#     await asyncio.sleep(1)
#     print('Hello again! (%s)' % threading.currentThread())

# loop = asyncio.get_event_loop()
# tasks = [hello(), hello()]
# loop.run_until_complete(asyncio.wait(tasks))
# loop.close()

class A:
    __a = "abc"

    __c__ = 'bbb'

    @property
    def __a__(self):
        return self.__a
    
    @__a__.setter
    def __a__(self, a):
        self.__a = a
    

    def b(self):
        self.__a__ = "123"
    
    def c(self):
        print(self.__a, self.__a__)

    def d(self):
        self.__c__ = '1234455'
    
    def e(self):
        print(self.__c__)

    
c = A()
c.b()
c.c()
c.d()
c.e()