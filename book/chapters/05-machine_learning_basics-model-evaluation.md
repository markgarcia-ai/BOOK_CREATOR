## Introduction

In machine learning, understanding how well a model performs is crucial. Model evaluation provides insights into a model's strengths, weaknesses, and generalization capabilities [@James2013:ModelEvaluation].

## Performance Metrics

### Classification Metrics

Performance metrics help quantify a model's predictive power across different scenarios:

1. **Accuracy**: Proportion of correct predictions
   - $Accuracy = \frac{Correct\,Predictions}{Total\,Predictions}$ [[NEEDS_SOURCE]]

2. **Precision**: Measures exactness of positive predictions
   - $Precision = \frac{True\,Positives}{True\,Positives + False\,Positives}$ [@Brownlee2020]

3. **Recall**: Measures completeness of positive predictions
   - $Recall = \frac{True\,Positives}{True\,Positives + False\,Negatives}$ [@Brownlee2020]

4. **F1-Score**: Harmonic mean balancing precision and recall
   - $F1 = 2 * \frac{Precision * Recall}{Precision + Recall}$ [@Brownlee2020]

{{FIG:classification-metrics:\