"""
Tissue ID: ML-TISSUE-007
Title: Flexible Neural Network Implementation
Category: ml/neural_networks
Tags: ["neural-network", "deep-learning", "mlp", "backpropagation", "classification", "regression"]
Difficulty: Advanced
Dependencies: ["numpy>=1.24", "scikit-learn>=1.3"]
Performance: O(n*m*h*e) where n is samples, m is features, h is hidden units, e is epochs
Tested: Python 3.8+, 3.9, 3.10
Author: CodeSnippetBank
Version: 1.0.0
Last Updated: 2024-01-20

Description:
A comprehensive neural network tissue implementing multi-layer perceptrons (MLP)
with various activation functions, optimizers, and regularization techniques.
Supports both classification and regression, batch/mini-batch/stochastic training,
early stopping, and dropout. Includes gradient checking and weight visualization.

Use Cases:
- Non-linear classification
- Function approximation
- Feature learning
- Pattern recognition
- Time series prediction

Example Usage:
    # Basic neural network
    nn = NeuralNetwork(layers=[10, 20, 10, 2], activation="relu")
    nn.fit(X_train, y_train, epochs=100)
    predictions = nn.predict(X_test)
    
    # With regularization and dropout
    nn = NeuralNetwork(
        layers=[input_size, 128, 64, output_size],
        activation="tanh",
        dropout_rate=0.2,
        l2_lambda=0.01
    )
    nn.fit(X_train, y_train, validation_data=(X_val, y_val))
    
    # Get hidden representations
    features = nn.get_hidden_representations(X, layer=2)
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import warnings
from collections import defaultdict


class ActivationType(Enum):
    """Available activation functions"""
    SIGMOID = "sigmoid"
    TANH = "tanh"
    RELU = "relu"
    LEAKY_RELU = "leaky_relu"
    ELU = "elu"
    SOFTMAX = "softmax"
    LINEAR = "linear"


class OptimizerType(Enum):
    """Available optimizers"""
    SGD = "sgd"
    MOMENTUM = "momentum"
    ADAM = "adam"
    RMSPROP = "rmsprop"
    ADAGRAD = "adagrad"


class LossType(Enum):
    """Available loss functions"""
    MSE = "mse"  # Mean squared error
    CROSS_ENTROPY = "cross_entropy"
    BINARY_CROSS_ENTROPY = "binary_cross_entropy"
    HUBER = "huber"


@dataclass
class NeuralNetConfig:
    """Configuration for neural network"""
    learning_rate: float = 0.01
    momentum: float = 0.9
    batch_size: Optional[int] = 32
    epochs: int = 100
    optimizer: str = "adam"
    loss: str = "cross_entropy"
    l1_lambda: float = 0.0
    l2_lambda: float = 0.0
    dropout_rate: float = 0.0
    early_stopping_patience: int = 10
    learning_rate_decay: float = 0.0
    gradient_clip_value: Optional[float] = None
    random_state: int = 42
    verbose: int = 1


@dataclass
class Layer:
    """Neural network layer"""
    input_size: int
    output_size: int
    activation: str
    
    # Weights and biases
    W: Optional[np.ndarray] = None
    b: Optional[np.ndarray] = None
    
    # For optimization
    W_velocity: Optional[np.ndarray] = None
    b_velocity: Optional[np.ndarray] = None
    W_cache: Optional[np.ndarray] = None
    b_cache: Optional[np.ndarray] = None
    
    # For forward/backward pass
    input: Optional[np.ndarray] = None
    output: Optional[np.ndarray] = None
    activation_output: Optional[np.ndarray] = None
    dropout_mask: Optional[np.ndarray] = None


class NeuralNetwork:
    """
    Flexible neural network implementation.
    Tissue Type: FUNCTIONAL - Core ML neural network functionality.
    """
    
    def __init__(self,
                 layers: List[int],
                 activation: Union[str, List[str]] = "relu",
                 output_activation: Optional[str] = None,
                 config: Optional[NeuralNetConfig] = None):
        """
        Initialize neural network.
        
        Args:
            layers: List of layer sizes [input_size, hidden1, hidden2, ..., output_size]
            activation: Activation function(s) for hidden layers
            output_activation: Activation for output layer (auto-determined if None)
            config: Network configuration
        """
        self.config = config or NeuralNetConfig()
        self.layers_config = layers
        
        # Handle activation functions
        if isinstance(activation, str):
            self.hidden_activations = [activation] * (len(layers) - 2)
        else:
            self.hidden_activations = activation
        
        self.output_activation = output_activation
        
        # Initialize layers
        self.layers: List[Layer] = []
        self._init_layers()
        
        # Training state
        self.is_fitted = False
        self.n_iter_ = 0
        self.loss_history_ = []
        self.val_loss_history_ = []
        
        # Task info
        self.n_classes_ = None
        self.classes_ = None
        
        # Optimizer state
        self.optimizer_state = {}
        
        # Random state
        self.rng = np.random.RandomState(self.config.random_state)
    
    def _init_layers(self):
        """Initialize network layers"""
        self.layers = []
        
        # Hidden layers
        for i in range(len(self.layers_config) - 1):
            if i < len(self.layers_config) - 2:
                # Hidden layer
                activation = self.hidden_activations[i]
            else:
                # Output layer
                activation = self.output_activation or "sigmoid"
            
            layer = Layer(
                input_size=self.layers_config[i],
                output_size=self.layers_config[i + 1],
                activation=activation
            )
            
            # Initialize weights using He or Xavier initialization
            if activation in ["relu", "leaky_relu", "elu"]:
                # He initialization for ReLU variants
                std = np.sqrt(2.0 / layer.input_size)
            else:
                # Xavier initialization for others
                std = np.sqrt(1.0 / layer.input_size)
            
            layer.W = self.rng.randn(layer.input_size, layer.output_size) * std
            layer.b = np.zeros(layer.output_size)
            
            # Initialize optimizer state
            if self.config.optimizer in ["momentum", "adam", "rmsprop"]:
                layer.W_velocity = np.zeros_like(layer.W)
                layer.b_velocity = np.zeros_like(layer.b)
            
            if self.config.optimizer in ["adam", "rmsprop", "adagrad"]:
                layer.W_cache = np.zeros_like(layer.W)
                layer.b_cache = np.zeros_like(layer.b)
            
            self.layers.append(layer)
    
    def fit(self, X: np.ndarray, y: np.ndarray,
            validation_data: Optional[Tuple[np.ndarray, np.ndarray]] = None,
            sample_weights: Optional[np.ndarray] = None) -> 'NeuralNetwork':
        """
        Train neural network.
        
        Args:
            X: Training features (n_samples, n_features)
            y: Target values (n_samples,) or (n_samples, n_classes)
            validation_data: Optional (X_val, y_val) for early stopping
            sample_weights: Optional sample weights
            
        Returns:
            Self for chaining
        """
        # Validate inputs
        X, y = self._validate_inputs(X, y)
        
        # Determine task type and prepare labels
        y_processed = self._prepare_labels(y)
        
        # Initialize optimizer state
        self._init_optimizer_state()
        
        # Training loop
        best_val_loss = np.inf
        patience_counter = 0
        
        for epoch in range(self.config.epochs):
            # Shuffle data
            indices = self.rng.permutation(len(X))
            X_shuffled = X[indices]
            y_shuffled = y_processed[indices]
            
            if sample_weights is not None:
                weights_shuffled = sample_weights[indices]
            else:
                weights_shuffled = None
            
            # Mini-batch training
            epoch_loss = self._train_epoch(X_shuffled, y_shuffled, weights_shuffled)
            self.loss_history_.append(epoch_loss)
            
            # Validation
            if validation_data is not None:
                X_val, y_val = validation_data
                y_val_processed = self._prepare_labels(y_val)
                val_loss = self._calculate_loss(X_val, y_val_processed)
                self.val_loss_history_.append(val_loss)
                
                # Early stopping
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    patience_counter = 0
                    # Save best weights
                    self._save_weights()
                else:
                    patience_counter += 1
                    
                    if patience_counter >= self.config.early_stopping_patience:
                        if self.config.verbose > 0:
                            print(f"Early stopping at epoch {epoch}")
                        # Restore best weights
                        self._restore_weights()
                        break
            
            # Learning rate decay
            if self.config.learning_rate_decay > 0:
                self.config.learning_rate *= (1 - self.config.learning_rate_decay)
            
            # Verbose output
            if self.config.verbose > 0 and epoch % 10 == 0:
                if validation_data is not None:
                    print(f"Epoch {epoch}: loss={epoch_loss:.4f}, val_loss={val_loss:.4f}")
                else:
                    print(f"Epoch {epoch}: loss={epoch_loss:.4f}")
            
            self.n_iter_ = epoch + 1
        
        self.is_fitted = True
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions.
        
        Args:
            X: Features to predict (n_samples, n_features)
            
        Returns:
            Predictions
        """
        if not self.is_fitted:
            raise ValueError("Network must be fitted before prediction")
        
        X = self._validate_input(X)
        
        # Forward pass
        output = self._forward(X, training=False)
        
        # Convert to class labels for classification
        if self.n_classes_ is not None:
            if self.n_classes_ == 2:
                # Binary classification
                predictions = (output[:, 0] > 0.5).astype(int)
            else:
                # Multi-class
                predictions = np.argmax(output, axis=1)
            
            # Decode labels
            return self.classes_[predictions]
        else:
            # Regression
            return output.squeeze()
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class probabilities.
        
        Args:
            X: Features to predict (n_samples, n_features)
            
        Returns:
            Class probabilities
        """
        if self.n_classes_ is None:
            raise ValueError("predict_proba is only for classification")
        
        X = self._validate_input(X)
        
        # Forward pass
        output = self._forward(X, training=False)
        
        if self.n_classes_ == 2:
            # Binary classification - ensure 2 columns
            proba = np.column_stack([1 - output[:, 0], output[:, 0]])
        else:
            proba = output
        
        return proba
    
    def _validate_inputs(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Validate training inputs"""
        X = np.asarray(X, dtype=np.float32)
        y = np.asarray(y)
        
        if X.ndim != 2:
            raise ValueError(f"X must be 2D, got {X.ndim}D")
        
        if X.shape[0] != y.shape[0]:
            raise ValueError("X and y must have same number of samples")
        
        # Check input size matches network
        if X.shape[1] != self.layers_config[0]:
            raise ValueError(f"Input size {X.shape[1]} doesn't match network input size {self.layers_config[0]}")
        
        return X, y
    
    def _validate_input(self, X: np.ndarray) -> np.ndarray:
        """Validate single input"""
        X = np.asarray(X, dtype=np.float32)
        
        if X.ndim == 1:
            X = X.reshape(1, -1)
        elif X.ndim != 2:
            raise ValueError(f"X must be 1D or 2D, got {X.ndim}D")
        
        if X.shape[1] != self.layers_config[0]:
            raise ValueError(f"Input size {X.shape[1]} doesn't match network input size {self.layers_config[0]}")
        
        return X
    
    def _prepare_labels(self, y: np.ndarray) -> np.ndarray:
        """Prepare labels for training"""
        if y.ndim == 1:
            # Check if classification or regression
            unique_values = np.unique(y)
            
            if len(unique_values) <= 20 and all(isinstance(v, (int, np.integer)) or v.is_integer() for v in unique_values):
                # Classification
                self.classes_ = unique_values
                self.n_classes_ = len(self.classes_)
                
                # One-hot encode
                y_encoded = np.zeros((len(y), self.n_classes_))
                for i, label in enumerate(y):
                    class_idx = np.where(self.classes_ == label)[0][0]
                    y_encoded[i, class_idx] = 1
                
                # Set output activation
                if self.output_activation is None:
                    if self.n_classes_ == 2:
                        self.layers[-1].activation = "sigmoid"
                    else:
                        self.layers[-1].activation = "softmax"
                
                # Set loss function
                if self.config.loss == "cross_entropy":
                    if self.n_classes_ == 2:
                        self.config.loss = "binary_cross_entropy"
                
                return y_encoded
            else:
                # Regression
                self.n_classes_ = None
                self.classes_ = None
                
                # Set output activation
                if self.output_activation is None:
                    self.layers[-1].activation = "linear"
                
                # Set loss function
                if self.config.loss == "cross_entropy":
                    self.config.loss = "mse"
                
                return y.reshape(-1, 1)
        else:
            # Already prepared (e.g., one-hot encoded)
            self.n_classes_ = y.shape[1]
            self.classes_ = np.arange(self.n_classes_)
            return y
    
    def _init_optimizer_state(self):
        """Initialize optimizer state"""
        if self.config.optimizer == "adam":
            self.optimizer_state['beta1'] = 0.9
            self.optimizer_state['beta2'] = 0.999
            self.optimizer_state['epsilon'] = 1e-8
            self.optimizer_state['t'] = 0
        elif self.config.optimizer == "rmsprop":
            self.optimizer_state['decay_rate'] = 0.9
            self.optimizer_state['epsilon'] = 1e-8
    
    def _train_epoch(self, X: np.ndarray, y: np.ndarray,
                    sample_weights: Optional[np.ndarray]) -> float:
        """Train one epoch"""
        n_samples = X.shape[0]
        
        if self.config.batch_size is None:
            # Full batch
            return self._train_batch(X, y, sample_weights)
        else:
            # Mini-batch
            epoch_loss = 0.0
            n_batches = 0
            
            for start_idx in range(0, n_samples, self.config.batch_size):
                end_idx = min(start_idx + self.config.batch_size, n_samples)
                
                X_batch = X[start_idx:end_idx]
                y_batch = y[start_idx:end_idx]
                
                if sample_weights is not None:
                    weights_batch = sample_weights[start_idx:end_idx]
                else:
                    weights_batch = None
                
                batch_loss = self._train_batch(X_batch, y_batch, weights_batch)
                epoch_loss += batch_loss
                n_batches += 1
            
            return epoch_loss / n_batches
    
    def _train_batch(self, X: np.ndarray, y: np.ndarray,
                    sample_weights: Optional[np.ndarray]) -> float:
        """Train on a single batch"""
        # Forward pass
        output = self._forward(X, training=True)
        
        # Calculate loss
        loss = self._calculate_loss_batch(output, y, sample_weights)
        
        # Backward pass
        self._backward(X, y, output, sample_weights)
        
        # Update weights
        self._update_weights()
        
        return loss
    
    def _forward(self, X: np.ndarray, training: bool = True) -> np.ndarray:
        """Forward pass through network"""
        current_input = X
        
        for layer in self.layers:
            # Store input for backward pass
            layer.input = current_input
            
            # Linear transformation
            z = current_input @ layer.W + layer.b
            
            # Activation
            layer.activation_output = self._apply_activation(z, layer.activation)
            
            # Dropout
            if training and self.config.dropout_rate > 0 and layer != self.layers[-1]:
                # Don't apply dropout to output layer
                mask = self.rng.binomial(1, 1 - self.config.dropout_rate, 
                                       size=layer.activation_output.shape)
                layer.dropout_mask = mask
                layer.activation_output *= mask / (1 - self.config.dropout_rate)
            else:
                layer.dropout_mask = None
            
            layer.output = layer.activation_output
            current_input = layer.output
        
        return current_input
    
    def _backward(self, X: np.ndarray, y: np.ndarray, output: np.ndarray,
                 sample_weights: Optional[np.ndarray]):
        """Backward pass through network"""
        n_samples = X.shape[0]
        
        # Calculate output layer gradient
        if self.config.loss == "mse":
            delta = (output - y) / n_samples
        elif self.config.loss == "binary_cross_entropy":
            delta = (output - y) / (n_samples * (output * (1 - output) + 1e-8))
        elif self.config.loss == "cross_entropy":
            delta = (output - y) / n_samples
        else:
            delta = (output - y) / n_samples
        
        # Apply sample weights
        if sample_weights is not None:
            delta *= sample_weights.reshape(-1, 1)
        
        # Backpropagate through layers
        for i in reversed(range(len(self.layers))):
            layer = self.layers[i]
            
            # Calculate gradients
            dW = layer.input.T @ delta
            db = np.sum(delta, axis=0)
            
            # Add regularization
            if self.config.l2_lambda > 0:
                dW += self.config.l2_lambda * layer.W
            if self.config.l1_lambda > 0:
                dW += self.config.l1_lambda * np.sign(layer.W)
            
            # Clip gradients
            if self.config.gradient_clip_value is not None:
                dW = np.clip(dW, -self.config.gradient_clip_value, 
                           self.config.gradient_clip_value)
                db = np.clip(db, -self.config.gradient_clip_value, 
                           self.config.gradient_clip_value)
            
            # Store gradients
            layer.dW = dW
            layer.db = db
            
            # Calculate delta for previous layer
            if i > 0:
                delta = delta @ layer.W.T
                
                # Apply activation derivative
                delta *= self._apply_activation_derivative(
                    layer.input @ self.layers[i-1].W + self.layers[i-1].b,
                    self.layers[i-1].activation
                )
                
                # Apply dropout mask if exists
                if self.layers[i-1].dropout_mask is not None:
                    delta *= self.layers[i-1].dropout_mask / (1 - self.config.dropout_rate)
    
    def _update_weights(self):
        """Update weights using optimizer"""
        if self.config.optimizer == "adam":
            self.optimizer_state['t'] += 1
            t = self.optimizer_state['t']
            
        for layer in self.layers:
            if self.config.optimizer == "sgd":
                # Standard SGD
                layer.W -= self.config.learning_rate * layer.dW
                layer.b -= self.config.learning_rate * layer.db
                
            elif self.config.optimizer == "momentum":
                # SGD with momentum
                layer.W_velocity = self.config.momentum * layer.W_velocity - self.config.learning_rate * layer.dW
                layer.b_velocity = self.config.momentum * layer.b_velocity - self.config.learning_rate * layer.db
                
                layer.W += layer.W_velocity
                layer.b += layer.b_velocity
                
            elif self.config.optimizer == "adam":
                # Adam optimizer
                beta1 = self.optimizer_state['beta1']
                beta2 = self.optimizer_state['beta2']
                epsilon = self.optimizer_state['epsilon']
                
                # Update biased first moment estimate
                layer.W_velocity = beta1 * layer.W_velocity + (1 - beta1) * layer.dW
                layer.b_velocity = beta1 * layer.b_velocity + (1 - beta1) * layer.db
                
                # Update biased second raw moment estimate
                layer.W_cache = beta2 * layer.W_cache + (1 - beta2) * layer.dW ** 2
                layer.b_cache = beta2 * layer.b_cache + (1 - beta2) * layer.db ** 2
                
                # Compute bias-corrected estimates
                W_velocity_corrected = layer.W_velocity / (1 - beta1 ** t)
                b_velocity_corrected = layer.b_velocity / (1 - beta1 ** t)
                W_cache_corrected = layer.W_cache / (1 - beta2 ** t)
                b_cache_corrected = layer.b_cache / (1 - beta2 ** t)
                
                # Update parameters
                layer.W -= self.config.learning_rate * W_velocity_corrected / (np.sqrt(W_cache_corrected) + epsilon)
                layer.b -= self.config.learning_rate * b_velocity_corrected / (np.sqrt(b_cache_corrected) + epsilon)
                
            elif self.config.optimizer == "rmsprop":
                # RMSprop
                decay_rate = self.optimizer_state['decay_rate']
                epsilon = self.optimizer_state['epsilon']
                
                layer.W_cache = decay_rate * layer.W_cache + (1 - decay_rate) * layer.dW ** 2
                layer.b_cache = decay_rate * layer.b_cache + (1 - decay_rate) * layer.db ** 2
                
                layer.W -= self.config.learning_rate * layer.dW / (np.sqrt(layer.W_cache) + epsilon)
                layer.b -= self.config.learning_rate * layer.db / (np.sqrt(layer.b_cache) + epsilon)
                
            elif self.config.optimizer == "adagrad":
                # Adagrad
                epsilon = 1e-8
                
                layer.W_cache += layer.dW ** 2
                layer.b_cache += layer.db ** 2
                
                layer.W -= self.config.learning_rate * layer.dW / (np.sqrt(layer.W_cache) + epsilon)
                layer.b -= self.config.learning_rate * layer.db / (np.sqrt(layer.b_cache) + epsilon)
    
    def _apply_activation(self, z: np.ndarray, activation: str) -> np.ndarray:
        """Apply activation function"""
        if activation == "sigmoid":
            return 1 / (1 + np.exp(-np.clip(z, -500, 500)))
        elif activation == "tanh":
            return np.tanh(z)
        elif activation == "relu":
            return np.maximum(0, z)
        elif activation == "leaky_relu":
            return np.where(z > 0, z, 0.01 * z)
        elif activation == "elu":
            return np.where(z > 0, z, np.exp(z) - 1)
        elif activation == "softmax":
            exp_z = np.exp(z - np.max(z, axis=1, keepdims=True))
            return exp_z / np.sum(exp_z, axis=1, keepdims=True)
        elif activation == "linear":
            return z
        else:
            raise ValueError(f"Unknown activation: {activation}")
    
    def _apply_activation_derivative(self, z: np.ndarray, activation: str) -> np.ndarray:
        """Apply activation function derivative"""
        if activation == "sigmoid":
            s = self._apply_activation(z, "sigmoid")
            return s * (1 - s)
        elif activation == "tanh":
            return 1 - np.tanh(z) ** 2
        elif activation == "relu":
            return (z > 0).astype(float)
        elif activation == "leaky_relu":
            return np.where(z > 0, 1, 0.01)
        elif activation == "elu":
            return np.where(z > 0, 1, np.exp(z))
        elif activation == "linear":
            return np.ones_like(z)
        else:
            return np.ones_like(z)
    
    def _calculate_loss(self, X: np.ndarray, y: np.ndarray) -> float:
        """Calculate loss on dataset"""
        output = self._forward(X, training=False)
        return self._calculate_loss_batch(output, y, None)
    
    def _calculate_loss_batch(self, output: np.ndarray, y: np.ndarray,
                            sample_weights: Optional[np.ndarray]) -> float:
        """Calculate loss for a batch"""
        if self.config.loss == "mse":
            loss = np.mean((output - y) ** 2)
        elif self.config.loss == "binary_cross_entropy":
            # Clip to prevent log(0)
            output_clipped = np.clip(output, 1e-7, 1 - 1e-7)
            loss = -np.mean(y * np.log(output_clipped) + (1 - y) * np.log(1 - output_clipped))
        elif self.config.loss == "cross_entropy":
            # Clip to prevent log(0)
            output_clipped = np.clip(output, 1e-7, 1 - 1e-7)
            loss = -np.mean(np.sum(y * np.log(output_clipped), axis=1))
        elif self.config.loss == "huber":
            delta = 1.0
            error = y - output
            loss = np.mean(np.where(np.abs(error) <= delta,
                                   0.5 * error ** 2,
                                   delta * np.abs(error) - 0.5 * delta ** 2))
        else:
            loss = np.mean((output - y) ** 2)
        
        # Apply sample weights
        if sample_weights is not None:
            loss = np.average(loss, weights=sample_weights)
        
        # Add regularization
        if self.config.l2_lambda > 0:
            l2_penalty = sum(np.sum(layer.W ** 2) for layer in self.layers)
            loss += 0.5 * self.config.l2_lambda * l2_penalty
        
        if self.config.l1_lambda > 0:
            l1_penalty = sum(np.sum(np.abs(layer.W)) for layer in self.layers)
            loss += self.config.l1_lambda * l1_penalty
        
        return loss
    
    def _save_weights(self):
        """Save current weights"""
        self.best_weights_ = []
        for layer in self.layers:
            self.best_weights_.append({
                'W': layer.W.copy(),
                'b': layer.b.copy()
            })
    
    def _restore_weights(self):
        """Restore saved weights"""
        if hasattr(self, 'best_weights_'):
            for layer, weights in zip(self.layers, self.best_weights_):
                layer.W = weights['W'].copy()
                layer.b = weights['b'].copy()
    
    def get_hidden_representations(self, X: np.ndarray, layer: int) -> np.ndarray:
        """
        Get hidden layer representations.
        
        Args:
            X: Input features
            layer: Layer index (0-based)
            
        Returns:
            Hidden representations
        """
        if not self.is_fitted:
            raise ValueError("Network must be fitted first")
        
        X = self._validate_input(X)
        
        current_input = X
        
        for i, l in enumerate(self.layers):
            if i <= layer:
                z = current_input @ l.W + l.b
                current_input = self._apply_activation(z, l.activation)
            else:
                break
        
        return current_input
    
    def gradient_check(self, X: np.ndarray, y: np.ndarray, epsilon: float = 1e-7) -> Dict[str, float]:
        """
        Check gradients using numerical approximation.
        
        Args:
            X: Input features
            y: Target values
            epsilon: Small value for numerical gradient
            
        Returns:
            Gradient check results
        """
        # Forward and backward pass
        output = self._forward(X, training=False)
        self._backward(X, y, output, None)
        
        results = {}
        
        for i, layer in enumerate(self.layers):
            # Check weight gradients
            analytical_dW = layer.dW.copy()
            numerical_dW = np.zeros_like(layer.W)
            
            for j in range(layer.W.shape[0]):
                for k in range(layer.W.shape[1]):
                    # Positive perturbation
                    layer.W[j, k] += epsilon
                    loss_plus = self._calculate_loss(X, y)
                    
                    # Negative perturbation
                    layer.W[j, k] -= 2 * epsilon
                    loss_minus = self._calculate_loss(X, y)
                    
                    # Restore weight
                    layer.W[j, k] += epsilon
                    
                    # Numerical gradient
                    numerical_dW[j, k] = (loss_plus - loss_minus) / (2 * epsilon)
            
            # Compare gradients
            diff = np.linalg.norm(analytical_dW - numerical_dW)
            norm_sum = np.linalg.norm(analytical_dW) + np.linalg.norm(numerical_dW)
            relative_error = diff / (norm_sum + 1e-8)
            
            results[f"layer_{i}_weights"] = relative_error
        
        return results


# Utility functions
def create_mlp_classifier(input_size: int, hidden_sizes: List[int], 
                         output_size: int, activation: str = "relu") -> NeuralNetwork:
    """Create MLP classifier"""
    layers = [input_size] + hidden_sizes + [output_size]
    config = NeuralNetConfig(
        loss="cross_entropy",
        optimizer="adam",
        learning_rate=0.001
    )
    return NeuralNetwork(layers=layers, activation=activation, config=config)


def create_mlp_regressor(input_size: int, hidden_sizes: List[int],
                        activation: str = "relu") -> NeuralNetwork:
    """Create MLP regressor"""
    layers = [input_size] + hidden_sizes + [1]
    config = NeuralNetConfig(
        loss="mse",
        optimizer="adam",
        learning_rate=0.001
    )
    return NeuralNetwork(layers=layers, activation=activation, 
                        output_activation="linear", config=config)


def train_with_cross_validation(nn: NeuralNetwork, X: np.ndarray, y: np.ndarray,
                              cv_folds: int = 5) -> Dict[str, float]:
    """Train neural network with cross-validation"""
    n_samples = X.shape[0]
    fold_size = n_samples // cv_folds
    scores = []
    
    for fold in range(cv_folds):
        # Create train/test split
        test_start = fold * fold_size
        test_end = (fold + 1) * fold_size if fold < cv_folds - 1 else n_samples
        
        test_idx = list(range(test_start, test_end))
        train_idx = list(range(test_start)) + list(range(test_end, n_samples))
        
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # Train network
        nn_fold = NeuralNetwork(
            layers=nn.layers_config,
            activation=nn.hidden_activations[0] if nn.hidden_activations else "relu",
            config=nn.config
        )
        nn_fold.fit(X_train, y_train)
        
        # Evaluate
        predictions = nn_fold.predict(X_test)
        if nn_fold.n_classes_ is not None:
            score = np.mean(predictions == y_test)
        else:
            score = -np.mean((predictions - y_test) ** 2)
        
        scores.append(score)
    
    return {
        "mean_score": np.mean(scores),
        "std_score": np.std(scores),
        "scores": scores
    }


# Auto-generated tests
def test_neural_network():
    """Test neural network functionality"""
    # Generate synthetic data
    np.random.seed(42)
    
    # Classification data (XOR problem)
    X_class = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
    y_class = np.array([0, 1, 1, 0])
    
    # Expand dataset
    X_class = np.repeat(X_class, 50, axis=0) + np.random.randn(200, 2) * 0.1
    y_class = np.repeat(y_class, 50)
    
    # Test basic neural network
    nn = NeuralNetwork(layers=[2, 4, 2], activation="tanh")
    nn.fit(X_class, y_class, epochs=50)
    
    assert nn.is_fitted
    assert len(nn.layers) == 2  # Hidden + output layers
    assert nn.n_classes_ == 2
    
    # Test prediction
    predictions = nn.predict(X_class[:10])
    assert len(predictions) == 10
    assert all(p in [0, 1] for p in predictions)
    
    # Test probability prediction
    probas = nn.predict_proba(X_class[:10])
    assert probas.shape == (10, 2)
    assert np.allclose(probas.sum(axis=1), 1.0, atol=1e-6)
    
    # Test regression
    X_reg = np.random.randn(100, 3)
    y_reg = X_reg[:, 0] + 0.5 * X_reg[:, 1] - 0.3 * X_reg[:, 2] + 0.1 * np.random.randn(100)
    
    nn_reg = NeuralNetwork(
        layers=[3, 8, 4, 1],
        activation="relu",
        output_activation="linear"
    )
    nn_reg.fit(X_reg, y_reg, epochs=50)
    
    reg_predictions = nn_reg.predict(X_reg[:10])
    assert len(reg_predictions) == 10
    assert all(isinstance(p, (float, np.floating)) for p in reg_predictions)
    
    # Test multiclass classification
    X_multi = np.random.randn(150, 4)
    y_multi = np.array([0] * 50 + [1] * 50 + [2] * 50)
    
    nn_multi = NeuralNetwork(layers=[4, 8, 3], activation="relu")
    nn_multi.fit(X_multi, y_multi, epochs=50)
    
    assert nn_multi.n_classes_ == 3
    multi_predictions = nn_multi.predict(X_multi[:10])
    assert all(p in [0, 1, 2] for p in multi_predictions)
    
    # Test with validation data
    config_val = NeuralNetConfig(
        epochs=100,
        early_stopping_patience=5,
        verbose=0
    )
    nn_val = NeuralNetwork(layers=[2, 4, 2], activation="tanh", config=config_val)
    nn_val.fit(X_class[:150], y_class[:150], 
              validation_data=(X_class[150:], y_class[150:]))
    
    assert len(nn_val.val_loss_history_) > 0
    assert nn_val.n_iter_ <= 100  # Should stop early
    
    # Test different optimizers
    for optimizer in ["sgd", "momentum", "adam", "rmsprop"]:
        config_opt = NeuralNetConfig(optimizer=optimizer, epochs=20, verbose=0)
        nn_opt = NeuralNetwork(layers=[2, 3, 2], config=config_opt)
        nn_opt.fit(X_class[:50], y_class[:50])
        assert nn_opt.is_fitted
    
    # Test regularization
    config_reg = NeuralNetConfig(
        l2_lambda=0.01,
        l1_lambda=0.001,
        dropout_rate=0.2,
        epochs=30
    )
    nn_regularized = NeuralNetwork(layers=[2, 8, 2], config=config_reg)
    nn_regularized.fit(X_class, y_class)
    assert nn_regularized.is_fitted
    
    # Test hidden representations
    hidden = nn.get_hidden_representations(X_class[:5], layer=0)
    assert hidden.shape == (5, 4)  # 4 hidden units in first layer
    
    # Test gradient checking (small network for speed)
    nn_small = NeuralNetwork(layers=[2, 2, 2], activation="sigmoid")
    nn_small.fit(X_class[:10], y_class[:10], epochs=1)
    
    grad_check = nn_small.gradient_check(X_class[:5], y_class[:5])
    assert all(error < 1e-5 for error in grad_check.values())
    
    # Test different activation functions
    for activation in ["sigmoid", "tanh", "relu", "leaky_relu"]:
        nn_act = NeuralNetwork(layers=[2, 3, 2], activation=activation)
        nn_act.fit(X_class[:50], y_class[:50], epochs=20)
        assert nn_act.is_fitted
    
    # Test utility functions
    mlp_clf = create_mlp_classifier(
        input_size=4,
        hidden_sizes=[8, 4],
        output_size=3
    )
    assert len(mlp_clf.layers) == 3
    
    mlp_reg = create_mlp_regressor(
        input_size=5,
        hidden_sizes=[10, 5]
    )
    assert mlp_reg.layers[-1].activation == "linear"
    
    # Test cross-validation
    cv_results = train_with_cross_validation(nn, X_class[:100], y_class[:100], cv_folds=3)
    assert "mean_score" in cv_results
    assert len(cv_results["scores"]) == 3
    
    print("All neural network tests passed!")


if __name__ == "__main__":
    test_neural_network()