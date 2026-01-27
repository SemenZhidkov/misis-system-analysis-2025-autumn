import json
import unittest
from task import main


class TestMain(unittest.TestCase):
    def setUp(self):
        with open('examples/функции-принадлежности-температуры.json', 'r', encoding='utf-8') as f:
            self.temperature_json = f.read().strip()
        with open('examples/функции-принадлежности-управление.json', 'r', encoding='utf-8') as f:
            self.control_json = f.read().strip()
        with open('examples/функция-отображения.json', 'r', encoding='utf-8') as f:
            self.rules_json = f.read().strip()
    
    def test_main_returns_float(self):
        result = main(self.temperature_json, self.control_json, self.rules_json, 20.0)
        self.assertIsInstance(result, float)
    
    def test_main_with_different_temperatures(self):
        result_cold = main(self.temperature_json, self.control_json, self.rules_json, 10.0)
        result_comfort = main(self.temperature_json, self.control_json, self.rules_json, 23.0)
        result_hot = main(self.temperature_json, self.control_json, self.rules_json, 30.0)
        
        self.assertIsInstance(result_cold, float)
        self.assertIsInstance(result_comfort, float)
        self.assertIsInstance(result_hot, float)
        
        self.assertGreater(result_cold, result_hot)
        self.assertGreater(result_comfort, result_hot)
    
    def test_main_with_examples(self):
        result = main(self.temperature_json, self.control_json, self.rules_json, 20.0)
        self.assertGreater(result, 0)
        self.assertLess(result, 30)


if __name__ == '__main__':
    unittest.main()
