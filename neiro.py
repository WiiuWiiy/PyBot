def add(a, b):           # positional
    return a + b

def power(base, exp=2):  # default argument
    return base ** exp

add(1, 2)                # 3
power(3)                 # 9
power(3, 3)              # 27
power(exp=3, base=2)     # 8  (keyword args)