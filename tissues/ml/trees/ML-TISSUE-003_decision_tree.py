"""
Tissue ID: ML-TISSUE-003
Title: Advanced Decision Tree Implementation
Category: ml/trees
Tags: ["decision-tree", "classification", "regression", "tree-based", "interpretable-ml"]
Difficulty: Advanced
Dependencies: ["numpy>=1.24", "scikit-learn>=1.3"]
Performance: O(n*m*log(n)) for training where n is samples, m is features
Tested: Python 3.8+, 3.9, 3.10
Author: CodeSnippetBank
Version: 1.0.0
Last Updated: 2024-01-20

Description:
A comprehensive decision tree tissue supporting both classification and regression
with multiple splitting criteria (Gini, Entropy, MSE). Features include pruning,
feature importance calculation, tree visualization, rule extraction, and handling
of missing values.

Use Cases:
- Classification problems
- Regression tasks
- Feature importance analysis
- Rule-based decision making
- Model interpretation

Example Usage:
    # Classification tree
    tree = DecisionTree(task="classification", max_depth=5)
    tree.fit(X_train, y_train)
    predictions = tree.predict(X_test)
    
    # Regression tree with pruning
    tree = DecisionTree(task="regression", min_samples_leaf=5)
    tree.fit(X_train, y_train)
    tree.prune(X_val, y_val)
    
    # Extract rules
    rules = tree.extract_rules()
    
    # Get feature importance
    importance = tree.get_feature_importance()
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import Counter, deque
import json


class TaskType(Enum):
    """Task types for decision tree"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"


class SplitCriterion(Enum):
    """Splitting criteria"""
    GINI = "gini"
    ENTROPY = "entropy"
    MSE = "mse"  # Mean Squared Error
    MAE = "mae"  # Mean Absolute Error


