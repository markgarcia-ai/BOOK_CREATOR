## Introduction to File Handling in Python

File handling is a crucial skill for Python programmers, enabling you to read, write, and manipulate data stored in files. This chapter will explore essential techniques for working with files efficiently.

## Reading Text Files

### Opening Files
Python provides simple methods to open and read files. The `open()` function is your primary tool for file operations [@pythonDocs2023].

```python
# Basic file reading
with open('example.txt', 'r') as file:
    content = file.read()
```

### Reading Methods
- `read()`: Reads entire file
- `readline()`: Reads single line
- `readlines()`: Returns list of all lines

{{FIG:file-reading: