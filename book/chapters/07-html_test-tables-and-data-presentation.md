## Introduction to HTML Tables

Tables are fundamental for organizing and presenting structured data on web pages. In this chapter, we'll explore how to create, style, and manage HTML tables effectively.

### Basic Table Structure

HTML tables are created using the `<table>`, `<tr>`, and `<td>` tags. Here's a basic example:

```html
<table>
    <tr>
        <td>First Column</td>
        <td>Second Column</td>
    </tr>
</table>
```

#### Key Elements
- `<table>`: Defines the entire table
- `<tr>`: Creates a table row
- `<td>`: Defines individual table cells

### Table Headers and Rows

To improve semantic structure, use `<th>` for header cells:

```html
<table>
    <tr>
        <th>Name</th>
        <th>Age</th>
    </tr>
    <tr>
        <td>Alice</td>
        <td>28</td>
    </tr>
</table>
```

### Complex Table Layouts

Advanced tables can include:
- Merged cells with `colspan` and `rowspan`
- Multiple header rows
- Nested table structures

#### Cell Merging Example
```html
<table>
    <tr>
        <th colspan='2'>Merged Header</th>
    </tr>
    <tr>
        <td>Column 1</td>
        <td>Column 2</td>
    </tr>
</table>
```

### Styling and Accessibility

{{FIG:table-structure: