import os
import json
import logging
from typing import List, Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

def is_ai_configured() -> bool:
    return bool(settings.GROQ_API_KEY and settings.GROQ_API_KEY.strip() and not settings.GROQ_API_KEY.startswith("your_"))

def get_groq_client():
    if not is_ai_configured():
        return None
    try:
        from groq import Groq
        return Groq(api_key=settings.GROQ_API_KEY)
    except Exception as e:
        logger.warning(f"Failed to initialize Groq client: {e}")
        return None

# --- Specialized Subject Knowledge Banks for Local Demo Fallback ---
SUBJECT_CURRICULA = {
    "machine learning": [
        {
            "title": "Introduction to Machine Learning & Fundamentals",
            "objectives": [
                "Understand the paradigm shift from traditional rule-based programming to data-driven learning",
                "Distinguish between Supervised, Unsupervised, and Reinforcement learning paradigms",
                "Analyze the end-to-end Machine Learning lifecycle from data ingestion to model deployment",
                "Identify common real-world use cases and ethical considerations in AI systems"
            ],
            "content": """# Chapter 1: Introduction to Machine Learning

## 1. Executive Summary & Paradigm Shift
Traditional computer programming relies on explicit instructions: humans write algorithms ($Rules$) that act upon $Data$ to produce $Answers$. In contrast, **Machine Learning (ML)** inverts this paradigm. We feed algorithms historical $Data$ and ground-truth $Answers$, allowing the system to deduce the underlying $Rules$ or patterns automatically.

$$\\text{Traditional: } \\text{Data} + \\text{Rules} \\longrightarrow \\text{Answers}$$
$$\\text{Machine Learning: } \\text{Data} + \\text{Answers} \\longrightarrow \\text{Rules}$$

## 2. Taxonomy of Machine Learning
Machine Learning algorithms are categorized based on the nature of the learning signal and supervision:

1. **Supervised Learning**: The training dataset contains input features ($X$) paired with target labels ($y$). The objective is to learn a mapping function $f: X \\to y$.
   - *Classification*: Discrete targets (e.g., spam vs. non-spam, disease diagnosis).
   - *Regression*: Continuous targets (e.g., housing price prediction, stock forecasting).
2. **Unsupervised Learning**: The dataset consists solely of unlabeled inputs ($X$). The system discovers latent structures, clusters, or probability distributions without external guidance.
   - *Clustering* (K-Means, DBSCAN)
   - *Dimensionality Reduction* (PCA, t-SNE)
3. **Reinforcement Learning (RL)**: An autonomous agent interacts with an environment, learning an optimal policy $\\pi(a|s)$ through trial, error, state rewards, and penalties.

## 3. The End-to-End Machine Learning Pipeline
1. **Problem Formulation**: Framing the business problem as an ML task.
2. **Data Acquisition & Exploration**: Gathering tabular, textual, or visual data and performing Exploratory Data Analysis (EDA).
3. **Data Preprocessing & Feature Engineering**: Handling missing values, categorical encoding (One-Hot, Target), feature scaling (MinMax, Standard Scaler), and feature selection.
4. **Model Selection & Training**: Choosing inductive hypotheses (e.g., Linear Models, Random Forests, XGBoost, Deep Neural Networks) and minimizing loss $\\mathcal{L}(\\theta)$.
5. **Evaluation & Validation**: Testing generalization on unseen test sets using K-Fold Cross-Validation.
6. **Deployment & Monitoring**: Serving via REST APIs and tracking data drift and concept drift over time.

## 4. Key Mathematical Formulations
In any parametric model with weights $W = [w_1, w_2, \\dots, w_d]^T$ and bias $b$:
$$\\hat{y} = W^T X + b$$
The optimization problem minimizes empirical risk:
$$\\min_{W, b} \\frac{1}{N} \\sum_{i=1}^N \\mathcal{L}(y_i, \\hat{y}_i)$$

## 5. Practical Python Implementation
```python
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# 1. Generate synthetic feature vectors (1000 samples, 4 features)
np.random.seed(42)
X = np.random.randn(1000, 4)
y = (X[:, 0] + 0.5 * X[:, 1] > 0).astype(int)

# 2. Split dataset with stratification
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Fit classifier
clf = LogisticRegression()
clf.fit(X_train, y_train)

# 4. Evaluate generalization accuracy
predictions = clf.predict(X_test)
print(f"Test Accuracy: {accuracy_score(y_test, predictions):.4f}")
```

## 6. Exam-Important Highlights & Tips
- **Key Takeaway**: A model is only as good as the data quality; garbage in equals garbage out.
- **Common Pitfall**: Data leakage, where test set information leaks into training during normalization or imputation.
- **Exam Question**: How does parametric ML differ from non-parametric ML? (Parametric has fixed parameter size, e.g., Linear Regression; non-parametric parameters grow with data size, e.g., KNN, Decision Trees).
""",
            "summary": "Covers the fundamental transition from deterministic programming to statistical learning, detailing supervised, unsupervised, and reinforcement paradigms alongside the full ML lifecycle."
        },
        {
            "title": "Supervised Learning: Regression & Classification",
            "objectives": [
                "Master Ordinary Least Squares (OLS) and Gradient Descent optimization for Linear Regression",
                "Formulate Logistic Regression, the Sigmoid activation, and Binary Cross-Entropy loss",
                "Compare margin-based classifiers (Support Vector Machines) with tree-based ensembles",
                "Evaluate multi-class classification using Confusion Matrices, Precision, Recall, and ROC-AUC"
            ],
            "content": """# Chapter 2: Supervised Learning Foundations

## 1. Linear Regression and the Cost Surface
Linear regression models the relationship between continuous dependent scalar $y$ and independent explanatory variables $X$.
The hypothesis function is:
$$\\hat{y} = \\theta_0 + \\theta_1 x_1 + \\dots + \\theta_d x_d = \\theta^T x$$
We formulate the Mean Squared Error (MSE) objective function:
$$J(\\theta) = \\frac{1}{2m} \\sum_{i=1}^m (\\hat{y}^{(i)} - y^{(i)})^2$$

To find parameters $\\theta$ that minimize $J(\\theta)$, we employ **Gradient Descent**:
$$\\theta_j := \\theta_j - \\alpha \\frac{\\partial}{\\partial \\theta_j} J(\\theta) = \\theta_j - \\frac{\\alpha}{m} \\sum_{i=1}^m (\\hat{y}^{(i)} - y^{(i)}) x_j^{(i)}$$
Where $\\alpha > 0$ is the learning rate hyperparameter.

## 2. Logistic Regression & Binary Cross-Entropy
For classification, predicting continuous numbers is ill-suited. We map raw logits $z = \\theta^T x$ into the interval $(0, 1)$ via the **Logistic Sigmoid function**:
$$\\sigma(z) = \\frac{1}{1 + e^{-z}}$$
Interpreting $\\hat{p} = \\sigma(z) = P(y=1|x)$, we maximize log-likelihood, leading to the **Binary Cross-Entropy (BCE) Loss**:
$$\\mathcal{L}_{BCE}(\\theta) = -\\frac{1}{m} \\sum_{i=1}^m \\left[ y^{(i)} \\ln(\\hat{p}^{(i)}) + (1 - y^{(i)}) \\ln(1 - \\hat{p}^{(i)}) \\right]$$

## 3. Decision Trees and Ensembles (Random Forest, Gradient Boosting)
Decision Trees recursively partition feature space by choosing splits that maximize **Information Gain** (minimizing Entropy or Gini Impurity):
$$\\text{Entropy}(S) = - \\sum_{k=1}^C p_k \\log_2(p_k)$$
$$\\text{Gini}(S) = 1 - \\sum_{k=1}^C p_k^2$$
- **Random Forest**: Bagging (Bootstrap Aggregating) + random feature subspacing to reduce variance.
- **Gradient Boosting (XGBoost/LightGBM)**: Sequential boosting where each tree fits the negative gradient residuals of previous trees.

## 4. Comprehensive Evaluation Metrics
Accuracy alone is misleading on imbalanced datasets. We define:
- **Precision**: $\\frac{TP}{TP + FP}$ (Fraction of positive predictions that were correct)
- **Recall (Sensitivity)**: $\\frac{TP}{TP + FN}$ (Fraction of actual positives captured)
- **F1-Score**: Harmonic mean: $2 \\cdot \\frac{\\text{Precision} \\cdot \\text{Recall}}{\\text{Precision} + \\text{Recall}}$
- **ROC-AUC**: Area under the True Positive Rate vs False Positive Rate curve across all classification thresholds.

## 5. Practical Scikit-Learn Code
```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

# Train an ensemble of 100 decision trees
rf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("\\nClassification Report:")
print(classification_report(y_test, y_pred))
```

## 6. Exam-Important Takeaways
- Always inspect the cost function convexity: Linear & Logistic regression have convex loss functions (guaranteed global minimum under gradient descent).
- When false negatives are critical (e.g., cancer detection), optimize for **Recall**.
- When false positives are disastrous (e.g., fraud blockings), prioritize **Precision**.
""",
            "summary": "Deep dive into regression and classification mathematics, gradient descent derivation, tree ensembles, and robust model evaluation metrics."
        },
        {
            "title": "Unsupervised Learning: Clustering & Dimensionality Reduction",
            "objectives": [
                "Understand the mechanics and convergence guarantees of K-Means clustering",
                "Perform density-based spatial clustering (DBSCAN) for non-spherical clusters",
                "Derive Principal Component Analysis (PCA) using covariance matrices and eigendecomposition",
                "Apply dimensionality reduction for high-dimensional data compression and visualization"
            ],
            "content": """# Chapter 3: Unsupervised Learning & Feature Projection

## 1. The Core Objective of Unsupervised Learning
Without ground-truth annotations $y$, the algorithm must extract latent geometry, density variations, or intrinsic coordinate frames from $X \\in \\mathbb{R}^{N \\times D}$.

## 2. K-Means Clustering Algorithm
Given target cluster count $K$, K-Means minimizes the Within-Cluster Sum of Squares (WCSS), also called inertia:
$$J = \\sum_{k=1}^K \\sum_{x_i \\in S_k} \\| x_i - \\mu_k \\|^2$$
**Algorithm Iterations**:
1. *Initialization*: Pick $K$ initial centroids $\\mu_1, \\dots, \\mu_K$ (preferably via K-Means++).
2. *Assignment step*: Assign each sample $x_i$ to the nearest centroid:
   $$c_i = \\arg\\min_k \\| x_i - \\mu_k \\|^2$$
3. *Update step*: Recompute cluster centroids as the arithmetic mean of assigned points:
   $$\\mu_k = \\frac{1}{|S_k|} \\sum_{x_i \\in S_k} x_i$$
4. Repeat until convergence.

## 3. Density-Based Clustering: DBSCAN
Unlike K-Means, which assumes convex, spherical clusters and requires specifying $K$, **DBSCAN** groups points based on density connectivity:
- Core points: At least `min_samples` within distance $\\epsilon$.
- Border points: Within $\\epsilon$ of a core point but fewer than `min_samples`.
- Noise: Points that are neither core nor border (handles outliers automatically).

## 4. Principal Component Analysis (PCA)
High-dimensional datasets suffer from the *Curse of Dimensionality*. PCA finds an orthogonal coordinate system where components maximize sample variance.
1. Center data: $\\tilde{X} = X - \\bar{X}$
2. Compute sample covariance matrix:
   $$\\Sigma = \\frac{1}{N-1} \\tilde{X}^T \\tilde{X}$$
3. Perform eigendecomposition:
   $$\\Sigma v_j = \\lambda_j v_j$$
   Where eigenvalues $\\lambda_1 \\ge \\lambda_2 \\ge \\dots \\ge \\lambda_D$ quantify the variance explained along eigenvectors $v_j$.
4. Project data onto the top $k$ principal eigenvectors: $Z = \\tilde{X} V_k$.

## 5. Python Example
```python
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

# Reduce 20 features down to 2 principal components
pca = PCA(n_components=2)
X_reduced = pca.fit_transform(X)
print(f"Explained Variance Ratio: {pca.explained_variance_ratio_.sum():.2%}")

# Cluster in the lower-dimensional latent space
kmeans = KMeans(n_clusters=3, init='k-means++', random_state=42)
labels = kmeans.fit_predict(X_reduced)
```

## 6. Exam-Important Concepts
- **Elbow Method & Silhouette Analysis**: Techniques used to determine optimal $K$ in K-Means.
- **PCA is sensitive to feature scale**: Always standardize features with `StandardScaler` before performing PCA.
""",
            "summary": "Explores unsupervised discovery of geometric clusters with K-Means and DBSCAN, alongside spectral projection via Principal Component Analysis."
        },
        {
            "title": "Model Evaluation, Cross-Validation & Diagnostics",
            "objectives": [
                "Design leak-free evaluation schemes using K-Fold and Stratified Cross-Validation",
                "Diagnose model health through Learning Curves and Validation Curves",
                "Apply Hyperparameter Tuning strategies: Grid Search, Random Search, and Bayesian Optimization",
                "Implement calibration curves and Brier scores for probability reliability"
            ],
            "content": """# Chapter 4: Model Evaluation and Experimental Rigor

## 1. The Generalization Principle
The ultimate test of any machine learning model is its generalization capability on independent, identically distributed ($i.i.d.$) unseen data. Splitting a dataset arbitrarily into training and testing sets is susceptible to statistical variance and data leakage.

## 2. Cross-Validation Paradigms
- **Hold-out Method**: Simple 70/15/15 train/val/test split. Fast, but vulnerable on small datasets.
- **K-Fold Cross-Validation**: Divides dataset into $K$ disjoint partitions. Trains on $K-1$ folds and tests on the remaining fold, rotating $K$ times. The overall performance is the sample average:
  $$\\text{CV}_K = \\frac{1}{K} \\sum_{k=1}^K \\text{Metric}_k$$
- **Stratified K-Fold**: Preserves the exact class proportion across every fold. Critical for imbalanced datasets.
- **Time-Series Split**: Forward-chaining split that prevents temporal lookahead bias.

## 3. Learning Curves Diagnostic Framework
Plotting training score vs validation score as sample size $N$ increases diagnoses capacity issues:
- **High Bias (Underfitting)**: Both training and validation errors plateau at an unacceptably high error rate. Adding more data will not help; a more expressive model or richer features are required.
- **High Variance (Overfitting)**: Training error is near zero, but validation error remains significantly higher. Adding training samples or applying regularization narrows the generalization gap.

## 4. Hyperparameter Optimization
$$\\theta^* = \\arg\\min_{\\theta \\in \\Theta} \\text{CV}(\\mathcal{M}_\\theta)$$
1. **Grid Search**: Exhaustive evaluation over a discrete Cartesian product grid. Computationally expensive ($O(S^P)$).
2. **Randomized Search**: Samples candidate configurations randomly from probability distributions. Much faster and empirically effective.
3. **Bayesian Optimization**: Fits a Gaussian Process surrogate model to map hyperparameter spaces to expected performance improvements.

## 5. Python Pipeline Implementation
```python
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# Leak-free pipeline encapsulating normalization and classification
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('svc', SVC(kernel='rbf'))
])

param_grid = {
    'svc__C': [0.1, 1.0, 10.0],
    'svc__gamma': ['scale', 'auto', 0.01]
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
grid = GridSearchCV(pipe, param_grid, cv=cv, scoring='roc_auc', n_jobs=-1)
grid.fit(X_train, y_train)

print(f"Optimal Hyperparameters: {grid.best_params_}")
print(f"Best Stratified ROC-AUC: {grid.best_score_:.4f}")
```

## 6. Exam-Important Concepts
- **Data Leakage in Preprocessing**: Performing feature scaling or imputation on the entire dataset prior to splitting leaks validation statistics into the model. Always execute transformations inside an estimator pipeline!
""",
            "summary": "Covers rigorous experimental methodology, stratified cross-validation, leak-free pipeline engineering, and hyperparameter optimization."
        },
        {
            "title": "Overfitting, Underfitting & Advanced Regularization",
            "objectives": [
                "Deconstruct Generalization Error into Bias, Variance, and Irreducible Noise",
                "Formulate L1 Lasso (sparsity) and L2 Ridge (weight decay) penalties",
                "Understand ElasticNet compromise and modern deep learning regularization (Dropout, Early Stopping)",
                "Apply actionable remediation strategies when overfitting or underfitting occurs in production"
            ],
            "content": """# Chapter 5: Bias-Variance Tradeoff & Regularization

## 1. Bias-Variance Decomposition
For any target $y = f(x) + \\epsilon$ with irreducible error $\\epsilon \\sim \\mathcal{N}(0, \\sigma^2)$, the expected Mean Squared Error of estimator $\\hat{f}(x)$ decomposes mathematically:
$$\\mathbb{E}\\left[ (y - \\hat{f}(x))^2 \\right] = \\text{Bias}[\\hat{f}(x)]^2 + \\text{Var}[\\hat{f}(x)] + \\sigma^2$$
- **Bias**: Error introduced by approximating a complex physical reality with a simplified algorithm. (Underfitting)
- **Variance**: Error stemming from sensitivity to small fluctuations in the training dataset. (Overfitting)
- **$\\sigma^2$**: Inherent irreducible noise within the problem formulation or measurements.

## 2. Regularization Formulations
To combat high variance, we penalize large parameter magnitudes by augmenting the empirical loss function:
$$\\mathcal{L}_{reg}(\\theta) = \\mathcal{L}_{data}(\\theta) + \\lambda \\cdot \\Omega(\\theta)$$
Where $\\lambda \\ge 0$ balances empirical fit against model simplicity.

### Ridge Regression (L2 Penalty)
$$\\Omega_{L2}(\\theta) = \\frac{1}{2} \\sum_{j=1}^d \\theta_j^2 = \\frac{1}{2} \\| \\theta \\|_2^2$$
- Shrinks weights smoothly towards zero.
- Admits a closed-form analytical solution: $\\theta_{Ridge} = (X^T X + \\lambda I)^{-1} X^T y$.
- Retains all features; mitigates multicollinearity.

### Lasso Regression (L1 Penalty)
$$\\Omega_{L1}(\\theta) = \\sum_{j=1}^d |\\theta_j| = \\| \\theta \\|_1$$
- Possesses sharp diamond-shaped contour constraints at axes intersections.
- Forces non-informative coefficients strictly to **zero**, acting as automatic feature selection.

### ElasticNet
Combines both penalties via a mixing ratio $\\rho$:
$$\\Omega_{EN}(\\theta) = \\lambda \\left[ \\rho \\| \\theta \\|_1 + \\frac{1 - \\rho}{2} \\| \\theta \\|_2^2 \\right]$$

## 3. Comparison Matrix
| Technique | Penalty Formula | Effect on Weights | Feature Selection? | Best Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **Ridge (L2)** | $\\sum \\theta_j^2$ | Shrinks uniformly | No | Multicollinear features |
| **Lasso (L1)** | $\\sum |\\theta_j|$ | Drives weights to 0 | **Yes (Sparse)** | High-dimensional sparse data |
| **ElasticNet** | $\\alpha L1 + (1-\\alpha) L2$ | Group sparsity | **Yes** | Correlated feature groups |

## 4. Modern Regularization in Deep Learning
- **Dropout**: Inverted dropout randomly zeroes neuron activations with probability $p$ during forward propagation, preventing complex co-adaptations.
- **Early Stopping**: Halts gradient updates when validation error ceases to improve for $k$ consecutive epochs.
- **Data Augmentation**: Artificially inflates dataset size via domain-specific transformations (flips, rotations, jitter).

## 5. Practical Python Demonstration
```python
from sklearn.linear_model import Ridge, Lasso, ElasticNet

# Regularized linear models
ridge = Ridge(alpha=1.0)
lasso = Lasso(alpha=0.1)
elastic = ElasticNet(alpha=0.5, l1_ratio=0.5)

ridge.fit(X_train, y_train)
lasso.fit(X_train, y_train)
elastic.fit(X_train, y_train)

print(f"Lasso Zeroed-out Features: {np.sum(lasso.coef_ == 0)} of {X_train.shape[1]}")
```

## 6. Exam-Important Concepts & Review Checklist
- Why does Lasso produce exact zeros while Ridge does not? The $L1$ norm geometry has sharp corners that intersect the error elliptical contours on the coordinate axes.
- Increasing $\\lambda$ increases Bias and decreases Variance.
- Decreasing $\\lambda$ decreases Bias and increases Variance.
""",
            "summary": "Exhaustive treatment of the bias-variance tradeoff, mathematical derivation of L1 Lasso and L2 Ridge regularizations, and concrete anti-overfitting strategies."
        }
    ]
}