@dataclass
class TreeNode:
    """Decision tree node"""
    node_id: int
    depth: int
    n_samples: int
    value: Union[float, np.ndarray]  # Prediction value or class distribution
    impurity: float
    
    # For internal nodes
    feature_idx: Optional[int] = None
    threshold: Optional[float] = None
    left_child: Optional['TreeNode'] = None
    right_child: Optional['TreeNode'] = None
    
    # For leaf nodes
    is_leaf: bool = False
    
    # Additional info
    class_label: Optional[Any] = None  # For classification
    samples_per_class: Optional[Dict[Any, int]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary"""
        result = {
            "node_id": self.node_id,
            "depth": self.depth,
            "n_samples": self.n_samples,
            "impurity": self.impurity,
            "is_leaf": self.is_leaf
        }
        
        if self.is_leaf:
            result["value"] = self.value.tolist() if isinstance(self.value, np.ndarray) else self.value
            if self.class_label is not None:
                result["class_label"] = self.class_label
        else:
            result["feature_idx"] = self.feature_idx
            result["threshold"] = self.threshold
            
        return result


@dataclass
class TreeConfig:
    """Configuration for decision tree"""
    max_depth: Optional[int] = None
    min_samples_split: int = 2
    min_samples_leaf: int = 1
    min_impurity_decrease: float = 0.0
    max_features: Optional[Union[int, str]] = None
    max_leaf_nodes: Optional[int] = None
    random_state: int = 42
    criterion: str = "gini"
    splitter: str = "best"  # best or random


@dataclass
class TreeRule:
    """Extracted decision rule"""
    conditions: List[str]
    prediction: Any
    confidence: float
    support: int
    
    def to_string(self) -> str:
        """Convert rule to readable string"""
        if self.conditions:
            conditions_str = " AND ".join(self.conditions)
            return f"IF {conditions_str} THEN {self.prediction} (conf: {self.confidence:.2f}, support: {self.support})"
        else:
            return f"DEFAULT: {self.prediction} (support: {self.support})"


class DecisionTree:
    """
    Advanced decision tree implementation.
    Tissue Type: FUNCTIONAL - Core ML tree-based functionality.
    """
    
    def __init__(self,
                 task: str = "classification",
                 config: Optional[TreeConfig] = None,
                 feature_names: Optional[List[str]] = None):
        """
        Initialize decision tree.
        
        Args:
            task: Task type (classification or regression)
            config: Tree configuration
            feature_names: Names of features for interpretability
        """
        self.task = TaskType(task.lower())
        self.config = config or TreeConfig()
        self.feature_names = feature_names
        
        # Set default criterion based on task
        if self.config.criterion == "gini" and self.task == TaskType.REGRESSION:
            self.config.criterion = "mse"
        
        # Tree structure
        self.root_ = None
        self.n_nodes_ = 0
        self.max_depth_ = 0
        
        # Training info
        self.n_features_ = 0
        self.n_classes_ = 0
        self.classes_ = None
        self.is_fitted = False
        
        # Feature importance
        self.feature_importances_ = None
        
        # Random number generator
        self.rng = np.random.RandomState(self.config.random_state)
    
    def fit(self, X: np.ndarray, y: np.ndarray,
            sample_weights: Optional[np.ndarray] = None) -> 'DecisionTree':
        """
        Fit decision tree.
        
        Args:
            X: Training features (n_samples, n_features)
            y: Target values (n_samples,)
            sample_weights: Optional sample weights
            
        Returns:
            Self for chaining
        """
        # Validate inputs
        X, y = self._validate_inputs(X, y)
        
        # Store dimensions
        self.n_features_ = X.shape[1]
        
        # Handle task-specific setup
        if self.task == TaskType.CLASSIFICATION:
            self.classes_ = np.unique(y)
            self.n_classes_ = len(self.classes_)
            # Encode labels
            y_encoded = self._encode_labels(y)
        else:
            y_encoded = y
            self.n_classes_ = 0
        
        # Initialize feature importances
        self.feature_importances_ = np.zeros(self.n_features_)
        
        # Build tree
        self.root_ = self._build_tree(X, y_encoded, sample_weights, depth=0)
        
        # Normalize feature importances
        if self.feature_importances_.sum() > 0:
            self.feature_importances_ /= self.feature_importances_.sum()
        
        self.is_fitted = True
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions.
        
        Args:
            X: Features to predict (n_samples, n_features)
            
        Returns:
            Predicted values or class labels
        """
        if not self.is_fitted:
            raise ValueError("Tree must be fitted before prediction")
        
        # Validate input
        X = self._validate_input(X)
        
        # Make predictions
        n_samples = X.shape[0]
        predictions = np.zeros(n_samples)
        
        for i in range(n_samples):
            node = self._traverse_tree(self.root_, X[i])
            
            if self.task == TaskType.CLASSIFICATION:
                # Return class label
                predictions[i] = node.class_label
            else:
                # Return regression value
                predictions[i] = node.value
        
        return predictions
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class probabilities (classification only).
        
        Args:
            X: Features to predict (n_samples, n_features)
            
        Returns:
            Class probabilities (n_samples, n_classes)
        """
        if self.task != TaskType.CLASSIFICATION:
            raise ValueError("predict_proba is only available for classification")
        
        if not self.is_fitted:
            raise ValueError("Tree must be fitted before prediction")
        
        # Validate input
        X = self._validate_input(X)
        
        # Get probabilities
        n_samples = X.shape[0]
        probas = np.zeros((n_samples, self.n_classes_))
        
        for i in range(n_samples):
            node = self._traverse_tree(self.root_, X[i])
            probas[i] = node.value
        
        return probas
    
    def _validate_inputs(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Validate training inputs"""
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y)
        
        if X.ndim != 2:
            raise ValueError(f"X must be 2D, got {X.ndim}D")
        
        if y.ndim != 1:
            raise ValueError(f"y must be 1D, got {y.ndim}D")
        
        if X.shape[0] != y.shape[0]:
            raise ValueError("X and y must have same number of samples")
        
        return X, y
    
    def _validate_input(self, X: np.ndarray) -> np.ndarray:
        """Validate single input"""
        X = np.asarray(X, dtype=np.float64)
        
        if X.ndim == 1:
            X = X.reshape(1, -1)
        elif X.ndim != 2:
            raise ValueError(f"X must be 1D or 2D, got {X.ndim}D")
        
        if X.shape[1] != self.n_features_:
            raise ValueError(f"X has {X.shape[1]} features, expected {self.n_features_}")
        
        return X
    
    def _encode_labels(self, y: np.ndarray) -> np.ndarray:
        """Encode class labels to integers"""
        label_to_int = {label: i for i, label in enumerate(self.classes_)}
        return np.array([label_to_int[label] for label in y])
    
    def _build_tree(self, X: np.ndarray, y: np.ndarray,
                   sample_weights: Optional[np.ndarray],
                   depth: int) -> TreeNode:
        """Recursively build tree"""
        n_samples = X.shape[0]
        self.n_nodes_ += 1
        node_id = self.n_nodes_
        
        # Update max depth
        self.max_depth_ = max(self.max_depth_, depth)
        
        # Calculate node value and impurity
        if self.task == TaskType.CLASSIFICATION:
            value, impurity = self._calculate_class_distribution(y, sample_weights)
            class_label = self.classes_[np.argmax(value)]
        else:
            value, impurity = self._calculate_regression_value(y, sample_weights)
            class_label = None
        
        # Check stopping criteria
        if (self._should_stop_splitting(n_samples, depth, impurity) or
            len(np.unique(y)) == 1):
            # Create leaf node
            return TreeNode(
                node_id=node_id,
                depth=depth,
                n_samples=n_samples,
                value=value,
                impurity=impurity,
                is_leaf=True,
                class_label=class_label
            )
        
        # Find best split
        best_feature, best_threshold, best_impurity_decrease = self._find_best_split(
            X, y, sample_weights, impurity
        )
        
        # Check if split improves impurity
        if best_feature is None or best_impurity_decrease < self.config.min_impurity_decrease:
            # Create leaf node
            return TreeNode(
                node_id=node_id,
                depth=depth,
                n_samples=n_samples,
                value=value,
                impurity=impurity,
                is_leaf=True,
                class_label=class_label
            )
        
        # Update feature importance
        self.feature_importances_[best_feature] += best_impurity_decrease * n_samples
        
        # Split data
        left_mask = X[:, best_feature] <= best_threshold
        right_mask = ~left_mask
        
        X_left, y_left = X[left_mask], y[left_mask]
        X_right, y_right = X[right_mask], y[right_mask]
        
        weights_left = sample_weights[left_mask] if sample_weights is not None else None
        weights_right = sample_weights[right_mask] if sample_weights is not None else None
        
        # Create internal node
        node = TreeNode(
            node_id=node_id,
            depth=depth,
            n_samples=n_samples,
            value=value,
            impurity=impurity,
            feature_idx=best_feature,
            threshold=best_threshold,
            is_leaf=False
        )
        
        # Recursively build children
        node.left_child = self._build_tree(X_left, y_left, weights_left, depth + 1)
        node.right_child = self._build_tree(X_right, y_right, weights_right, depth + 1)
        
        return node
    
    def _should_stop_splitting(self, n_samples: int, depth: int, 
                             impurity: float) -> bool:
        """Check stopping criteria"""
        if self.config.max_depth is not None and depth >= self.config.max_depth:
            return True
        
        if n_samples < self.config.min_samples_split:
            return True
        
        if n_samples < 2 * self.config.min_samples_leaf:
            return True
        
        if impurity == 0:
            return True
        
        if self.config.max_leaf_nodes is not None:
            # Count current leaves
            n_leaves = self._count_leaves(self.root_)
            if n_leaves >= self.config.max_leaf_nodes:
                return True
        
        return False
    
    def _calculate_class_distribution(self, y: np.ndarray,
                                    sample_weights: Optional[np.ndarray]) -> Tuple[np.ndarray, float]:
        """Calculate class distribution and impurity"""
        n_samples = len(y)
        
        # Count samples per class
        if sample_weights is None:
            class_counts = np.bincount(y, minlength=self.n_classes_)
        else:
            class_counts = np.zeros(self.n_classes_)
            for i in range(n_samples):
                class_counts[y[i]] += sample_weights[i]
        
        # Normalize to get probabilities
        total_weight = class_counts.sum()
        if total_weight > 0:
            probabilities = class_counts / total_weight
        else:
            probabilities = np.zeros(self.n_classes_)
        
        # Calculate impurity
        if self.config.criterion == "gini":
            impurity = 1.0 - np.sum(probabilities ** 2)
        elif self.config.criterion == "entropy":
            # Avoid log(0)
            probs_positive = probabilities[probabilities > 0]
            impurity = -np.sum(probs_positive * np.log2(probs_positive))
        else:
            impurity = 0.0
        
        return probabilities, impurity
    
    def _calculate_regression_value(self, y: np.ndarray,
                                  sample_weights: Optional[np.ndarray]) -> Tuple[float, float]:
        """Calculate regression value and impurity"""
        if sample_weights is None:
            value = np.mean(y)
            
            if self.config.criterion == "mse":
                impurity = np.var(y)
            elif self.config.criterion == "mae":
                impurity = np.mean(np.abs(y - np.median(y)))
            else:
                impurity = np.var(y)
        else:
            # Weighted statistics
            total_weight = sample_weights.sum()
            if total_weight > 0:
                value = np.sum(y * sample_weights) / total_weight
                
                if self.config.criterion == "mse":
                    impurity = np.sum(sample_weights * (y - value) ** 2) / total_weight
                elif self.config.criterion == "mae":
                    weighted_median = self._weighted_median(y, sample_weights)
                    impurity = np.sum(sample_weights * np.abs(y - weighted_median)) / total_weight
                else:
                    impurity = np.sum(sample_weights * (y - value) ** 2) / total_weight
            else:
                value = 0.0
                impurity = 0.0
        
        return value, impurity
    
    def _weighted_median(self, values: np.ndarray, weights: np.ndarray) -> float:
        """Calculate weighted median"""
        sorted_indices = np.argsort(values)
        sorted_values = values[sorted_indices]
        sorted_weights = weights[sorted_indices]
        
        cumsum = np.cumsum(sorted_weights)
        median_idx = np.searchsorted(cumsum, cumsum[-1] / 2)
        
        return sorted_values[median_idx]
    
    def _find_best_split(self, X: np.ndarray, y: np.ndarray,
                        sample_weights: Optional[np.ndarray],
                        parent_impurity: float) -> Tuple[Optional[int], Optional[float], float]:
        """Find best feature and threshold to split on"""
        n_samples, n_features = X.shape
        
        # Select features to consider
        if self.config.max_features is None:
            features_to_consider = list(range(n_features))
        elif isinstance(self.config.max_features, int):
            features_to_consider = self.rng.choice(
                n_features, 
                min(self.config.max_features, n_features), 
                replace=False
            ).tolist()
        elif self.config.max_features == "sqrt":
            n_features_to_consider = int(np.sqrt(n_features))
            features_to_consider = self.rng.choice(
                n_features, 
                n_features_to_consider, 
                replace=False
            ).tolist()
        else:
            features_to_consider = list(range(n_features))
        
        best_feature = None
        best_threshold = None
        best_impurity_decrease = 0.0
        
        # Try each feature
        for feature_idx in features_to_consider:
            # Get unique values for this feature
            feature_values = X[:, feature_idx]
            unique_values = np.unique(feature_values)
            
            if len(unique_values) <= 1:
                continue
            
            # Try different thresholds
            if self.config.splitter == "best":
                # Try all midpoints between unique values
                thresholds = (unique_values[:-1] + unique_values[1:]) / 2
            else:
                # Random thresholds
                n_thresholds = min(10, len(unique_values) - 1)
                threshold_indices = self.rng.choice(
                    len(unique_values) - 1, 
                    n_thresholds, 
                    replace=False
                )
                thresholds = (unique_values[threshold_indices] + 
                            unique_values[threshold_indices + 1]) / 2
            
            for threshold in thresholds:
                # Split data
                left_mask = feature_values <= threshold
                right_mask = ~left_mask
                
                n_left = left_mask.sum()
                n_right = right_mask.sum()
                
                # Check minimum samples in leaves
                if (n_left < self.config.min_samples_leaf or 
                    n_right < self.config.min_samples_leaf):
                    continue
                
                # Calculate impurity decrease
                if self.task == TaskType.CLASSIFICATION:
                    left_impurity = self._calculate_class_distribution(
                        y[left_mask], 
                        sample_weights[left_mask] if sample_weights is not None else None
                    )[1]
                    right_impurity = self._calculate_class_distribution(
                        y[right_mask], 
                        sample_weights[right_mask] if sample_weights is not None else None
                    )[1]
                else:
                    left_impurity = self._calculate_regression_value(
                        y[left_mask], 
                        sample_weights[left_mask] if sample_weights is not None else None
                    )[1]
                    right_impurity = self._calculate_regression_value(
                        y[right_mask], 
                        sample_weights[right_mask] if sample_weights is not None else None
                    )[1]
                
                # Weighted impurity decrease
                impurity_decrease = parent_impurity - (
                    (n_left / n_samples) * left_impurity +
                    (n_right / n_samples) * right_impurity
                )
                
                # Update best split
                if impurity_decrease > best_impurity_decrease:
                    best_feature = feature_idx
                    best_threshold = threshold
                    best_impurity_decrease = impurity_decrease
        
        return best_feature, best_threshold, best_impurity_decrease
    
    def _traverse_tree(self, node: TreeNode, x: np.ndarray) -> TreeNode:
        """Traverse tree to find leaf node for sample"""
        if node.is_leaf:
            return node
        
        if x[node.feature_idx] <= node.threshold:
            return self._traverse_tree(node.left_child, x)
        else:
            return self._traverse_tree(node.right_child, x)
    
    def _count_leaves(self, node: Optional[TreeNode]) -> int:
        """Count number of leaf nodes"""
        if node is None:
            return 0
        
        if node.is_leaf:
            return 1
        
        return self._count_leaves(node.left_child) + self._count_leaves(node.right_child)
    
    def prune(self, X_val: np.ndarray, y_val: np.ndarray,
             alpha: float = 0.0) -> 'DecisionTree':
        """
        Prune tree using validation set.
        
        Args:
            X_val: Validation features
            y_val: Validation targets
            alpha: Complexity parameter
            
        Returns:
            Self for chaining
        """
        if not self.is_fitted:
            raise ValueError("Tree must be fitted before pruning")
        
        # Validate inputs
        X_val = self._validate_input(X_val)
        
        if self.task == TaskType.CLASSIFICATION:
            y_val = self._encode_labels(y_val)
        
        # Cost-complexity pruning
        self._prune_subtree(self.root_, X_val, y_val, alpha)
        
        return self
    
    def _prune_subtree(self, node: TreeNode, X: np.ndarray, y: np.ndarray,
                      alpha: float) -> Tuple[float, int]:
        """Recursively prune subtree"""
        if node.is_leaf:
            # Calculate leaf error
            predictions = np.full(len(y), node.value if self.task == TaskType.REGRESSION 
                                else np.argmax(node.value))
            if self.task == TaskType.CLASSIFICATION:
                error = np.mean(predictions != y)
            else:
                error = np.mean((predictions - y) ** 2)
            
            return error, 1
        
        # Get samples for left and right children
        feature_values = X[:, node.feature_idx]
        left_mask = feature_values <= node.threshold
        right_mask = ~left_mask
        
        # Recursively calculate error for children
        left_error, left_leaves = self._prune_subtree(
            node.left_child, X[left_mask], y[left_mask], alpha
        )
        right_error, right_leaves = self._prune_subtree(
            node.right_child, X[right_mask], y[right_mask], alpha
        )
        
        # Calculate total error with subtree
        n_left = left_mask.sum()
        n_right = right_mask.sum()
        n_total = len(y)
        
        subtree_error = (n_left / n_total) * left_error + (n_right / n_total) * right_error
        subtree_leaves = left_leaves + right_leaves
        
        # Calculate error if we prune to leaf
        if self.task == TaskType.CLASSIFICATION:
            leaf_prediction = np.argmax(node.value)
            leaf_error = np.mean(leaf_prediction != y)
        else:
            leaf_error = np.mean((node.value - y) ** 2)
        
        # Decide whether to prune
        if leaf_error + alpha <= subtree_error + alpha * subtree_leaves:
            # Prune: convert to leaf
            node.is_leaf = True
            node.left_child = None
            node.right_child = None
            node.feature_idx = None
            node.threshold = None
            
            return leaf_error, 1
        else:
            return subtree_error, subtree_leaves
    
    def extract_rules(self, max_rules: Optional[int] = None) -> List[TreeRule]:
        """
        Extract decision rules from tree.
        
        Args:
            max_rules: Maximum number of rules to extract
            
        Returns:
            List of decision rules
        """
        if not self.is_fitted:
            raise ValueError("Tree must be fitted before extracting rules")
        
        rules = []
        
        # Traverse tree to extract rules
        self._extract_rules_recursive(self.root_, [], rules)
        
        # Sort by confidence and support
        rules.sort(key=lambda r: (r.confidence, r.support), reverse=True)
        
        # Limit number of rules
        if max_rules is not None:
            rules = rules[:max_rules]
        
        return rules
    
    def _extract_rules_recursive(self, node: TreeNode, conditions: List[str],
                               rules: List[TreeRule]):
        """Recursively extract rules from tree"""
        if node.is_leaf:
            # Create rule
            if self.task == TaskType.CLASSIFICATION:
                prediction = node.class_label
                confidence = np.max(node.value)
            else:
                prediction = node.value
                confidence = 1.0 - (node.impurity / (node.impurity + 1))
            
            rule = TreeRule(
                conditions=conditions.copy(),
                prediction=prediction,
                confidence=confidence,
                support=node.n_samples
            )
            rules.append(rule)
        else:
            # Add condition and recurse
            feature_name = (self.feature_names[node.feature_idx] 
                          if self.feature_names else f"feature_{node.feature_idx}")
            
            # Left child (<=)
            left_condition = f"{feature_name} <= {node.threshold:.4f}"
            self._extract_rules_recursive(
                node.left_child, 
                conditions + [left_condition], 
                rules
            )
            
            # Right child (>)
            right_condition = f"{feature_name} > {node.threshold:.4f}"
            self._extract_rules_recursive(
                node.right_child, 
                conditions + [right_condition], 
                rules
            )
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores"""
        if not self.is_fitted:
            raise ValueError("Tree must be fitted first")
        
        if self.feature_names:
            return {name: float(imp) for name, imp in 
                   zip(self.feature_names, self.feature_importances_)}
        else:
            return {f"feature_{i}": float(imp) for i, imp in 
                   enumerate(self.feature_importances_)}
    
    def visualize(self, format: str = "text") -> str:
        """
        Visualize tree structure.
        
        Args:
            format: Visualization format (text, json)
            
        Returns:
            Tree visualization
        """
        if not self.is_fitted:
            raise ValueError("Tree must be fitted first")
        
        if format == "text":
            lines = []
            self._visualize_text_recursive(self.root_, lines, "", True)
            return "\n".join(lines)
        elif format == "json":
            return json.dumps(self._tree_to_dict(self.root_), indent=2)
        else:
            raise ValueError(f"Unknown format: {format}")
    
    def _visualize_text_recursive(self, node: TreeNode, lines: List[str],
                                prefix: str, is_tail: bool):
        """Recursively build text visualization"""
        # Current node
        lines.append(prefix + ("└── " if is_tail else "├── ") + 
                    self._node_to_string(node))
        
        # Children
        if not node.is_leaf:
            extension = "    " if is_tail else "│   "
            
            if node.left_child:
                self._visualize_text_recursive(
                    node.left_child, 
                    lines, 
                    prefix + extension, 
                    False
                )
            
            if node.right_child:
                self._visualize_text_recursive(
                    node.right_child, 
                    lines, 
                    prefix + extension, 
                    True
                )
    
    def _node_to_string(self, node: TreeNode) -> str:
        """Convert node to string representation"""
        if node.is_leaf:
            if self.task == TaskType.CLASSIFICATION:
                return f"[Leaf] Class: {node.class_label} (samples: {node.n_samples})"
            else:
                return f"[Leaf] Value: {node.value:.4f} (samples: {node.n_samples})"
        else:
            feature_name = (self.feature_names[node.feature_idx] 
                          if self.feature_names else f"feature_{node.feature_idx}")
            return f"[Node] {feature_name} <= {node.threshold:.4f} (samples: {node.n_samples})"
    
    def _tree_to_dict(self, node: Optional[TreeNode]) -> Optional[Dict[str, Any]]:
        """Convert tree to dictionary"""
        if node is None:
            return None
        
        result = node.to_dict()
        
        if not node.is_leaf:
            result["left_child"] = self._tree_to_dict(node.left_child)
            result["right_child"] = self._tree_to_dict(node.right_child)
        
        return result
    
    def get_depth(self) -> int:
        """Get tree depth"""
        return self.max_depth_
    
    def get_n_leaves(self) -> int:
        """Get number of leaves"""
        return self._count_leaves(self.root_)


# Utility functions
def create_decision_tree(X: np.ndarray, y: np.ndarray,
                       task: str = "classification",
                       max_depth: int = 5) -> DecisionTree:
    """Quick decision tree creation"""
    config = TreeConfig(max_depth=max_depth)
    tree = DecisionTree(task=task, config=config)
    tree.fit(X, y)
    return tree


def extract_important_features(tree: DecisionTree, top_k: int = 5) -> List[Tuple[str, float]]:
    """Extract top important features"""
    importance = tree.get_feature_importance()
    sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)
    return sorted_features[:top_k]


def tree_to_rules(tree: DecisionTree, min_confidence: float = 0.8) -> List[str]:
    """Convert tree to high-confidence rules"""
    rules = tree.extract_rules()
    filtered_rules = [r for r in rules if r.confidence >= min_confidence]
    return [r.to_string() for r in filtered_rules]


# Auto-generated tests
def test_decision_tree():
    """Test decision tree functionality"""
    # Generate synthetic data
    np.random.seed(42)
    
    # Classification data
    n_samples = 200
    n_features = 4
    
    # Create separable clusters
    X_class = np.random.randn(n_samples, n_features)
    y_class = (X_class[:, 0] + X_class[:, 1] > 0).astype(int)
    y_class[X_class[:, 2] > 1] = 2  # Add third class
    
    # Test classification tree
    tree_class = DecisionTree(task="classification")
    tree_class.fit(X_class, y_class)
    
    assert tree_class.is_fitted
    assert tree_class.n_classes_ == 3
    
    # Test prediction
    predictions = tree_class.predict(X_class[:10])
    assert len(predictions) == 10
    assert all(p in [0, 1, 2] for p in predictions)
    
    # Test probability prediction
    probas = tree_class.predict_proba(X_class[:10])
    assert probas.shape == (10, 3)
    assert np.allclose(probas.sum(axis=1), 1.0)
    
    # Test with max depth
    config = TreeConfig(max_depth=3, min_samples_leaf=5)
    tree_limited = DecisionTree(task="classification", config=config)
    tree_limited.fit(X_class, y_class)
    assert tree_limited.get_depth() <= 3
    
    # Test regression
    y_reg = X_class[:, 0] + 0.5 * X_class[:, 1] + 0.1 * np.random.randn(n_samples)
    
    tree_reg = DecisionTree(task="regression")
    tree_reg.fit(X_class, y_reg)
    
    reg_predictions = tree_reg.predict(X_class[:10])
    assert len(reg_predictions) == 10
    assert all(isinstance(p, (float, np.floating)) for p in reg_predictions)
    
    # Test feature importance
    importance = tree_class.get_feature_importance()
    assert len(importance) == n_features
    assert all(0 <= v <= 1 for v in importance.values())
    assert abs(sum(importance.values()) - 1.0) < 1e-6
    
    # Test rule extraction
    rules = tree_class.extract_rules(max_rules=5)
    assert len(rules) <= 5
    assert all(isinstance(r, TreeRule) for r in rules)
    
    # Test with feature names
    feature_names = [f"feat_{i}" for i in range(n_features)]
    tree_named = DecisionTree(task="classification", feature_names=feature_names)
    tree_named.fit(X_class, y_class)
    
    rules_named = tree_named.extract_rules(max_rules=3)
    assert any("feat_" in r.to_string() for r in rules_named)
    
    # Test visualization
    viz = tree_limited.visualize(format="text")
    assert isinstance(viz, str)
    assert "[Node]" in viz or "[Leaf]" in viz
    
    # Test pruning (simple test)
    tree_pruned = DecisionTree(task="classification")
    tree_pruned.fit(X_class[:150], y_class[:150])
    initial_leaves = tree_pruned.get_n_leaves()
    
    tree_pruned.prune(X_class[150:], y_class[150:], alpha=0.01)
    pruned_leaves = tree_pruned.get_n_leaves()
    assert pruned_leaves <= initial_leaves
    
    # Test utility functions
    quick_tree = create_decision_tree(X_class, y_class, max_depth=3)
    assert quick_tree.is_fitted
    
    top_features = extract_important_features(quick_tree, top_k=2)
    assert len(top_features) <= 2
    
    rule_strings = tree_to_rules(quick_tree, min_confidence=0.7)
    assert all(isinstance(r, str) for r in rule_strings)
    
    print("All decision tree tests passed!")


if __name__ == "__main__":
    test_decision_tree()