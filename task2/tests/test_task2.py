"""
Тесты для функции task из модуля task2
"""
import pytest
from task2 import task


class TestBasicFunctionality:
    """Базовые тесты функциональности"""
    
    def test_simple_tree(self):
        """Тест на простом дереве из примера"""
        csv_string = "1,2\n1,3\n3,4\n3,5"
        root = "1"
        entropy, normalized = task(csv_string, root)
        
        assert isinstance(entropy, float)
        assert isinstance(normalized, float)
        assert entropy >= 0
        assert normalized >= 0
    
    def test_linear_chain(self):
        """Тест на линейной цепочке узлов"""
        csv_string = "1,2\n2,3\n3,4"
        root = "1"
        entropy, normalized = task(csv_string, root)
        
        assert entropy >= 0
        assert normalized >= 0
    
    def test_single_edge(self):
        """Тест с одним ребром"""
        csv_string = "1,2"
        root = "1"
        entropy, normalized = task(csv_string, root)
        
        assert entropy >= 0
        assert normalized >= 0


class TestTreeStructures:
    """Тесты различных структур деревьев"""
    
    def test_binary_tree(self):
        """Тест на бинарном дереве"""
        csv_string = "1,2\n1,3\n2,4\n2,5\n3,6\n3,7"
        root = "1"
        entropy, normalized = task(csv_string, root)
        
        assert entropy > 0
        assert normalized > 0
    
    def test_wide_tree(self):
        """Тест на широком дереве (много детей у корня)"""
        csv_string = "1,2\n1,3\n1,4\n1,5\n1,6"
        root = "1"
        entropy, normalized = task(csv_string, root)
        
        assert entropy > 0
        assert normalized > 0
    
    def test_deep_tree(self):
        """Тест на глубоком дереве"""
        csv_string = "1,2\n2,3\n3,4\n4,5\n5,6"
        root = "1"
        entropy, normalized = task(csv_string, root)
        
        assert entropy > 0
        assert normalized > 0
    
    def test_asymmetric_tree(self):
        """Тест на несимметричном дереве"""
        csv_string = "1,2\n1,3\n2,4\n2,5\n2,6\n3,7"
        root = "1"
        entropy, normalized = task(csv_string, root)
        
        assert entropy > 0
        assert normalized > 0


class TestRelations:
    """Тесты корректности вычисления отношений"""
    
    def test_parent_child_relation(self):
        """Проверка что r1 (родитель-потомок) работает корректно"""
        csv_string = "1,2\n1,3"
        root = "1"
        entropy, normalized = task(csv_string, root)
        
        # Должна быть энтропия, так как есть связи
        assert entropy > 0
    
    def test_siblings_relation(self):
        """Проверка что r5 (отношение братьев/сестер) работает"""
        csv_string = "1,2\n1,3\n1,4"
        root = "1"
        entropy, normalized = task(csv_string, root)
        
        # С тремя братьями/сестрами должна быть значительная энтропия
        assert entropy > 0
    
    def test_indirect_descendants(self):
        """Проверка что r3 (непрямые потомки) вычисляется"""
        csv_string = "1,2\n2,3\n3,4"
        root = "1"
        entropy, normalized = task(csv_string, root)
        
        # Должны быть непрямые связи (1->3, 1->4, 2->4)
        assert entropy > 0


class TestEdgeCases:
    """Тесты граничных случаев"""
    
    def test_empty_csv(self):
        """Тест с пустой строкой CSV"""
        csv_string = ""
        root = "1"
        entropy, normalized = task(csv_string, root)
        
        # С одним узлом энтропия должна быть 0
        assert entropy == 0
        assert normalized == 0
    
    def test_whitespace_handling(self):
        """Тест обработки пробелов"""
        csv_string = " 1 , 2 \n 1 , 3 "
        root = "1"
        entropy, normalized = task(csv_string, root)
        
        assert entropy >= 0
        assert normalized >= 0
    
    def test_large_numbers(self):
        """Тест с большими номерами узлов"""
        csv_string = "100,200\n100,300\n200,400"
        root = "100"
        entropy, normalized = task(csv_string, root)
        
        assert entropy > 0
        assert normalized > 0


class TestReturnValues:
    """Тесты возвращаемых значений"""
    
    def test_return_type(self):
        """Проверка типов возвращаемых значений"""
        csv_string = "1,2\n1,3"
        root = "1"
        result = task(csv_string, root)
        
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], float)
        assert isinstance(result[1], float)
    
    def test_rounding(self):
        """Проверка округления до одного знака"""
        csv_string = "1,2\n1,3\n3,4\n3,5"
        root = "1"
        entropy, normalized = task(csv_string, root)
        
        # Проверяем что округлено до 1 знака после запятой
        assert entropy == round(entropy, 1)
        assert normalized == round(normalized, 1)
    
    def test_normalized_bounds(self):
        """Проверка что нормированная сложность в разумных пределах"""
        csv_string = "1,2\n1,3\n2,4\n2,5\n3,6\n3,7"
        root = "1"
        entropy, normalized = task(csv_string, root)
        
        # Нормированная величина должна быть положительной
        assert normalized >= 0


class TestConsistency:
    """Тесты консистентности результатов"""
    
    def test_same_input_same_output(self):
        """Одинаковый вход должен давать одинаковый выход"""
        csv_string = "1,2\n1,3\n3,4\n3,5"
        root = "1"
        
        result1 = task(csv_string, root)
        result2 = task(csv_string, root)
        
        assert result1 == result2
    
    def test_order_independence(self):
        """Порядок рёбер в CSV не должен влиять на результат"""
        csv1 = "1,2\n1,3\n3,4\n3,5"
        csv2 = "3,4\n1,2\n3,5\n1,3"
        root = "1"
        
        result1 = task(csv1, root)
        result2 = task(csv2, root)
        
        assert result1 == result2


class TestComplexTrees:
    """Тесты на сложных деревьях"""
    
    def test_medium_tree(self):
        """Тест на дереве среднего размера"""
        csv_string = "1,2\n1,3\n1,4\n2,5\n2,6\n3,7\n3,8\n4,9\n4,10"
        root = "1"
        entropy, normalized = task(csv_string, root)
        
        assert entropy > 0
        assert normalized > 0
    
    def test_unbalanced_tree(self):
        """Тест на несбалансированном дереве"""
        csv_string = "1,2\n2,3\n3,4\n3,5\n3,6\n3,7"
        root = "1"
        entropy, normalized = task(csv_string, root)
        
        assert entropy > 0
        assert normalized > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