# --- Questions Bank for Local Demo ---
MACHINE_LEARNING_QUESTIONS = [
    # Section 1
    [
        {
            "question_text": "In the fundamental paradigm shift of Machine Learning, what are the primary inputs provided to the algorithm to generate predictive rules?",
            "question_type": "multiple_choice",
            "options": [
                "Data and Answers (Ground Truth)",
                "Handcrafted Rules and Logic Constraints",
                "Database Schemas and Static Compilers",
                "Raw Random Vectors and Unit Tests"
            ],
            "correct_answer": "Data and Answers (Ground Truth)",
            "explanation": "Unlike traditional software engineering where rules and data produce answers, machine learning takes input data and answers to deduce the underlying rules.",
            "associated_concept": "ML Fundamentals"
        },
        {
            "question_text": "True or False: In Unsupervised Learning, algorithms require labeled ground-truth targets ($y$) to identify clusters and hidden geometric patterns.",
            "question_type": "true_false",
            "options": ["True", "False"],
            "correct_answer": "False",
            "explanation": "Unsupervised learning operates strictly on unlabeled input features ($X$) without external ground-truth supervision.",
            "associated_concept": "Unsupervised Learning Taxonomy"
        },
        {
            "question_text": "What type of machine learning problem seeks to predict a continuous numeric quantity (such as housing price or temperature)?",
            "question_type": "multiple_choice",
            "options": ["Regression", "Binary Classification", "Association Rule Mining", "Dimensionality Reduction"],
            "correct_answer": "Regression",
            "explanation": "Regression models predict continuous numeric values, whereas classification models predict discrete categorical labels.",
            "associated_concept": "Supervised Learning Taxonomy"
        },
        {
            "question_text": "Fill in the blank: The phenomenon where information from the test dataset inadvertently leaks into the training pipeline during preprocessing is known as Data ________.",
            "question_type": "fill_blank",
            "options": [],
            "correct_answer": "Leakage",
            "explanation": "Data Leakage occurs when test or future information contaminates the model training process, leading to unrealistically optimistic validation metrics.",
            "associated_concept": "Data Preprocessing & Validation"
        },
        {
            "question_text": "Briefly describe the key difference between parametric and non-parametric machine learning models.",
            "question_type": "short_answer",
            "options": [],
            "correct_answer": "Parametric models have a fixed number of parameters regardless of dataset size (e.g., Linear Regression), whereas non-parametric model complexity grows with data size (e.g., KNN, Decision Trees).",
            "explanation": "Parametric models summarize data through fixed parameters; non-parametric models make fewer structural assumptions and scale their parameters with sample volume.",
            "associated_concept": "Model Parametrization"
        }
    ],
    # Section 2
    [
        {
            "question_text": "Which activation function is utilized in Logistic Regression to map arbitrary real-valued logits into calibrated probabilities within the range (0, 1)?",
            "question_type": "multiple_choice",
            "options": [
                "Logistic Sigmoid Function",
                "Rectified Linear Unit (ReLU)",
                "Hyperbolic Tangent (Tanh)",
                "Leaky ReLU with alpha 0.01"
            ],
            "correct_answer": "Logistic Sigmoid Function",
            "explanation": "The sigmoid function sigma(z) = 1 / (1 + e^-z) smoothly compresses (-inf, +inf) into the probability interval (0, 1).",
            "associated_concept": "Logistic Regression"
        },
        {
            "question_text": "When diagnosing an extreme medical screening model where failing to detect an illness has fatal consequences, which evaluation metric must be prioritized?",
            "question_type": "multiple_choice",
            "options": ["Recall (Sensitivity)", "Precision", "Accuracy", "Specificity"],
            "correct_answer": "Recall (Sensitivity)",
            "explanation": "Recall measures the fraction of actual positive cases detected. High recall minimizes catastrophic False Negatives.",
            "associated_concept": "Evaluation Metrics"
        },
        {
            "question_text": "True or False: Random Forest utilizes Bagging (Bootstrap Aggregation) alongside random feature subsampling to decrease model variance.",
            "question_type": "true_false",
            "options": ["True", "False"],
            "correct_answer": "True",
            "explanation": "Random Forest builds decorrelated decision trees on bootstrap resamples and averages predictions to suppress overall variance.",
            "associated_concept": "Ensemble Methods"
        },
        {
            "question_text": "What is the harmonic mean of Precision and Recall called?",
            "question_type": "multiple_choice",
            "options": ["F1-Score", "ROC-AUC", "Mean Squared Error", "Gini Impurity"],
            "correct_answer": "F1-Score",
            "explanation": "The F1-score provides a balanced harmonic mean between precision and recall, especially valuable on skewed class distributions.",
            "associated_concept": "Evaluation Metrics"
        },
        {
            "question_text": "Explain how Gradient Boosting differs from Random Forest in tree construction.",
            "question_type": "short_answer",
            "options": [],
            "correct_answer": "Random Forest builds independent trees in parallel using bagging, whereas Gradient Boosting builds trees sequentially, with each new tree fitting the residual errors of the previous ensemble.",
            "explanation": "Boosting is additive and sequential, correcting previous mistakes; Bagging is parallel and averages independent high-variance estimators.",
            "associated_concept": "Ensemble Methods"
        }
    ],
    # Section 3
    [
        {
            "question_text": "Which objective does the K-Means clustering algorithm iteratively minimize during its execution?",
            "question_type": "multiple_choice",
            "options": [
                "Within-Cluster Sum of Squares (Inertia)",
                "Between-Cluster Covariance Determinant",
                "Cross-Entropy of Centroid Probabilities",
                "Kullback-Leibler Divergence"
            ],
            "correct_answer": "Within-Cluster Sum of Squares (Inertia)",
            "explanation": "K-Means minimizes the sum of squared Euclidean distances from each data point to its assigned centroid.",
            "associated_concept": "K-Means Clustering"
        },
        {
            "question_text": "True or False: Unlike K-Means, the DBSCAN algorithm can identify arbitrarily shaped non-spherical clusters and automatically labels outliers as noise.",
            "question_type": "true_false",
            "options": ["True", "False"],
            "correct_answer": "True",
            "explanation": "DBSCAN clusters based on local sample density within radius epsilon and isolates low-density noise points.",
            "associated_concept": "Density-Based Clustering"
        },
        {
            "question_text": "In Principal Component Analysis (PCA), along which directions in feature space do the principal components point?",
            "question_type": "multiple_choice",
            "options": [
                "Directions of maximum sample variance",
                "Directions minimizing geometric entropy",
                "Random orthogonal hyperplanes",
                "Lines connecting nearest centroid pairs"
            ],
            "correct_answer": "Directions of maximum sample variance",
            "explanation": "Principal components are the eigenvectors of the covariance matrix, ordered descendingly by explained variance (eigenvalues).",
            "associated_concept": "PCA Dimensionality Reduction"
        },
        {
            "question_text": "Why must continuous features always be standardized (e.g. zero mean, unit variance) prior to computing Principal Component Analysis?",
            "question_type": "short_answer",
            "options": [],
            "correct_answer": "Because PCA is sensitive to variance magnitude, features with larger measurement scales will artificially dominate the principal eigenvectors regardless of true informativeness.",
            "explanation": "Scaling prevents high-magnitude features from skewing the covariance matrix and dominating the projection axes.",
            "associated_concept": "PCA Standardization"
        }
    ],
    # Section 4
    [
        {
            "question_text": "Which cross-validation scheme should be selected when evaluating a machine learning classifier on an imbalanced dataset?",
            "question_type": "multiple_choice",
            "options": [
                "Stratified K-Fold Cross-Validation",
                "Standard Random Split without Folds",
                "Leave-One-Out Cross-Validation",
                "Reverse Temporal Validation"
            ],
            "correct_answer": "Stratified K-Fold Cross-Validation",
            "explanation": "Stratified K-Fold maintains the exact class proportion within each fold, preventing any fold from lacking minority class instances.",
            "associated_concept": "Cross-Validation"
        },
        {
            "question_text": "On a diagnostic learning curve plot, what issue is indicated when both training error and validation error plateau at an unacceptably high error rate?",
            "question_type": "multiple_choice",
            "options": [
                "High Bias (Underfitting)",
                "High Variance (Overfitting)",
                "Catastrophic Data Leakage",
                "Optimal Bayes Error Convergence"
            ],
            "correct_answer": "High Bias (Underfitting)",
            "explanation": "When both curves converge to high error, the model lacks representational capacity to capture the underlying pattern.",
            "associated_concept": "Learning Curve Diagnostics"
        },
        {
            "question_text": "True or False: Executing feature normalization and imputation on the entire dataset before creating training/validation splits causes data leakage.",
            "question_type": "true_false",
            "options": ["True", "False"],
            "correct_answer": "True",
            "explanation": "Computing scaling statistics across the whole dataset leaks validation distribution parameters into the training phase.",
            "associated_concept": "Data Leakage"
        },
        {
            "question_text": "What is the primary operational advantage of Randomized Search over exhaustive Grid Search during hyperparameter optimization?",
            "question_type": "short_answer",
            "options": [],
            "correct_answer": "Randomized Search evaluates a fixed budget of random combinations rather than all possibilities, discovering near-optimal parameters dramatically faster in high-dimensional spaces.",
            "explanation": "Randomized search explores the parameter landscape without wasting computations on uninformative hyperparameter dimensions.",
            "associated_concept": "Hyperparameter Optimization"
        }
    ],
    # Section 5
    [
        {
            "question_text": "According to the Bias-Variance decomposition, what are the three mathematical constituents of expected generalization error?",
            "question_type": "multiple_choice",
            "options": [
                "Bias Squared, Variance, and Irreducible Noise",
                "Accuracy, Precision, and Recall",
                "Gradient Residuals, Learning Rate, and Batch Size",
                "Entropy, Gini Impurity, and Information Gain"
            ],
            "correct_answer": "Bias Squared, Variance, and Irreducible Noise",
            "explanation": "Expected MSE = Bias^2 + Variance + sigma^2 (irreducible measurement noise).",
            "associated_concept": "Bias-Variance Decomposition"
        },
        {
            "question_text": "Which regularization technique adds the absolute sum of parameters (L1 norm) to the loss function, inducing parameter sparsity and feature selection?",
            "question_type": "multiple_choice",
            "options": [
                "Lasso Regression (L1 Regularization)",
                "Ridge Regression (L2 Regularization)",
                "Batch Normalization",
                "Inverted Dropout"
            ],
            "correct_answer": "Lasso Regression (L1 Regularization)",
            "explanation": "Lasso penalizes the sum of absolute values, driving non-informative feature weights strictly to zero.",
            "associated_concept": "L1 Lasso Regularization"
        },
        {
            "question_text": "True or False: Increasing the regularization hyperparameter lambda increases model variance while reducing model bias.",
            "question_type": "true_false",
            "options": ["True", "False"],
            "correct_answer": "False",
            "explanation": "Increasing lambda penalizes complex weights more heavily, which reduces variance but increases bias (simpler model).",
            "associated_concept": "Regularization Hyperparameters"
        },
        {
            "question_text": "Why does Lasso (L1) produce exact zero weights while Ridge (L2) only shrinks weights toward zero without setting them to zero?",
            "question_type": "short_answer",
            "options": [],
            "correct_answer": "The L1 norm constraint has sharp corners (vertices) on the coordinate axes where the elliptical loss contours frequently intersect first, setting coordinates to exactly zero.",
            "explanation": "L1 norm has diamond contours with non-differentiable vertices on axes, favoring corner solutions; L2 has smooth spherical contours that shrink parameters without setting them to zero.",
            "associated_concept": "L1 vs L2 Geometric Intuition"
        }
    ]
]


