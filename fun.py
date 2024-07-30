def f1(n):
    def f2(k):
        return 1 - (k-2)/((k-1)*(n-1))
    sigma = 1
    sum = 0
    for i in range(2, n+1):
        sigma *= f2(i)
        sum += sigma * (i-1)/(n-1)
    
    return sum / n

import numpy as np

def outer():
    arr = np.array([1, 2, 3])
    
    def inner():
        nonlocal arr
        arr[0] = 999
        
    inner()
    print(arr)  # 输出：[999   2   3]

outer()