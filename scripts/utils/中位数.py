a = [1,4,7,9]
b = [2,4,8, 8]

def middle_number(num_list1, num_list2):
    len_1 = len(num_list1)
    len_2 = len(num_list2)

    if (len_1 + len_2) % 2 == 0:
        middle_index = (len_1 + len_2) / 2
        index_1 = 0
        index_2 = 0
        for index in range(0, middle_index + 1):
            if num_list1[index_1] > num_list2[index_2]:
                index_1 += 1
            else:
                index_2 += 1

