import pandas as pd

from sklearn.model_selection import (
    train_test_split
)

from sklearn.linear_model import (
    LinearRegression
)

from sklearn.metrics import (
    mean_squared_error,
    r2_score
)

# 讀取資料
df = pd.read_csv(
    "dashboard/ml_dataset.csv"
)

# Features
X = df[
    [
        "ma5",
        "ma20",
        "volatility",
        "volume"
    ]
]

# Target
y = df["target"]

# 切分資料
X_train, X_test, y_train, y_test = (
    train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )
)

# 建立模型
model = LinearRegression()

# 訓練
model.fit(
    X_train,
    y_train
)

# 預測
predictions = model.predict(
    X_test
)

# 評估
mse = mean_squared_error(
    y_test,
    predictions
)

r2 = r2_score(
    y_test,
    predictions
)

print(f"MSE: {mse}")
print(f"R2 Score: {r2}")

import matplotlib.pyplot as plt

plt.figure(figsize=(10, 5))

plt.plot(
    y_test.values[:100],
    label="Actual"
)

plt.plot(
    predictions[:100],
    label="Predicted"
)

plt.legend()

plt.show()