import signal
import time

signal.signal(signal.SIGTERM, signal.SIG_IGN)

B = 7

l, r = 0, 2**B
for _ in range(B):
    m = (l + r) // 2
    print("?", m, flush=True)
    res = int(input())
    if res == 1:
        r = m
    elif res == 0:
        l = m
    else:
        exit(1)

print("!", l, flush=True)

time.sleep(3.0)
