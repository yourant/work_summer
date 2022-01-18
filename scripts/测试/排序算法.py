import random

def genrate_list(length=10, _min=1, _max=20):
    target_list = [random.randrange(_min, _max) for i in range(length)]
    print(target_list)
    return target_list

def bubble_sort(target_list) :
    """
    冒泡排序
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



# def once_quick_sort(target_list):
#     """
#     一次快排
#     """
#     if not target_list or not isinstance(target_list, (list, tuple)):
#         return target_list
#     i = 0
#     j = len(target_list)
#     flag_value = target_list[i]
#     for index in range(j):
#         if target_list[j] < flag_value:
#             target_list[j] = target_list[i]
#             continue
#         elif target_list[i] > flag_value:
#             pass



if __name__ == "__main__":
    target_list = genrate_list()
    # 冒泡排序
    # bubble_sort(target_list)
