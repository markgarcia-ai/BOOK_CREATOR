## Introduction

Blockchain technology, while revolutionary, is not inherently immune to security threats. This chapter explores the complex landscape of blockchain security, examining vulnerabilities, best practices, and emerging protective strategies [@nakamoto2008bitcoin].

## Common Blockchain Vulnerabilities

### 51% Attack
A fundamental security risk where an attacker controls more than half of a network's mining hash rate, potentially allowing transaction manipulation [@eyal2014majority]. 

Key vulnerability characteristics:
- Enables double-spending
- Most threatening in smaller blockchain networks
- Requires significant computational resources

### Smart Contract Exploits
Smart contracts, while powerful, can contain critical vulnerabilities [[NEEDS_SOURCE]]:

1. Reentrancy attacks
2. Integer overflow/underflow
3. Unchecked external calls
4. Timestamp dependency

{{FIG:smart-contract-vulnerabilities: