import random
import sys

# argv[1]: ID (Starts from 0 for each test case group)
# argv[2]: Random seed (Generated from the test case group's name and the case's ID)
seed = int(sys.argv[2])
random.seed(seed)

x = random.randint(0, 99)
y = random.randint(0, 99)
print(x, y)