# --- Core Generator Functions ---

def generate_course_content(
    title: str,
    subject: str,
    description: str = "",
    prompt: str = "",
    difficulty: str = "Beginner",
    section_count: int = 5
) -> List[Dict[str, Any]]:
    """
    Generates structured course sections.
    If Groq is configured, uses Groq LLM.
    Otherwise, generates rich, deterministic subject-aware course content.
    """
    groq_client = get_groq_client()
    
    if groq_client:
        try:
            system_prompt = (
                "You are an elite university professor and educational curriculum designer. "
                "Generate a detailed, rigorous college-level syllabus and section content. "
                "Output ONLY valid JSON matching this schema: "
                "{\"sections\": [{\"title\": str, \"objectives\": [str], \"content\": str (detailed markdown with formulas, code, concepts, exam tips), \"summary\": str}]}"
            )
            user_msg = (
                f"Course Title: {title}\n"
                f"Subject / Domain: {subject}\n"
                f"Description: {description}\n"
                f"Teacher Guidance / Prompt: {prompt}\n"
                f"Target Difficulty: {difficulty}\n"
                f"Number of Sections: {section_count}\n\n"
                "Ensure each section has rich, exhaustive educational markdown content, concrete formulas, practical code or worked examples, definitions, and exam notes."
            )
            
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ],
                model=settings.GROQ_MODEL,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            response_text = chat_completion.choices[0].message.content
            parsed = json.loads(response_text)
            if "sections" in parsed and len(parsed["sections"]) > 0:
                logger.info(f"Successfully generated {len(parsed['sections'])} sections via Groq API.")
                return parsed["sections"][:section_count]
        except Exception as e:
            logger.warning(f"Groq API course generation failed, falling back to local engine: {e}")

    # --- Local Subject-Aware Demo Fallback ---
    norm_subject = subject.lower().strip()
    norm_title = title.lower().strip()
    
    if "machine learning" in norm_subject or "machine learning" in norm_title or "ml" in norm_subject or "ai" in norm_subject or "data science" in norm_subject:
        base_sections = SUBJECT_CURRICULA["machine learning"]
        sections = []
        for i in range(min(section_count, len(base_sections))):
            sections.append(base_sections[i])
        
        # If user asked for more sections than pre-seeded, dynamically create additional in-depth sections
        extra_topics = [
            ("Deep Learning & Neural Network Architectures", ["Feedforward networks", "Backpropagation calculus", "Activation functions", "Convolutional layers"]),
            ("Natural Language Processing & Transformer Models", ["Tokenization", "Self-attention mechanism", "BERT vs GPT", "Fine-tuning"]),
            ("Reinforcement Learning & Markov Decision Processes", ["Bellman equation", "Q-learning", "Policy gradients", "Exploration vs exploitation"]),
            ("MLOps: Model Deployment, Monitoring & Drift Detection", ["Containerization", "REST inference", "Concept drift", "Feature stores"]),
            ("Ethical AI, Fairness & Model Interpretability", ["SHAP and LIME", "Algorithmic bias", "Fairness metrics", "Differential privacy"])
        ]
        curr_idx = 0
        while len(sections) < section_count and curr_idx < len(extra_topics):
            topic_name, topic_objs = extra_topics[curr_idx]
            sections.append({
                "title": topic_name,
                "objectives": [f"Understand {o.lower()}" for o in topic_objs],
                "content": f"""# {topic_name}

## 1. Introduction and Architectural Foundations
In this section, we study the theoretical and practical underpinnings of **{topic_name}**. We inspect how modern algorithms tackle high-dimensional real-world challenges with rigorous mathematical guarantees.

## 2. Core Methodologies and Mathematical Formulations
Key concepts explored in this domain:
- **Foundational Principles**: Systematic formulation of state representations and transition dynamics.
- **Optimization Strategy**: Minimizing empirical risk with tailored regularizers:
$$\\mathcal{{L}}(\\theta) = \\mathbb{{E}}_{{x \\sim \\mathcal{{D}}}} [ \\ell(f_\\theta(x), y) ] + \\lambda \\Omega(\\theta)$$

## 3. Practical Code Example
```python
# Practical implementation snippet for {topic_name}
import numpy as np

def run_simulation(inputs):
    print("Executing computational pipeline for {topic_name}...")
    weights = np.ones((inputs.shape[1], 1))
    return np.dot(inputs, weights)

data = np.random.randn(10, 4)
output = run_simulation(data)
print("Pipeline verified successfully.")
```

## 4. Exam-Important Concepts & Review
- Pay careful attention to hyperparameter sensitivity and computational complexity.
- Be prepared to discuss trade-offs between sample efficiency and computational throughput.
""",
                "summary": f"In-depth analysis of {topic_name}, covering theoretical formulation, architecture, and deployment trade-offs."
            })
            curr_idx += 1
        return sections[:section_count]

    # Generic Subject Fallback: generate rich topic-tailored modules
    sections = []
    for i in range(1, section_count + 1):
        sections.append({
            "title": f"Module {i}: Advanced Principles of {title} (Part {i})",
            "objectives": [
                f"Master key theoretical models in {subject} - Topic {i}",
                f"Analyze practical architectures and methodologies for {title}",
                f"Execute hands-on computational or analytical procedures",
                f"Identify common pitfalls and design patterns in {subject}"
            ],
            "content": f"""# Module {i}: Advanced Principles of {title}

## 1. Domain Overview & Motivation
This module covers critical aspects of **{subject}**, tailored to **{title}**. Students will master the primary theoretical foundations and practical patterns required for university-level proficiency.

## 2. Fundamental Theories & Definitions
- **Core Concept {i}.A**: The foundational mechanism governing system behavior.
- **Analytical Model {i}.B**: Evaluating constraints, latency, throughput, and consistency.
- **Mathematical / Formal Representation**:
$$F_{{system}}(x) = \\sum_{{k=1}}^{{N}} \\alpha_k \\cdot \\phi_k(x) + \\epsilon$$

## 3. Practical Implementation Guidelines
1. Establish verifiable input boundaries and validation checks.
2. Structure modular components with clean separation of concerns.
3. Test edge conditions and error handling routines thoroughly.

## 4. Summary & Assessment Checkpoints
- Ensure you can define the core mechanisms without consulting references.
- Review the practical trade-offs discussed in class regarding performance and scalability.
""",
            "summary": f"Comprehensive guide to Module {i} in {title}, detailing core theories, mathematical formulations, and engineering practices."
        })
    return sections


