def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

def calculate_pi(n):
    pi = 0
    for i in range(n):
        pi += (-1)**i / (2*i + 1)
    return 4 * pi

if __name__ == "__main__":
    print("斐波那契数列的前10个数：")
    print([fibonacci(i) for i in range(10)])
    
    print(f"\n圆周率的近似值 (1000次迭代): {calculate_pi(1000)}")

