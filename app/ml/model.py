# -*- coding: utf-8 -*-
import numpy as np
import random
from collections import Counter
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.metrics import accuracy_score

class Node:
    """Decision tree node implementation"""
    def __init__(self, feature_idx=None, threshold=None, left=None, right=None, *, value=None):
        self.feature_idx = feature_idx
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value  # For leaf nodes

    def is_leaf(self):
        return self.value is not None

def entropy(labels):
    """Calculate entropy for multi-class labels"""
    counts = np.bincount(labels)
    probs = counts / len(labels)
    return -np.sum([p * np.log2(p) for p in probs if p > 0])

def information_gain(parent, left, right):
    """Calculate information gain for multi-class"""
    p = len(parent)
    if p == 0:
        return 0
    ig = entropy(parent) - (len(left)/p)*entropy(left) - (len(right)/p)*entropy(right)
    return ig

def find_best_split(X, y, max_features, min_samples_leaf):
    """Efficient split finding with feature subsampling"""
    n_samples, n_features = X.shape
    best_gain = -1
    best_feature = None
    best_threshold = None

    # Feature subsampling
    features = random.sample(range(n_features), max_features)

    for feature_idx in features:
        # Get unique values efficiently
        thresholds = np.unique(X[:, feature_idx])
        if len(thresholds) > 100:  # Limit splits for continuous features
            percentiles = np.linspace(0, 100, 50)
            thresholds = np.percentile(X[:, feature_idx], percentiles)

        for threshold in thresholds:
            # Split data
            left_mask = X[:, feature_idx] <= threshold
            right_mask = ~left_mask

            # Skip if child too small
            if np.sum(left_mask) < min_samples_leaf or np.sum(right_mask) < min_samples_leaf:
                continue

            # Calculate information gain
            gain = information_gain(y, y[left_mask], y[right_mask])

            # Update best split
            if gain > best_gain:
                best_gain = gain
                best_feature = feature_idx
                best_threshold = threshold

    return best_feature, best_threshold, best_gain

def build_tree(X, y, max_depth, min_samples_split, min_samples_leaf, max_features, depth=0):
    """Recursive tree building with stopping conditions"""
    # Stopping conditions
    if (depth >= max_depth or
        len(y) < min_samples_split or
        len(np.unique(y)) == 1):
        leaf_value = Counter(y).most_common(1)[0][0]
        return Node(value=leaf_value)

    # Find best split
    feature_idx, threshold, gain = find_best_split(
        X, y, max_features, min_samples_leaf
    )

    # If no split improves information gain
    if gain < 0.001:
        leaf_value = Counter(y).most_common(1)[0][0]
        return Node(value=leaf_value)

    # Split data
    left_mask = X[:, feature_idx] <= threshold
    right_mask = ~left_mask

    # Build subtrees
    left_subtree = build_tree(
        X[left_mask], y[left_mask], max_depth, min_samples_split,
        min_samples_leaf, max_features, depth+1
    )
    right_subtree = build_tree(
        X[right_mask], y[right_mask], max_depth, min_samples_split,
        min_samples_leaf, max_features, depth+1
    )

    return Node(feature_idx, threshold, left_subtree, right_subtree)

class RandomForest(BaseEstimator, ClassifierMixin):
    """Scikit-learn compatible random forest classifier"""
    def __init__(self, n_estimators=100, max_features='sqrt', max_depth=10,
                 min_samples_split=2, min_samples_leaf=1, oob_score=False):
        self.n_estimators = n_estimators
        self.max_features = max_features
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.oob_score = oob_score
        self.trees = []
        self.feature_importances = None
        self.oob_error = None

    def fit(self, X, y):
        """Train random forest with proper OOB scoring"""
        n_samples, n_features = X.shape

        # Set max_features
        if self.max_features == 'sqrt':
            max_features = int(np.sqrt(n_features))
        elif self.max_features == 'log2':
            max_features = int(np.log2(n_features))
        else:
            max_features = self.max_features

        # Initialize feature importances and OOB prediction matrix
        feature_importances = np.zeros(n_features)
        oob_predictions = np.zeros((n_samples, len(np.unique(y))))
        oob_counts = np.zeros(n_samples)  # To count OOB votes per sample

        self.trees = []  # Clear trees if re-fitting

        # Build each tree
        for _ in range(self.n_estimators):
            # Bootstrap sample
            bootstrap_indices = np.random.choice(n_samples, n_samples, replace=True)
            oob_indices = list(set(range(n_samples)) - set(bootstrap_indices))

            X_bootstrap = X[bootstrap_indices]
            y_bootstrap = y[bootstrap_indices]

            # Build tree
            tree = build_tree(
                X_bootstrap, y_bootstrap, self.max_depth,
                self.min_samples_split, self.min_samples_leaf, max_features
            )
            self.trees.append(tree)

            # OOB prediction accumulation
            if self.oob_score and oob_indices:
                oob_preds = self._predict_tree(tree, X[oob_indices])
                for i, idx in enumerate(oob_indices):
                    oob_predictions[idx, oob_preds[i]] += 1
                    oob_counts[idx] += 1

        # Normalize feature importances (if tracking them)
        self.feature_importances = feature_importances / max(1, feature_importances.sum())

        # Compute OOB error
        if self.oob_score:
            # Only use samples with at least one OOB prediction
            mask = oob_counts > 0
            final_preds = np.argmax(oob_predictions[mask], axis=1)
            true_labels = y[mask]
            self.oob_error = 1 - accuracy_score(true_labels, final_preds)
            print(f"OOB Error: {self.oob_error:.4f}")


    def _predict_tree(self, tree, X):
        """Predict single tree"""
        return np.array([self._traverse_tree(x, tree) for x in X])

    def _traverse_tree(self, x, node):
        """Traverse tree for single sample"""
        if node.is_leaf():
            return node.value

        if x[node.feature_idx] <= node.threshold:
            return self._traverse_tree(x, node.left)
        else:
            return self._traverse_tree(x, node.right)

    def predict(self, X):
        """Predict with all trees"""
        tree_preds = np.array([self._predict_tree(tree, X) for tree in self.trees])
        return np.array([Counter(row).most_common(1)[0][0] for row in tree_preds.T])

    def predict_proba(self, X):
        """Predict class probabilities"""
        tree_preds = np.array([self._predict_tree(tree, X) for tree in self.trees])
        n_classes = len(np.unique(np.concatenate(tree_preds)))
        proba = np.zeros((X.shape[0], n_classes))
        
        for i in range(X.shape[0]):
            counts = np.bincount(tree_preds[:, i], minlength=n_classes)
            proba[i] = counts / counts.sum()
            
        return proba