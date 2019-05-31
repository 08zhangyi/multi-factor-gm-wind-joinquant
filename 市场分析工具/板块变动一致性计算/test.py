import textdistance

d = textdistance.Jaro().distance('testT', 'Ttest')
print(d)

import numpy as np

a = ['小明', '小红', '小方', '小丽']
b = [92, 87, 93, 89]
a = np.array(a)
print(a[np.argsort(b)][::-1])  # ['小方' '小明' '小丽' '小红']，从大到小排序


import Levenshtein
print(Levenshtein.jaro('testT', 'Ttest'))