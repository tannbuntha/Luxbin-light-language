#!/usr/bin/env python3
"""
Test suite for LUXBIN Code Translator
Developed by Nicheai - Testing code translation functionality

Tests cover:
- Python to JavaScript translation
- JavaScript to Python translation
- Type inference
- Error handling
- Edge cases

Company: Nicheai (https://nicheai.com)
Author: Nichole Christie
License: MIT
"""

import unittest
import sys
import os
from luxbin_code_translator import CodeTranslator


class TestCodeTranslator(unittest.TestCase):
    """Test cases for the CodeTranslator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.translator = CodeTranslator()

    def test_python_to_javascript_basic_function(self):
        """Test basic Python function translation to JavaScript."""
        python_code = """
def greet(name):
    return "Hello, " + name
"""
        result = self.translator.translate_python_to_javascript(python_code)
        self.assertIn('function greet(name)', result)
        self.assertIn('return "Hello, " + name;', result)

    def test_python_to_javascript_variables(self):
        """Test Python variable assignments to JavaScript."""
        python_code = """
x = 42
y = "hello"
z = [1, 2, 3]
"""
        result = self.translator.translate_python_to_javascript(python_code)
        self.assertIn('let x = 42;', result)
        self.assertIn('let y = "hello";', result)
        self.assertIn('let z = [1, 2, 3];', result)

    def test_python_to_javascript_expressions(self):
        """Test Python expressions translation."""
        python_code = "result = a + b * c"
        result = self.translator.translate_python_to_javascript(python_code)
        self.assertIn('let result = a + b * c;', result)

    def test_python_to_javascript_operators(self):
        """Test Python operators translation."""
        python_code = """
x = a == b
y = a != c
z = a > b
"""
        result = self.translator.translate_python_to_javascript(python_code)
        self.assertIn('let x = a === b;', result)
        self.assertIn('let y = a !== c;', result)
        self.assertIn('let z = a > b;', result)

    def test_javascript_to_python_basic_function(self):
        """Test basic JavaScript function translation to Python."""
        js_code = 'function greet(name) { return "Hello, " + name; }'
        result = self.translator.translate_javascript_to_python(js_code)
        self.assertIn('def greet(name):', result)
        self.assertIn('return "Hello, " + name', result)

    def test_javascript_to_python_variables(self):
        """Test JavaScript variable declarations to Python."""
        js_code = """
let x = 42;
const y = "hello";
var z = [1, 2, 3];
"""
        result = self.translator.translate_javascript_to_python(js_code)
        self.assertIn('x = 42', result)
        self.assertIn('y = "hello"', result)
        self.assertIn('z = [1, 2, 3]', result)

    def test_javascript_to_python_expressions(self):
        """Test JavaScript expressions translation."""
        js_code = 'result = a + b * c;'
        result = self.translator.translate_javascript_to_python(js_code)
        self.assertIn('result = a + b * c', result)

    def test_javascript_to_python_operators(self):
        """Test JavaScript operators translation."""
        js_code = """
x = a === b;
y = a !== c;
z = a && b;
w = a || b;
"""
        result = self.translator.translate_javascript_to_python(js_code)
        self.assertIn('x = a == b', result)
        self.assertIn('y = a != c', result)
        self.assertIn('z = a and b', result)
        self.assertIn('w = a or b', result)

    def test_type_inference_python(self):
        """Test type inference for Python code."""
        code = """
x = 42
y = "hello"
z = [1, 2, 3]
w = {"key": "value"}
"""
        types = self.translator.infer_types(code, 'python')
        self.assertEqual(types['x'].name, 'int')
        self.assertEqual(types['y'].name, 'str')
        self.assertEqual(types['z'].name, 'list')
        self.assertEqual(types['w'].name, 'dict')

    def test_type_inference_javascript(self):
        """Test type inference for JavaScript code."""
        # This is currently mock implementation
        types = self.translator.infer_types("let x = 42;", 'javascript')
        # Should not crash, but may return mock data
        self.assertIsInstance(types, dict)

    def test_invalid_python_syntax(self):
        """Test error handling for invalid Python syntax."""
        with self.assertRaises(ValueError):
            self.translator.translate_python_to_javascript("def invalid syntax(")

    def test_invalid_javascript_syntax(self):
        """Test error handling for invalid JavaScript syntax."""
        with self.assertRaises(ValueError):
            self.translator.translate_javascript_to_python("function invalid syntax(")

    def test_empty_code(self):
        """Test handling of empty code."""
        result = self.translator.translate_python_to_javascript("")
        self.assertEqual(result, "")

        result = self.translator.translate_javascript_to_python("")
        self.assertEqual(result, "# JavaScript to Python conversion placeholder")

    def test_type_map_structure(self):
        """Test that type map is properly structured."""
        type_map = self.translator.type_map
        self.assertIn('int', type_map)
        self.assertIn('str', type_map)
        self.assertIn('Array', type_map)

        int_type = type_map['int']
        self.assertEqual(int_type.category, 'primitive')
        self.assertEqual(int_type.js_equivalent, 'number')
        self.assertEqual(int_type.py_equivalent, 'int')

    def test_round_trip_consistency(self):
        """Test that translations are somewhat consistent."""
        # Simple function that should translate both ways
        simple_func = "def test(): return 42"

        # Python -> JS
        js_result = self.translator.translate_python_to_javascript(simple_func)
        self.assertIn('function test()', js_result)

        # JS -> Python (using equivalent JS)
        js_equivalent = "function test() { return 42; }"
        py_result = self.translator.translate_javascript_to_python(js_equivalent)
        self.assertIn('def test():', py_result)


class TestIntegration(unittest.TestCase):
    """Integration tests for the translator system."""

    def setUp(self):
        self.translator = CodeTranslator()

    def test_complex_python_function(self):
        """Test translation of a more complex Python function."""
        python_code = '''
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(10)
'''
        result = self.translator.translate_python_to_javascript(python_code)
        self.assertIn('function fibonacci(n)', result)
        self.assertIn('if (n <= 1)', result)
        self.assertIn('return n;', result)
        self.assertIn('return fibonacci(n - 1) + fibonacci(n - 2);', result)

    def test_complex_javascript_function(self):
        """Test translation of a more complex JavaScript function."""
        js_code = '''
function factorial(n) {
    if (n === 0) {
        return 1;
    } else {
        return n * factorial(n - 1);
    }
}
'''
        result = self.translator.translate_javascript_to_python(js_code)
        self.assertIn('def factorial(n):', result)
        self.assertIn('if n == 0:', result)
        self.assertIn('return 1', result)
        self.assertIn('return n * factorial(n - 1)', result)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)