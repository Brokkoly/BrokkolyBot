import unittest
from unittest import TestCase
import brokkoly_bot

good_add_string="!add !labe Labe is good and so is this string"

class MyTestCase(TestCase):
    def test_parse_add_valid(self):
        parse_results = brokkoly_bot.parse_add(good_add_string)
        self.assertEqual(True, parse_results[0])
        self.assertEqual("!labe", parse_results[1])
        self.assertEqual("Labe is good and so is this string", parse_results[2])


#if __name__ == '__main__':
    #unittest.main()
