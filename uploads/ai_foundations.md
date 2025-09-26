# 📘 AI Foundations for Portfolio Projects

This document summarizes the **mathematical and conceptual foundations** required to build impactful AI projects, including **LLMs, NLP, Agents, Image Detection, Finance AI, Explainable AI, and Path Planning**.

---

## 1. Core Mathematics for AI

### Linear Algebra
- Vectors, dot product, cosine similarity (used in embeddings & vector search).
- Matrices and matrix multiplication (neural networks).
- Eigenvalues & eigenvectors (PCA, dimensionality reduction).

### Probability & Statistics
- Bayes’ theorem.
- Expectation, variance, covariance.
- Gaussian distributions, hypothesis testing.

### Calculus
- Derivatives and gradients (backpropagation).
- Chain rule (gradient descent).
- Integrals (probability & expectation).

### Optimization
- Gradient Descent, Stochastic Gradient Descent (SGD).
- Convex optimization.
- Regularization (L1, L2).

### Python Essentials
- `NumPy`, `Pandas` for math and data handling.
- `Matplotlib`, `Plotly` for visualization.
- `PyTorch`, `TensorFlow` for ML/NN.

---

## 2. LLMs & NLP (RAG, Agents, Text AI)

### NLP Basics
- Tokenization (WordPiece, BPE).
- Embeddings (Word2Vec, GloVe, Transformer embeddings).
- Attention mechanism.

### Transformers
- **Attention formula**:  
  \[
  \text{Attention}(Q,K,V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
  \]
- Positional encodings.
- Multi-head attention.

### Retrieval Concepts
- Cosine similarity, dot product.
- k-Nearest Neighbors.
- Vector databases (FAISS, Chroma).

### Evaluation
- Precision, Recall, F1.
- BLEU, ROUGE, Perplexity.

---

## 3. Agentic AI

### Reinforcement Learning (RL)
- Markov Decision Process (MDP): states, actions, rewards.
- **Bellman Equation**:  
  \[
  Q(s,a) = r + \gamma \max_{a'} Q(s', a')
  \]
- Policy gradients (REINFORCE, PPO).

### Planning & Reasoning
- Search algorithms (DFS, BFS, A*, Beam Search).
- Prompt chaining & reasoning strategies.

---

## 4. Image Detection & Vision AI

### Convolutional Neural Networks (CNNs)
- Convolution operation (dot product with kernel).
- Pooling layers (max, average).
- Feature extraction.

### Object Detection
- Intersection-over-Union (IoU).
- Non-Maximum Suppression (NMS).

### Vision Transformers (ViT)
- Image patching.
- Self-attention in vision.

---

## 5. Finance + Sentiment Analysis

### Time-Series Analysis
- Log returns:  
  \[
  r_t = \ln \left(\frac{P_t}{P_{t-1}}\right)
  \]
- Moving averages, volatility.

### Finance Models
- **CAPM**:  
  \[
  E(R_i) = R_f + \beta_i (E(R_m) - R_f)
  \]
- **Sharpe Ratio**:  
  \[
  S = \frac{E[R_p - R_f]}{\sigma_p}
  \]

### ML Models
- Regression (linear, logistic).
- LSTMs & Transformers for sequential prediction.

---

## 6. Explainable AI (XAI)

### LIME
- Perturb input, observe changes in output.

### SHAP
- **Shapley value formula**:  
  \[
  \phi_i = \sum_{S \subseteq N \setminus \{i\}} \frac{|S|!(n-|S|-1)!}{n!} [f(S \cup \{i\}) - f(S)]
  \]

### Grad-CAM
- Gradient-based visual explanations for CNNs.

---

## 7. Path Planning & Anticipation

### Graph Search
- A*, Dijkstra’s Algorithm.
- Heuristics (Manhattan, Euclidean distance).

### Control Theory
- PID controllers.
- State estimation.

### Multi-Agent Systems
- Game theory basics (Nash equilibrium).
- Collision avoidance strategies.

### Prediction
- Sequence models (LSTMs, Transformers) for trajectory prediction.
- Multi-Agent Reinforcement Learning (MARL).

---

# ✅ Summary

To excel in these projects:
- **Linear Algebra + Probability** → embeddings, LLMs, CNNs.
- **Optimization + Calculus** → model training.
- **Graph Search + RL** → agents & path planning.
- **Finance Math** → CAPM, Sharpe, log returns.
- **XAI Math** → SHAP, LIME.

With these foundations, you’ll have both the **theoretical depth** and **practical skills** to build impactful AI applications.

