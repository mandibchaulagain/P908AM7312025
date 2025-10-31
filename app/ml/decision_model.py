import pandas as pd
import numpy as np
import random
from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder

class TreeNode:
    def __init__(self, feature_idx=None, threshold=None, left=None, right=None, *, value=None):
        self.feature_idx = feature_idx
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value  # For leaf nodes
        self.samples = None  # Track samples at node
        self.class_distribution = None  # Track class distribution

    def is_leaf(self):
        return self.value is not None

class DecisionTreeClassifier:
    def __init__(self, criterion='entropy', max_depth=None, min_samples_split=2,
                 min_samples_leaf=1, max_features=None, ccp_alpha=0.0):
        self.criterion = criterion
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.max_features = max_features
        self.ccp_alpha = ccp_alpha  # Cost complexity pruning parameter
        self.root = None
        self.feature_importances_ = None
        self.tree_depth = 0

    def fit(self, X, y):
        self.n_classes_ = len(np.unique(y))
        self.n_features_ = X.shape[1]

        # Set max_features
        if self.max_features is None:
            max_features = self.n_features_
        elif self.max_features == 'sqrt':
            max_features = int(np.sqrt(self.n_features_))
        elif self.max_features == 'log2':
            max_features = int(np.log2(self.n_features_))
        else:
            max_features = self.max_features
        self.max_features = max_features

        # Build tree
        self.root = self._build_tree(X, y, depth=0)

        # Prune tree if ccp_alpha > 0
        if self.ccp_alpha > 0:
            self._prune_tree(self.root)

        # Calculate feature importances
        self._calculate_feature_importances()

        return self

    def _gini(self, y):
        """Calculate Gini impurity for a set of labels"""
        counts = np.bincount(y)
        probs = counts / len(y)
        return 1 - np.sum(probs ** 2)

    def _entropy(self, y):
        """Calculate entropy for a set of labels"""
        counts = np.bincount(y)
        probs = counts / len(y)
        return -np.sum([p * np.log2(p) for p in probs if p > 0])

    def _information_gain(self, parent, left, right):
        """Calculate information gain for a split"""
        if self.criterion == 'entropy':
            impurity = self._entropy
        else:  # gini
            impurity = self._gini

        p = len(parent)
        ig = impurity(parent) - (len(left)/p)*impurity(left) - (len(right)/p)*impurity(right)
        return ig

    def _find_best_split(self, X, y):
        """Find the best split for a node"""
        n_samples, n_features = X.shape
        best_gain = -float('inf')
        best_feature = None
        best_threshold = None

        # Feature subsampling
        features = np.random.choice(n_features, self.max_features, replace=False)

        for feature_idx in features:
            # Get unique values for this feature
            thresholds = np.unique(X[:, feature_idx])

            # For continuous features, consider midpoints between values
            if len(thresholds) > 10:
                percentiles = np.linspace(0, 100, 20)
                thresholds = np.percentile(X[:, feature_idx], percentiles)

            for threshold in thresholds:
                # Split data
                left_mask = X[:, feature_idx] <= threshold
                right_mask = ~left_mask

                # Skip if child too small
                if np.sum(left_mask) < self.min_samples_leaf or np.sum(right_mask) < self.min_samples_leaf:
                    continue

                # Calculate information gain
                gain = self._information_gain(y, y[left_mask], y[right_mask])

                # Update best split
                if gain > best_gain:
                    best_gain = gain
                    best_feature = feature_idx
                    best_threshold = threshold

        return best_feature, best_threshold, best_gain

    def _build_tree(self, X, y, depth):
        """Recursively build the decision tree"""
        # Update tree depth
        if depth > self.tree_depth:
            self.tree_depth = depth

        # Create node and track samples/class distribution
        node = TreeNode()
        node.samples = len(y)
        node.class_distribution = np.bincount(y, minlength=self.n_classes_)

        # Stopping conditions
        if (depth == self.max_depth or
            len(y) < self.min_samples_split or
            len(np.unique(y)) == 1):
            node.value = np.argmax(node.class_distribution)
            return node

        # Find best split
        feature_idx, threshold, gain = self._find_best_split(X, y)

        # If no valid split found
        if gain < 1e-5:  # Small gain threshold
            node.value = np.argmax(node.class_distribution)
            return node

        # Split data
        left_mask = X[:, feature_idx] <= threshold
        right_mask = ~left_mask

        # Build subtrees
        node.feature_idx = feature_idx
        node.threshold = threshold
        node.left = self._build_tree(X[left_mask], y[left_mask], depth+1)
        node.right = self._build_tree(X[right_mask], y[right_mask], depth+1)

        return node

    def _prune_tree(self, node):
        """Recursively prune the tree using cost complexity pruning"""
        # If leaf node, nothing to prune
        if node.is_leaf():
            return 0, node.class_distribution[0] if node.value is not None else 0

        # Prune left and right subtrees
        left_leafs, left_impurity = self._prune_tree(node.left)
        right_leafs, right_impurity = self._prune_tree(node.right)

        # Calculate total leafs and impurity
        total_leafs = left_leafs + right_leafs
        total_impurity = left_impurity + right_impurity

        # Calculate cost complexity if we were to prune this node
        node_impurity = self._gini(node.class_distribution) * node.samples
        cost_complexity = (node_impurity - total_impurity) / (total_leafs - 1)

        # Prune if cost complexity is less than alpha
        if cost_complexity < self.ccp_alpha:
            # Convert to leaf node
            node.value = np.argmax(node.class_distribution)
            node.left = None
            node.right = None
            return 1, node_impurity

        return total_leafs, total_impurity

    def _calculate_feature_importances(self):
        """Calculate feature importances based on Gini importance"""
        importances = np.zeros(self.n_features_)
        stack = [self.root]

        while stack:
            node = stack.pop()

            if not node.is_leaf():
                # Calculate node impurity reduction
                impurity_reduction = (
                    (node.samples / self.root.samples) *
                    (self._gini(node.class_distribution)) -
                    (node.left.samples / node.samples) * self._gini(node.left.class_distribution) -
                    (node.right.samples / node.samples) * self._gini(node.right.class_distribution)
                )

                importances[node.feature_idx] += impurity_reduction

                stack.append(node.left)
                stack.append(node.right)

        # Normalize importances
        if np.sum(importances) > 0:
            importances /= np.sum(importances)

        self.feature_importances_ = importances

    def predict(self, X):
        """Predict class labels for samples in X"""
        return np.array([self._traverse_tree(x, self.root) for x in X])

    def predict_proba(self, X):
        """Predict class probabilities for samples in X"""
        probas = []
        for x in X:
            node = self.root
            while not node.is_leaf():
                if x[node.feature_idx] <= node.threshold:
                    node = node.left
                else:
                    node = node.right
            # Return normalized class distribution
            dist = node.class_distribution
            probas.append(dist / np.sum(dist))
        return np.array(probas)

    def _traverse_tree(self, x, node):
        """Traverse tree for a single sample"""
        while not node.is_leaf():
            if x[node.feature_idx] <= node.threshold:
                node = node.left
            else:
                node = node.right
        return node.value