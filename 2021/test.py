### Gradient descent.
# mhist = [[],[]]
# j = -1
# I = 0
# while True:
#     j += 1
#     m = 250000
#     for i in range(20):
#         m = f(m, I)
#     mhist[0].append(I)
#     mhist[1].append(m)
#     if j == 1:
#         I += 1
#     elif j > 1: #y = mx + c
#         m = ((mhist[1][-1] - mhist[1][-2]) / (mhist[0][-1] - mhist[0][-2]))
#         c = mhist[1][-1] - (m * mhist[0][-1])
#         I = (0 - c)/m
#     print(I)

def f(m, I):
    return (m - I) * 1.08

### Binary search
upper = 250000
lower = 0
mHist = []
while True:
    m = 250000
    mid = (upper + lower) / 2
    I = mid
    for i in range(20):
        m = f(m, I)
    if m > 0:
        lower = mid
    else:
        upper = mid
    if len(mHist) > 0 and m == mHist[-1]:
        print(I, "found after", len(mHist), "iterations, giving remaining money", m)
        break
    mHist.append(m)