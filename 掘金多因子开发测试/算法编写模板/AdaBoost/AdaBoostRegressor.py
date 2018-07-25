import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import AdaBoostRegressor

# Create the dataset
rng = np.random.RandomState(1)
X1 = np.linspace(0, 6, 100)[:, np.newaxis]
X2 = np.linspace(3, 4, 100)[:, np.newaxis]
X = np.concatenate((X1, X2), axis=1)
y = np.sin(X1).ravel() + np.sin(6 * X1).ravel() + rng.normal(0, 0.1, X1.shape[0])

print(X.shape, y.shape)

# Fit regression model
regr_1 = DecisionTreeRegressor(max_depth=4)

regr_2 = AdaBoostRegressor(DecisionTreeRegressor(max_depth=4), n_estimators=300, random_state=rng)

regr_1.fit(X, y)
regr_2.fit(X, y)

# Predict
y_1 = regr_1.predict(X)
y_2 = regr_2.predict(X)

print(regr_2.get_params())

# Plot the results
# plt.figure()
# plt.scatter(X1, y, c="k", label="training samples")
# plt.plot(X1, y_1, c="g", label="n_estimators=1", linewidth=2)
# plt.plot(X1, y_2, c="r", label="n_estimators=300", linewidth=2)
# plt.xlabel("data")
# plt.ylabel("target")
# plt.title("Boosted Decision Tree Regression")
# plt.legend()
# plt.show()