import unittest
from unittest import TestCase
import brokkoly_bot

good_add_string = "!add !labe Labe is good and so is this string"


class MyTestCase(TestCase):
    bot = brokkoly_bot.BrokkolyBot(is_unit_test=True)

    # def test_parse_add_valid(self):
    #     parse_results = brokkoly_bot.parse_add(good_add_string)
    #     self.assertEqual(True, parse_results[0])
    #     self.assertEqual("!labe", parse_results[1])
    #     self.assertEqual("Labe is good and so is this string", parse_results[2])

    def test_add_command_only_letters(self):
        self.assertEqual(brokkoly_bot.CAN_ONLY_CONTAIN_LETTERS_ERROR, self.bot.validate_add("$add", "NEW ENTRY"))
        # self.assertEqual(self.bot.validate_add("asdf","<@449815971897671690>"))

    def test_add_command_protected(self):
        self.assertEqual(brokkoly_bot.PROTECTED_COMMAND_ERROR, self.bot.validate_add("add", "New_value"))

    def test_add_command_value_length(self):
        self.assertEqual(brokkoly_bot.NEW_VALUE_TOO_LONG_ERROR, self.bot.validate_add("asdf",
                                                                                      "12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890asdf"))
        self.assertNotEqual(brokkoly_bot.NEW_VALUE_TOO_LONG_ERROR, self.bot.validate_add("asdf",
                                                                                         "12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"))

    def test_add_command_command_length(self):
        self.assertEqual(brokkoly_bot.EXPECTED_SYNTAX_ERROR, self.bot.validate_add("ad", "New_value"))
        self.assertEqual(brokkoly_bot.COMMAND_TOO_LONG_ERROR,
                         self.bot.validate_add("asdfasdfasdfasdfasdfa", "New_value"))

    def test_add_command_valid(self):
        self.assertEqual(None, self.bot.validate_add("valid", "Valid Value"))


if __name__ == '__main__':
    unittest.main()
