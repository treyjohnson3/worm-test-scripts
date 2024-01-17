
def add():
    tot = 0
    for i in range(1000000):
        tot += i
    print(tot)


def times():
    tot = 0
    for i in range(10000000):
        tot += i
    print(tot)


add()
times()
g = 0
for i in range(100000000):
    g += 1
print(g)
