import numpy as np

funds = [{"name":"SRI", "score":76.01, "return2y":62.83, "drawdown2y":-9.6},
         {"name":"OLP", "score":81.02, "return2y":62.66, "drawdown2y":-7.67},
         {"name":"JTL", "score":70.96, "return2y":60.39, "drawdown2y":-5.71},
         {"name":"UAE", "score":83.38, "return2y":59.62, "drawdown2y":-10.81},
         {"name":"HEO", "score":80, "return2y":56.07, "drawdown2y":-10.57},
         {"name":"SKN", "score":74.09, "return2y":45.54, "drawdown2y":-5.76},
         {"name":"IEB", "score":77.29, "return2y":43.52, "drawdown2y":-4.11},
         {"name":"ZCD", "score":84.82, "return2y":42.99, "drawdown2y":-6.45}]
    
weights = {"score":0.5, "returnDrawdownRatio":0.5}
scores = []
for fund in funds:
    scores.append(((fund["score"] * weights["score"]) + ((fund["return2y"] / fund["drawdown2y"]) * weights["returnDrawdownRatio"])) / sum(weights.values()))

capital = 3000
scoreToCapital = capital / sum(scores)
i = -1
for fund in funds:
    i += 1
    fund["portfolioAmount"] = np.round(scores[i] * scoreToCapital, 2)

for fund in funds:
    print(fund)
