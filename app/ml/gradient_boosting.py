import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

class FastRegressionTree:
    def __init__(self, max_depth=3, min_samples_split=10, n_feature_samples=None):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.n_feature_samples = n_feature_samples

    def fit(self, X, y):
        X = X.to_numpy() if hasattr(X, 'to_numpy') else X
        y = y.to_numpy() if hasattr(y, 'to_numpy') else y
        self.tree = self._build_tree(X, y, depth=0)
        return self

    def _fast_mse(self, y):
        return np.var(y) if len(y) > 0 else 0

    def _best_split(self, X, y):
        n_samples, n_features = X.shape
        best_mse = float('inf')
        best_feature, best_threshold = None, None

        features = (np.random.choice(n_features, self.n_feature_samples, replace=False)
                    if self.n_feature_samples and self.n_feature_samples < n_features else range(n_features))

        for feature in features:
            sorted_idx = np.argsort(X[:, feature])
            feature_sorted = X[sorted_idx, feature]
            y_sorted = y[sorted_idx]

            n_splits = min(20, n_samples // 10)
            split_indices = [int(p / 100 * n_samples) for p in np.linspace(10, 90, n_splits)]
            split_indices = [idx for idx in split_indices if 0 < idx < n_samples]

            for idx in split_indices:
                if feature_sorted[idx] == feature_sorted[idx - 1]:
                    continue
                threshold = (feature_sorted[idx] + feature_sorted[idx - 1]) / 2
                left_y, right_y = y_sorted[:idx], y_sorted[idx:]
                if len(left_y) < self.min_samples_split or len(right_y) < self.min_samples_split:
                    continue
                mse_total = (len(left_y) * self._fast_mse(left_y) + len(right_y) * self._fast_mse(right_y)) / n_samples
                if mse_total < best_mse:
                    best_mse = mse_total
                    best_feature, best_threshold = feature, threshold
        return best_feature, best_threshold

    def _build_tree(self, X, y, depth):
        if depth >= self.max_depth or len(y) < 2 * self.min_samples_split:
            return np.mean(y)
        feature, threshold = self._best_split(X, y)
        if feature is None:
            return np.mean(y)
        left_idx = X[:, feature] <= threshold
        right_idx = ~left_idx
        if np.sum(left_idx) == 0 or np.sum(right_idx) == 0:
            return np.mean(y)
        left_branch = self._build_tree(X[left_idx], y[left_idx], depth + 1)
        right_branch = self._build_tree(X[right_idx], y[right_idx], depth + 1)
        return (feature, threshold, left_branch, right_branch)

    def _predict_one(self, x, node):
        if not isinstance(node, tuple):
            return node
        feature, threshold, left, right = node
        return self._predict_one(x, left) if x[feature] <= threshold else self._predict_one(x, right)

    def predict(self, X):
        X = X.to_numpy() if hasattr(X, 'to_numpy') else X
        return np.array([self._predict_one(x, self.tree) for x in X])



# Fast GBM Classifier

class FastGBMClassifier:
    def __init__(self, n_estimators=100, learning_rate=0.1, max_depth=3, subsample=0.8,
                 n_feature_samples='sqrt', early_stopping_rounds=10):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.subsample = subsample
        self.n_feature_samples = n_feature_samples
        self.early_stopping_rounds = early_stopping_rounds

    def fit(self, X, y, X_val=None, y_val=None):
        import time
        start_time = time.time()

        X = X.to_numpy() if hasattr(X, 'to_numpy') else X
        y = y.to_numpy() if hasattr(y, 'to_numpy') else y

        self.classes_ = np.unique(y)
        self.n_classes_ = len(self.classes_)
        n_samples, n_features = X.shape

        # Determine number of features per split
        if self.n_feature_samples == 'sqrt':
            n_feat_samples = int(np.sqrt(n_features))
        elif self.n_feature_samples == 'log2':
            n_feat_samples = int(np.log2(n_features))
        else:
            n_feat_samples = self.n_feature_samples or n_features

        self.class_to_idx_ = {cls: idx for idx, cls in enumerate(self.classes_)}
        y_indices = np.array([self.class_to_idx_[cls] for cls in y])
        y_onehot = np.eye(self.n_classes_)[y_indices]

        if X_val is None:
            X_train, X_val, y_train, y_val, y_onehot_train, y_onehot_val = train_test_split(
                X, y_indices, y_onehot, test_size=0.2, random_state=42, stratify=y_indices
            )
        else:
            X_val = X_val.to_numpy() if hasattr(X_val, 'to_numpy') else X_val
            y_val = y_val.to_numpy() if hasattr(y_val, 'to_numpy') else y_val
            y_val_indices = np.array([self.class_to_idx_[cls] for cls in y_val])
            y_onehot_val = np.eye(self.n_classes_)[y_val_indices]
            X_train, y_train, y_onehot_train = X, y_indices, y_onehot

        self.trees_ = [[] for _ in range(self.n_classes_)]
        pred = np.zeros((X_train.shape[0], self.n_classes_))
        val_pred = np.zeros((X_val.shape[0], self.n_classes_))

        best_val_accuracy = 0
        best_iteration = 0
        no_improvement_count = 0

        for i in range(self.n_estimators):
            # Subsample for stochastic gradient boosting
            if self.subsample < 1.0:
                sample_idx = np.random.choice(X_train.shape[0],
                                              int(X_train.shape[0] * self.subsample),
                                              replace=False)
            else:
                sample_idx = slice(None)

            # Softmax probabilities
            max_vals = np.max(pred[sample_idx], axis=1, keepdims=True)
            exp_pred = np.exp(pred[sample_idx] - max_vals)
            prob = exp_pred / np.sum(exp_pred, axis=1, keepdims=True)

            # Fit trees for each class
            for k in range(self.n_classes_):
                residual = prob[:, k] - y_onehot_train[sample_idx, k]
                tree = FastRegressionTree(max_depth=self.max_depth, n_feature_samples=n_feat_samples)
                tree.fit(X_train[sample_idx], residual)
                update = tree.predict(X_train[sample_idx])
                pred[sample_idx, k] -= self.learning_rate * update
                val_pred[:, k] -= self.learning_rate * tree.predict(X_val)
                self.trees_[k].append(tree)

            train_acc = self._calculate_accuracy(pred, y_train)
            val_acc = self._calculate_accuracy(val_pred, y_val)

            # Early stopping
            if val_acc > best_val_accuracy:
                best_val_accuracy = val_acc
                best_iteration = i
                no_improvement_count = 0
            else:
                no_improvement_count += 1
            if no_improvement_count >= self.early_stopping_rounds:
                # Keep only best iteration trees
                for k in range(self.n_classes_):
                    self.trees_[k] = self.trees_[k][:best_iteration + 1]
                break

        total_time = time.time() - start_time
        print(f"FastGBM training completed in {total_time:.2f} seconds")
        print(f"Final training accuracy: {train_acc:.4f}, validation accuracy: {val_acc:.4f}")
        return self

    def _calculate_accuracy(self, logits, y_true_indices):
        proba = self._softmax(logits)
        predictions = np.argmax(proba, axis=1)
        return accuracy_score(y_true_indices, predictions)

    def _softmax(self, x):
        exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=1, keepdims=True)

    def predict_proba(self, X):
        X = X.to_numpy() if hasattr(X, 'to_numpy') else X
        n_samples = X.shape[0]
        pred = np.zeros((n_samples, self.n_classes_))
        for k in range(self.n_classes_):
            for tree in self.trees_[k]:
                pred[:, k] -= self.learning_rate * tree.predict(X)
        return self._softmax(pred)

    def predict(self, X):
        proba = self.predict_proba(X)
        return self.classes_[np.argmax(proba, axis=1)]