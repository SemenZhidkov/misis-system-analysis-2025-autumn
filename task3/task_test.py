import json
import ast
import unittest
from task import main


class TestMain(unittest.TestCase):
    def test_main_with_examples(self):
        with open('examples/Ранжировка  A.json', 'r', encoding='utf-8') as f:
            ranking_a_str = f.read().strip()
        with open('examples/Ранжировка  B.json', 'r', encoding='utf-8') as f:
            ranking_b_str = f.read().strip()
        with open('examples/Согласованная кластерная ранжировка AB.json', 'r', encoding='utf-8') as f:
            expected_str = f.read().strip()
        
        result = main(ranking_a_str, ranking_b_str)
        result_parsed = ast.literal_eval(result)
        expected = ast.literal_eval(expected_str)
        
        self.assertEqual(result_parsed, expected)


if __name__ == '__main__':
    unittest.main()
