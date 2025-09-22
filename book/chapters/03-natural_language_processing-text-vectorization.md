## Introduction to Text Vectorization

Text vectorization is a fundamental process in natural language processing (NLP) that transforms textual data into numerical representations suitable for machine learning algorithms [@Jurafsky2022]. This chapter explores key techniques that convert raw text into structured, computable formats.

### Bag of Words (BoW)

#### Basic Concept
Bag of Words is the simplest text vectorization technique, representing text as an unordered collection of words and their frequencies [@Manning2008]. 

#### Implementation
The core idea is to:
1. Tokenize the text into individual words
2. Create a vocabulary of unique terms
3. Count word occurrences in each document

$$V = \{w_1, w_2, ..., w_n\}$$

#### Example
Consider the sentences:
- \