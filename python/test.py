from src.utils.lists import iter_groups


list = [1, 2, 3, 4]
for item in iter_groups(list, 2):
    print(item)
