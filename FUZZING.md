### CSV Fuzzing Ideas

1. **Empty Cells**: Insert empty cells randomly in the CSV.
2. **Duplicate Rows/Columns**: Duplicate an entire row or column.
3. **Long Strings**: Insert extremely long strings into individual cells.
4. **Special Characters**: Insert special characters (e.g., newlines, tabs, ASCII control characters) into cells.
5. **Inconsistent Data Types**: Insert strings in numerical columns or vice versa.
6. **Header Manipulation**: Remove or duplicate header lines.
7. **Negative Numbers**: Insert negative numbers in columns expecting positive values.
8. **Foreign Characters**: Use Unicode or foreign characters in cells.
9. **Extra Commas**: Insert extra commas between fields.
10. **Nested Quotes**: Insert nested quotes inside a cell value.

### JSON Fuzzing Ideas

1. **Duplicate Keys**: Add duplicate keys within a JSON object.
2. **Unescaped Characters**: Insert characters that should be escaped (like quotes or backslashes) within strings.
3. **Nesting**: Excessively nest JSON objects or arrays.
4. **Null Values**: Insert nulls in place of expected object keys or array elements.
5. **Array as Object**: Replace an expected object with an array or vice versa.
6. **Unexpected Data Types**: Use incorrect data types for values (e.g., string instead of boolean).
7. **Long Strings**: Use extremely long strings as keys or values.
8. **Numerical Extremes**: Insert extremely large or small numbers, or floating point numbers in unexpected places.
9. **Trailing Commas**: Add trailing commas in objects or arrays.

### General Fuzzing Ideas

1. **Bit Flipping**: Flip random bits in the serialized byte representation of the input.
2. **Random Insertion**: Insert random bytes or characters into the input.
3. **Truncation**: Truncate the input at random locations.
4. **Repetition**: Repeat chunks of data within the input.
5. **Shuffling**: Shuffle the order of elements within collections (e.g., JSON arrays or CSV rows).
6. **Exponential Growth**: Create inputs that grow exponentially in size, e.g., by repeatedly doubling the input.
7. **Out-of-Bounds Values**: Use numbers or lengths that exceed expected bounds.
8. **Invalid Encoding**: Use invalid character encodings.

