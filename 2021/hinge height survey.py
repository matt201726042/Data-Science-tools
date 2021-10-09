l = "6,6.3,5.7,5.11,6.4,5.9,6.3,5.10,6.1,6,6.1,5.11,5.7,6,5.10,6.2,6.1,6.2,5.7,6,5.9,5.10,5.8,5.9,6.1,5.8,5.11,5.9,5.8,6.1,5.6,6.2,5.9,5.11,6,5.10,6.1,6,5.8,5.5,6,5.4,5.7,6.2,5.11,5.11,5.11,5.10,5.11,5.9,6.1,5.7,6.1,5.10,5.10,5.8,6.1,5.5,5.10,6.2,5.9,5.11,6,5.10,5.6,5.8,6.1,5.11,6.2,6.1,6.1,6.3,5.6,5.7,5.7,6.6,5.9,5.11,5.8,6.3,6.2,5.9,5.7,5.11,5.11,5.10,5.11,6,5.11,6.2,5.9,5.5,6.6,5.8,6.1,5.5,5.11,5.11,6,5.8,5.9,5.10,6.2,5.4,6,5.9,5.3,6,6,6,6.2,5.10,6.3,5.9,5.9,6,5.9,5.10,6.4,5.11,6.2,5.8,5.6,5.5,5.7,5.10,6,6.1,5.11,6.1,6.2,5.10,5.2,5.10,6.2,6.2,6.1,6.1,5.10,5.8,5.11,6,6.1,5.10,6.1,5.8,5.11,5.10,6.1,5.11,5.8,5.7,5.5,6.1,5.10,5.8,5.11,6,6.1,5.11,6,5.8,6,6,5.7,6.3,5.10,5.11,5.7,6.1,5.9,6,6,5.7,5.11,5.10,6.2,5.9,6.0,5.10,5.8,5.5,6.3,5.11,6,6.1,5.10,5.8,5.10,6,5.5,5.9,5.10,5.9,6,5.9,5.8,5.8,5.9,5.8,5.9,6.4,6.1,6,6,6,5.11,5.9,6.3,5.10"
l = l.split(",")
for i in range(len(l)):
    parts = l[i].split(".")
    if len(parts) > 1:
        l[i] = int(parts[0]) + (int(parts[1]) / 12)
    l[i] = float(l[i])

import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt

l.sort()

a = [[str(x),l.count(x)] for x in sorted(set((l)))]

objects = []
for i in range(len(a)):
    try:
        objects.append(a[i][0].split(".")[0] + "\"" + str(round(float("0." + a[i][0].split(".")[1]) * (12/1))))
    except:
        objects.append(a[i][0].split(".")[0])
y_pos = np.arange(len(objects))
performance = [a[i][1] for i in range(len(a))]

plt.bar(y_pos, performance, align='center', alpha=0.5)
plt.xticks(y_pos, objects)
plt.ylabel('Amount')
plt.title('Heights of gay or bi males on Hinge ages 18-19 within 10 miles of London')

plt.show()