def generate_quiz_for_section(
    course_title: str,
    section_title: str,
    section_content: str,
    section_index: int = 0
) -> List[Dict[str, Any]]:
    """
    Generates 5 to 8 interactive questions for a given section.
    Uses Groq LLM if configured; otherwise uses specialized question banks.
    """
    groq_client = get_groq_client()
    
    if groq_client:
        try:
            system_prompt = (
                "You are an assessment specialist for a university LMS. "
                "Generate 5 to 8 high-quality quiz questions based on the provided section text. "
                "Include a mix of multiple_choice, true_false, and short_answer. "
                "Output ONLY valid JSON matching: "
                "{\"questions\": [{\"question_text\": str, \"question_type\": str, \"options\": [str], \"correct_answer\": str, \"explanation\": str, \"associated_concept\": str}]}"
            )
            user_msg = (
                f"Course: {course_title}\n"
                f"Section: {section_title}\n\n"
                f"Section Content:\n{section_content[:4000]}"
            )
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ],
                model=settings.GROQ_MODEL,
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            parsed = json.loads(chat_completion.choices[0].message.content)
            if "questions" in parsed and len(parsed["questions"]) > 0:
                return parsed["questions"]
        except Exception as e:
            logger.warning(f"Groq API quiz generation failed, using local bank: {e}")

    # Fallback to local question bank if ML or generic
    if section_index < len(MACHINE_LEARNING_QUESTIONS):
        return MACHINE_LEARNING_QUESTIONS[section_index]
    
    # Generic question generator
    return [
        {
            "question_text": f"What is the primary objective of studying {section_title}?",
            "question_type": "multiple_choice",
            "options": [
                f"To master theoretical foundations and practical applications of {section_title}",
                "To memorize static definitions without practical implementation",
                "To eliminate all software dependencies in production systems",
                "None of the above"
            ],
            "correct_answer": f"To master theoretical foundations and practical applications of {section_title}",
            "explanation": f"Understanding both the theory and applied mechanics is crucial in {section_title}.",
            "associated_concept": f"{section_title} Core Concept"
        },
        {
            "question_text": f"True or False: The principles discussed in {section_title} apply to real-world software and engineering workflows.",
            "question_type": "true_false",
            "options": ["True", "False"],
            "correct_answer": "True",
            "explanation": "Modern engineering principles require strict adherence to validated patterns.",
            "associated_concept": f"{section_title} Application"
        },
        {
            "question_text": f"Explain one primary benefit of following the guidelines established in {section_title}.",
            "question_type": "short_answer",
            "options": [],
            "correct_answer": "It provides structured, verifiable methodology that minimizes runtime failures and improves system scalability.",
            "explanation": "Systematic design practices ensure reproducibility and reliability across deployments.",
            "associated_concept": f"{section_title} Best Practices"
        }
    ]


