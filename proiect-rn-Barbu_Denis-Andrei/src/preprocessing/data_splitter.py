def split_time_series_data(X, y, dates, train_ratio=0.9):
    split_idx = int(len(X) * train_ratio)
    return X[:split_idx], X[split_idx:], y[:split_idx], y[split_idx:], dates[split_idx:]