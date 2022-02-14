import copy
import random
import time


def genrate_list(length:'int > 0' = 10, _min: 'int > 0' = 1, _max: 'int> 1' = 10, reverse=None):
    target_list = [random.randrange(_min, _max) for i in range(length)]
    if reverse is None:
        pass
    else:
        target_list.sort(reverse=reverse)
    print(target_list)
    return target_list

def laji_sort(target_list) :
    """
    垃圾排序
    """
    for i in range(len(target_list) - 1):
        max_index = i
        max_value = target_list[i]
        for j in range(i + 1, len(target_list)):
            if max_value < target_list[j]:
                max_value = target_list[j]
                max_index = j
        target_list[i], target_list[max_index] = max_value, target_list[i]
    print(target_list)
    return target_list

def bubble_sort(target_list):
    """
    冒泡排序
    """
    count = 0
    for i in range(len(target_list)):
        swap_flag = False
        for j in range(len(target_list) - i - 1):
            if target_list[j] > target_list[j+1]:
                target_list[j], target_list[j+1] = target_list[j+1],  target_list[j]
                swap_flag = True
            count += 1
        if swap_flag == False:
           break
    print(count)
    print(target_list)
    return target_list


def quick_sort(target_list):
    if len(target_list)<2:
        return target_list
    else:
        midpivot = target_list[0]
        lessbeforemidpivot = [i for i in target_list[1:] if i<=midpivot]
        biggerafterpivot = [i for i in target_list[1:] if i > midpivot]
        finallylist = quick_sort(lessbeforemidpivot) + [midpivot] + quick_sort(biggerafterpivot)
        return finallylist

# 汉若塔问题
def hanota(target_list, temp_list, result_list):
    n = len(target_list)
    def move(n, target_list, temp_list, result_list):
        if n == 1:
            result_list.append(target_list.pop())
        else:
            move(n - 1, target_list, result_list, temp_list)
            result_list.append(target_list[-1])
            target_list.pop()
            move(n-1, temp_list, target_list, result_list)

    move(n, target_list, temp_list, result_list)
    print(result_list)

# 小青蛙跳阶台
# 一只青蛙一次可以跳上1级台阶，也可以跳上2级。求该青蛙跳上一个n级的台阶总共有多少种跳法。
# 第一种跳法：第一次我跳了一个台阶，那么还剩下n-1个台阶还没跳，剩下的n-1个台阶的跳法有f(n-1)种。

# 第二种跳法：第一次跳了两个台阶，那么还剩下n-2个台阶还没，剩下的n-2个台阶的跳法有f(n-2)种。
# 优化方法, 避免重复计算, 将每次计算结果保存下来

def fn(n):
    result = {

    }
    def inner(n):
        nonlocal result
        if result.__contains__(n):
            return result[n]
        elif n <= 2:
            result[n] = n
            return result[n]
        count = inner(n-2) + inner(n-1)
        result[n] = count
        return result[n]
    inner(n)
    print(result)

# 递归乘法
# 递归乘法。 写一个递归函数，不使用 * 运算符， 实现两个正整数的相乘。可以使用加号、减号、位移，但要吝啬一些。

def my_multiply(a, b):
    if a < b:
        a, b, = b, a
    if b == 1:
        return a
    else:
        return a + my_multiply(a, b - 1)


if __name__ == "__main__":
    target_list = genrate_list(length=500, reverse=True)
    # 快排
    # target_list1 = copy.copy(target_list)
    # start = time.time()
    # quick_sort(target_list1)
    # print(time.time() - start)


    # 冒泡排序
    # target_list2 = copy.copy(target_list)
    # start = time.time()
    # bubble_sort(target_list2)
    # print(time.time()-start)


    # 汉若塔
    # hanota_list = genrate_list(length=10, reverse=False)
    # hanota(hanota_list, [], [])


    # 小青蛙跳台阶
    # fn(100)
    
    # 递归乘法
    # print(my_multiply(5, 60))
    wrapper()

