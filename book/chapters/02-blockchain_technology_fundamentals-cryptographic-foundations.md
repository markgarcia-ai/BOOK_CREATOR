## Introduction to Cryptographic Foundations

Cryptography forms the fundamental security infrastructure of blockchain technology, providing mechanisms for secure communication, authentication, and data integrity [@Schneier2015]. This chapter explores the core cryptographic principles that enable blockchain's robust security model.

## Public Key Cryptography

### Asymmetric Encryption Principles

Public key cryptography represents a revolutionary approach to secure communication [@Rivest1978]. In this system, each participant possesses two mathematically related keys:

- **Public Key**: Openly shared and used for encryption
- **Private Key**: Kept secret and used for decryption

The mathematical relationship can be represented as:

$Decrypt_{PrivateKey}(Encrypt_{PublicKey}(Message)) = Message$

{{FIG:public-key-cryptography: