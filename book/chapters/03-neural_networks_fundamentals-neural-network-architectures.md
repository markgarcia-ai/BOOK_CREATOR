## Introduction to Neural Network Architectures

Neural networks represent a powerful class of machine learning models inspired by the biological neural structures of the human brain. These computational models have revolutionized numerous domains, from computer vision to natural language processing [@goodfellow2016deep].

## Feedforward Networks

### Basic Structure and Principles
Feedforward networks, also known as multilayer perceptrons (MLPs), represent the foundational architecture of neural networks. In these networks, information flows in one direction—from input layer through hidden layers to the output layer [@Bishop2006].

#### Key Characteristics
- Neurons organized in discrete layers
- No feedback connections
- Typically trained using backpropagation
- Mathematical representation: $y = f(W^T x + b)$

### Activation Functions
Different activation functions enable neural networks to model complex, non-linear relationships:

1. **Sigmoid**: $\sigma(x) = \frac{1}{1 + e^{-x}}$
2. **ReLU**: $f(x) = \max(0, x)$
3. **Tanh**: $\tanh(x) = \frac{e^x - e^{-x}}{e^x + e^{-x}}$

{{FIG:feedforward-network: