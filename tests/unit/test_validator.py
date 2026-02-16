"""Unit tests for validation module."""

import unittest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from validator import validate_title, validate_description, validate_task_id, sanitize_input


class TestTitleValidation(unittest.TestCase):
    """Test title validation functions."""

    def test_empty_title_rejected(self):
        """Test that empty title is rejected."""
        is_valid, error = validate_title("")
        self.assertFalse(is_valid)
        self.assertIn("empty", error.lower())

    def test_whitespace_only_title_rejected(self):
        """Test that whitespace-only title is rejected."""
        is_valid, error = validate_title("   ")
        self.assertFalse(is_valid)
        self.assertIn("empty", error.lower())

    def test_valid_title_accepted(self):
        """Test that a valid title is accepted."""
        is_valid, error = validate_title("Buy groceries")
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_title_max_length_enforcement(self):
        """Test that title exceeds maximum length is rejected."""
        # Create a title longer than 500 characters
        long_title = "x" * 501
        is_valid, error = validate_title(long_title)
        self.assertFalse(is_valid)
        self.assertIn("500", error)

    def test_title_at_max_length_accepted(self):
        """Test that title at exactly max length is accepted."""
        max_title = "x" * 500
        is_valid, error = validate_title(max_title)
        self.assertTrue(is_valid)


class TestDescriptionValidation(unittest.TestCase):
    """Test description validation functions."""

    def test_empty_description_accepted(self):
        """Test that empty description is accepted."""
        is_valid, error = validate_description("")
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_valid_description_accepted(self):
        """Test that a valid description is accepted."""
        is_valid, error = validate_description("This is a detailed description.")
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_description_max_length_enforcement(self):
        """Test that description exceeds maximum length is rejected."""
        # Create a description longer than 5000 characters
        long_desc = "x" * 5001
        is_valid, error = validate_description(long_desc)
        self.assertFalse(is_valid)
        self.assertIn("5000", error)

    def test_description_at_max_length_accepted(self):
        """Test that description at exactly max length is accepted."""
        max_desc = "x" * 5000
        is_valid, error = validate_description(max_desc)
        self.assertTrue(is_valid)


class TestTaskIDValidation(unittest.TestCase):
    """Test task ID validation functions."""

    def test_valid_numeric_id_accepted(self):
        """Test that valid numeric ID is accepted."""
        is_valid, error = validate_task_id("1")
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_valid_multiple_digit_id_accepted(self):
        """Test that multi-digit ID is accepted."""
        is_valid, error = validate_task_id("123")
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_empty_id_rejected(self):
        """Test that empty ID is rejected."""
        is_valid, error = validate_task_id("")
        self.assertFalse(is_valid)
        self.assertIn("invalid", error.lower())

    def test_negative_id_format_rejected(self):
        """Test that negative-looking ID format is rejected."""
        is_valid, error = validate_task_id("-1")
        self.assertFalse(is_valid)

    def test_decimal_id_format_rejected(self):
        """Test that decimal ID format is rejected."""
        is_valid, error = validate_task_id("1.5")
        self.assertFalse(is_valid)

    def test_alpha_id_format_rejected(self):
        """Test that alphabetic ID is rejected."""
        is_valid, error = validate_task_id("abc")
        self.assertFalse(is_valid)


class TestSanitizeInput(unittest.TestCase):
    """Test input sanitization functions."""

    def test_sanitize_removes_leading_whitespace(self):
        """Test that leading whitespace is removed."""
        result = sanitize_input("  Hello")
        self.assertEqual(result, "Hello")

    def test_sanitize_removes_trailing_whitespace(self):
        """Test that trailing whitespace is removed."""
        result = sanitize_input("Hello  ")
        self.assertEqual(result, "Hello")

    def test_sanitize_preserves_internal_whitespace(self):
        """Test that internal whitespace is preserved."""
        result = sanitize_input("Hello World")
        self.assertEqual(result, "Hello World")

    def test_sanitize_preserves_special_characters(self):
        """Test that special characters are preserved."""
        result = sanitize_input("Task: Buy groceries!")
        self.assertEqual(result, "Task: Buy groceries!")

    def test_sanitize_empty_returns_empty(self):
        """Test that empty string returns empty."""
        result = sanitize_input("")
        self.assertEqual(result, "")


class TestErrorMessageFormatting(unittest.TestCase):
    """Test error message formatting."""

    def test_title_error_message_format(self):
        """Test that title error messages are user-friendly."""
        is_valid, error = validate_title("")
        self.assertIn("title", error.lower())

    def test_description_error_message_format(self):
        """Test that description error messages are user-friendly."""
        is_valid, error = validate_description("x" * 5001)
        self.assertIn("description", error.lower())

    def test_id_error_message_format(self):
        """Test that ID error messages are user-friendly."""
        is_valid, error = validate_task_id("")
        self.assertIn("id", error.lower())

    def test_error_includes_max_length(self):
        """Test that length errors include the max value."""
        is_valid, error = validate_title("x" * 501)
        self.assertIn("500", error)


if __name__ == '__main__':
    unittest.main()