def answer_student_chat(
    section_title: str,
    section_content: str,
    chat_history: List[Dict[str, str]],
    user_message: str
) -> Dict[str, str]:
    """
    Answers student questions grounded in the current section's content.
    Returns dict: {"content": str, "sources_cited": str}
    """
    groq_client = get_groq_client()
    
    if groq_client:
        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an encouraging, highly knowledgeable AI University Teaching Assistant for EduAI. "
                        "Answer the student's question clearly, grounded in the provided lesson context. "
                        "If the answer is in the lesson, cite the specific heading or section. "
                        "Keep explanations pedagogical, easy to digest, with simple examples when needed.\n\n"
                        f"Current Lesson: {section_title}\n"
                        f"Lesson Content:\n{section_content[:6000]}"
                    )
                }
            ]
            for h in chat_history[-6:]:
                messages.append({"role": h["role"], "content": h["content"]})
            messages.append({"role": "user", "content": user_message})

            chat_completion = groq_client.chat.completions.create(
                messages=messages,
                model=settings.GROQ_MODEL,
                temperature=0.3
            )
            response_text = chat_completion.choices[0].message.content
            return {
                "content": response_text,
                "sources_cited": f"Lesson: {section_title} (EduAI Grounded AI Tutor)"
            }
        except Exception as e:
            logger.warning(f"Groq chat failed: {e}")

    # --- Local Deterministic Teaching Assistant Fallback ---
    q = user_message.lower()
    
    # Check common queries
    if "overfit" in q:
        return {
            "content": (
                "**Overfitting Explained Simply:**\n\n"
                "Overfitting happens when a model learns the training data *too well*, including all its random noise and quirks, "
                "like a student memorizing past exam questions word-for-word instead of understanding the concepts. When given new, unseen questions, "
                "the model fails to generalize.\n\n"
                "**How to Fix It:**\n"
                "1. **Regularization** (L1 Lasso or L2 Ridge to penalize large weights).\n"
                "2. **Add more training data** or apply data augmentation.\n"
                "3. **Prune decision trees** or use Dropout in neural networks.\n"
                "4. **Early stopping** during training."
            ),
            "sources_cited": f"Chapter on Bias-Variance & Regularization in {section_title}"
        }
    elif "underfit" in q or "bias" in q:
        return {
            "content": (
                "**Underfitting (High Bias) Explained:**\n\n"
                "Underfitting occurs when an algorithm is too simple to capture the underlying pattern in the data "
                "(e.g., trying to fit a straight line to a curved parabolic relationship).\n\n"
                "**How to Fix It:**\n"
                "1. Use a more expressive or non-linear model.\n"
                "2. Engineer richer interaction features or polynomial terms.\n"
                "3. Decrease the regularization penalty ($\\lambda$)."
            ),
            "sources_cited": f"Bias-Variance Framework in {section_title}"
        }
    elif "supervised" in q or "unsupervised" in q:
        return {
            "content": (
                "**Supervised vs. Unsupervised Learning:**\n\n"
                "- **Supervised Learning**: We provide the model both input features ($X$) and ground-truth answers ($y$). The model learns to map inputs to targets (e.g., classifying emails as spam or predicting housing prices).\n"
                "- **Unsupervised Learning**: We only provide raw features ($X$) without labels. The model discovers natural groupings, clusters, or lower-dimensional projections on its own (e.g., K-Means customer segmentation, PCA compression)."
            ),
            "sources_cited": f"Taxonomy Section in {section_title}"
        }
    elif "summar" in q:
        return {
            "content": (
                f"**Lesson Summary for '{section_title}':**\n\n"
                "Here are the core takeaways you should review before quizzes:\n"
                "1. Understand the fundamental definitions and why this methodology is used.\n"
                "2. Keep the mathematical formulation and optimization objective in mind.\n"
                "3. Remember the practical evaluation metrics (accuracy vs precision/recall, or inertia vs variance).\n"
                "4. Be mindful of data leakage and always validate using proper cross-validation splits!"
            ),
            "sources_cited": f"Revision Summary in {section_title}"
        }
    elif "example" in q or "practice" in q:
        return {
            "content": (
                f"**Practical Example for {section_title}:**\n\n"
                "Imagine you are building a fraud-detection engine for a university payment portal:\n"
                "- **Data**: Transaction amount, location, time, and device fingerprint.\n"
                "- **Challenge**: 99.9% of transactions are legitimate, so accuracy would be misleading.\n"
                "- **Solution**: Optimize for **Recall** so no fraudulent transaction slips through, while using Cross-Validation to guarantee generalization on new payment types."
            ),
            "sources_cited": f"Practical Application Case in {section_title}"
        }
    else:
        # Grounded response using content snippet
        snippet = section_content[:500].replace("#", "").strip()
        return {
            "content": (
                f"Hello! Regarding your question about **{section_title}**:\n\n"
                f"Based on our lesson material: {snippet}...\n\n"
                "Key learning principle: Ensure you grasp how the theoretical concepts translate directly into practical implementations and evaluation metrics. "
                "Let me know if you would like me to break down any specific formula, code snippet, or exam tip from this section!"
            ),
            "sources_cited": f"Lesson Overview in {section_title}"
        }
