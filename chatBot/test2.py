import random

compress = random.choices([True, False], weights=[1-(1000/20000),1000/20000], k=10)
print(compress)