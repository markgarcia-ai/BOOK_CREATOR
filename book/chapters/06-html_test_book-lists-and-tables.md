## Introduction to Structured HTML Elements

Lists and tables are fundamental HTML elements that help organize and present information systematically. In this chapter, we'll explore how to create well-structured lists and tables that enhance the readability and presentation of web content.

### Ordered Lists

Ordered lists provide a sequential, numbered representation of information. Created using the `<ol>` tag, these lists are perfect for step-by-step instructions or ranked content.

#### Basic Ordered List Syntax

```html
<ol>
    <li>First item</li>
    <li>Second item</li>
    <li>Third item</li>
</ol>
```

#### List Style Variations

HTML supports multiple ordered list types through the `type` attribute:
- `type='1'`: Numeric (default, 1, 2, 3)
- `type='a'`: Lowercase alphabetic (a, b, c)
- `type='A'`: Uppercase alphabetic (A, B, C)
- `type='i'`: Lowercase Roman numerals (i, ii, iii)
- `type='I'`: Uppercase Roman numerals (I, II, III)

{{FIG:list-types: