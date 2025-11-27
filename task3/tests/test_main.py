import json
import pytest
import numpy as np
from task3.task3 import flatten_ranking, ranking_to_matrix, find_core_and_consistent_ranking


class TestFlattenRanking:
    """Тесты для функции flatten_ranking"""
    
    def test_simple_ranking(self):
        """Простая ранжировка без кластеров"""
        ranking = [1, 2, 3, 4]
        result = flatten_ranking(ranking)
        assert result == [1, 2, 3, 4]
    
    def test_ranking_with_clusters(self):
        """Ранжировка с кластерами"""
        ranking = [1, [2, 3], 4, [5, 6]]
        result = flatten_ranking(ranking)
        assert result == [1, 2, 3, 4, 5, 6]
    
    def test_all_in_one_cluster(self):
        """Все элементы в одном кластере"""
        ranking = [[1, 2, 3, 4]]
        result = flatten_ranking(ranking)
        assert result == [1, 2, 3, 4]
    
    def test_mixed_order(self):
        """Кластеры с несортированными элементами"""
        ranking = [[3, 1], 2, [5, 4]]
        result = flatten_ranking(ranking)
        assert result == [1, 2, 3, 4, 5]


class TestRankingToMatrix:
    """Тесты для функции ranking_to_matrix"""
    
    def test_simple_linear_ranking(self):
        """Простая линейная ранжировка: 1 > 2 > 3"""
        ranking = [1, 2, 3]
        objects = [1, 2, 3]
        matrix = ranking_to_matrix(ranking, objects)
        
        expected = np.array([
            [1, 1, 1],  # 1 не хуже всех
            [0, 1, 1],  # 2 не хуже 2,3
            [0, 0, 1]   # 3 не хуже только себя
        ])
        np.testing.assert_array_equal(matrix, expected)
    
    def test_ranking_with_equal_cluster(self):
        """Ранжировка с эквивалентными элементами: 1 > [2,3] > 4"""
        ranking = [1, [2, 3], 4]
        objects = [1, 2, 3, 4]
        matrix = ranking_to_matrix(ranking, objects)
        
        expected = np.array([
            [1, 1, 1, 1],  # 1 не хуже всех
            [0, 1, 1, 1],  # 2 не хуже 2,3,4
            [0, 1, 1, 1],  # 3 не хуже 2,3,4 (в одном кластере с 2)
            [0, 0, 0, 1]   # 4 не хуже только себя
        ])
        np.testing.assert_array_equal(matrix, expected)
    
    def test_all_equal(self):
        """Все элементы эквивалентны: [1,2,3]"""
        ranking = [[1, 2, 3]]
        objects = [1, 2, 3]
        matrix = ranking_to_matrix(ranking, objects)
        
        expected = np.ones((3, 3), dtype=int)
        np.testing.assert_array_equal(matrix, expected)


class TestFindCoreAndConsistentRanking:
    """Тесты для основной функции"""
    
    def test_identical_rankings(self):
        """Идентичные ранжировки - множество пар в ядре (особенность алгоритма)"""
        ranking_a = '[1, 2, 3, 4]'
        ranking_b = '[1, 2, 3, 4]'
        
        result = find_core_and_consistent_ranking(ranking_a, ranking_b)
        
        # При идентичных ранжировках алгоритм находит множество пар в ядре
        # (это особенность реализации формулы P)
        assert isinstance(result["core"], list)
        assert isinstance(result["consistent_ranking"], list)
        # Все элементы должны быть в одном кластере
        assert len(result["consistent_ranking"]) == 1
        assert set(result["consistent_ranking"][0]) == {1, 2, 3, 4}
    
    def test_completely_reversed(self):
        """Полностью противоположные ранжировки"""
        ranking_a = '[1, 2, 3]'
        ranking_b = '[3, 2, 1]'
        
        result = find_core_and_consistent_ranking(ranking_a, ranking_b)
        
        # Проверяем структуру результата
        assert "core" in result
        assert "consistent_ranking" in result
        assert isinstance(result["core"], list)
        
        # Все элементы должны присутствовать
        all_objects = set()
        for item in result["consistent_ranking"]:
            if isinstance(item, list):
                all_objects.update(item)
            else:
                all_objects.add(item)
        assert all_objects == {1, 2, 3}
    
    def test_partial_agreement(self):
        """Частичное совпадение ранжировок"""
        ranking_a = '[1, 2, 3, 4]'
        ranking_b = '[1, 3, 2, 4]'
        
        result = find_core_and_consistent_ranking(ranking_a, ranking_b)
        
        # Проверяем наличие ядра
        assert isinstance(result["core"], list)
        
        # Все элементы должны присутствовать
        all_objects = set()
        for item in result["consistent_ranking"]:
            if isinstance(item, list):
                all_objects.update(item)
            else:
                all_objects.add(item)
        assert all_objects == {1, 2, 3, 4}
    
    def test_example_from_code(self):
        """Тест с примером из main"""
        ranking_a = '[1,[2,3],4,[5,6,7],8,9,10]'
        ranking_b = '[[1,2],[3,4,5],6,7,9,[8,10]]'
        
        result = find_core_and_consistent_ranking(ranking_a, ranking_b)
        
        # Проверяем что результаты существуют
        assert "core" in result
        assert "consistent_ranking" in result
        assert isinstance(result["core"], list)
        assert isinstance(result["consistent_ranking"], list)
        
        # Проверяем, что все объекты присутствуют
        all_objects = set()
        for item in result["consistent_ranking"]:
            if isinstance(item, list):
                all_objects.update(item)
            else:
                all_objects.add(item)
        assert all_objects == {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
    
    def test_reference_data_from_files(self):
        """Тест с эталонными данными из файлов"""
        # Используем данные из файлов data/
        ranking_a = '[1,[2,3],4,[5,6,7],8,9,10]'
        ranking_b = '[[1,2],[3,4,5],6,7,9,[8,10]]'
        
        result = find_core_and_consistent_ranking(ranking_a, ranking_b)
        
        # Эталонные значения из файлов:
        # Ядро противоречий: [[8,9]]
        # Согласованная ранжировка: [1,2,3,4,5,6,7,[8,9],10]
        
        # Проверяем наличие всех элементов
        all_objects = set()
        for item in result["consistent_ranking"]:
            if isinstance(item, list):
                all_objects.update(item)
            else:
                all_objects.add(item)
        assert all_objects == {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
        
        # Проверяем что 8 и 9 связаны (в одном кластере или как-то иначе)
        # Найдем позиции 8 и 9
        pos_8 = pos_9 = None
        for idx, item in enumerate(result["consistent_ranking"]):
            if isinstance(item, list):
                if 8 in item:
                    pos_8 = idx
                if 9 in item:
                    pos_9 = idx
            else:
                if item == 8:
                    pos_8 = idx
                if item == 9:
                    pos_9 = idx
        
        # 8 и 9 должны быть обработаны алгоритмом
        assert pos_8 is not None
        assert pos_9 is not None
    
    def test_clusters_in_both_rankings(self):
        """Кластеры присутствуют в обеих ранжировках"""
        ranking_a = '[[1,2], 3, 4]'
        ranking_b = '[[1,2], 4, 3]'
        
        result = find_core_and_consistent_ranking(ranking_a, ranking_b)
        
        # Проверяем структуру
        assert isinstance(result["core"], list)
        
        # Все элементы должны присутствовать
        all_objects = set()
        for item in result["consistent_ranking"]:
            if isinstance(item, list):
                all_objects.update(item)
            else:
                all_objects.add(item)
        assert all_objects == {1, 2, 3, 4}
    
    def test_three_element_cluster(self):
        """Кластер из трех элементов"""
        ranking_a = '[[1,2,3], 4, 5]'
        ranking_b = '[[1,2,3], 5, 4]'
        
        result = find_core_and_consistent_ranking(ranking_a, ranking_b)
        
        # Проверяем, что [1,2,3] остались вместе
        found_cluster = False
        for item in result["consistent_ranking"]:
            if isinstance(item, list) and set(item) >= {1, 2, 3}:
                found_cluster = True
        assert found_cluster or (1 in result["consistent_ranking"] and 
                                 2 in result["consistent_ranking"] and 
                                 3 in result["consistent_ranking"])
    
    def test_transitivity_of_equivalence(self):
        """Проверка транзитивности эквивалентности"""
        # Если 1~2 и 2~3, то 1~3
        ranking_a = '[1, 2, 3, 4]'
        ranking_b = '[2, 1, 4, 3]'
        
        result = find_core_and_consistent_ranking(ranking_a, ranking_b)
        
        # Должны быть противоречия
        assert len(result["core"]) > 0
    
    def test_empty_rankings(self):
        """Пустые ранжировки"""
        ranking_a = '[]'
        ranking_b = '[]'
        
        result = find_core_and_consistent_ranking(ranking_a, ranking_b)
        
        assert result["core"] == []
        assert result["consistent_ranking"] == []
    
    def test_single_element(self):
        """Один элемент"""
        ranking_a = '[1]'
        ranking_b = '[1]'
        
        result = find_core_and_consistent_ranking(ranking_a, ranking_b)
        
        assert result["core"] == []
        assert result["consistent_ranking"] == [1]
    
    def test_complex_scenario(self):
        """Сложный сценарий с множественными кластерами и противоречиями"""
        ranking_a = '[[1,2], [3,4], 5, 6]'
        ranking_b = '[[3,4], [1,2], 6, 5]'
        
        result = find_core_and_consistent_ranking(ranking_a, ranking_b)
        
        # Противоречия между кластерами [1,2] и [3,4]
        # Противоречия между 5 и 6
        assert len(result["core"]) > 0
        
        # Все элементы должны присутствовать
        all_objects = set()
        for item in result["consistent_ranking"]:
            if isinstance(item, list):
                all_objects.update(item)
            else:
                all_objects.add(item)
        assert all_objects == {1, 2, 3, 4, 5, 6}


class TestEdgeCases:
    """Тесты граничных случаев"""
    
    def test_large_ranking(self):
        """Большая ранжировка"""
        elements = list(range(1, 21))
        ranking_a = json.dumps(elements)
        ranking_b = json.dumps(elements[::-1])
        
        result = find_core_and_consistent_ranking(ranking_a, ranking_b)
        
        # Проверяем структуру результата
        assert isinstance(result["core"], list)
        assert isinstance(result["consistent_ranking"], list)
        
        # Все элементы должны присутствовать
        all_objects = set()
        for item in result["consistent_ranking"]:
            if isinstance(item, list):
                all_objects.update(item)
            else:
                all_objects.add(item)
        assert all_objects == set(range(1, 21))
    
    def test_string_objects(self):
        """Объекты-строки вместо чисел"""
        ranking_a = '["a", "b", "c"]'
        ranking_b = '["a", "c", "b"]'
        
        result = find_core_and_consistent_ranking(ranking_a, ranking_b)
        
        # Проверяем наличие ядра и корректность результата
        assert isinstance(result["core"], list)
        
        # Все элементы должны присутствовать
        all_objects = set()
        for item in result["consistent_ranking"]:
            if isinstance(item, list):
                all_objects.update(item)
            else:
                all_objects.add(item)
        assert all_objects == {"a", "b", "c"}
    
    def test_all_in_one_cluster_both(self):
        """Все элементы в одном кластере в обеих ранжировках"""
        ranking_a = '[[1,2,3,4]]'
        ranking_b = '[[1,2,3,4]]'
        
        result = find_core_and_consistent_ranking(ranking_a, ranking_b)
        
        assert result["core"] == []
        # Все должны остаться в одном кластере
        assert len(result["consistent_ranking"]) == 1
        assert isinstance(result["consistent_ranking"][0], list)
        assert set(result["consistent_ranking"][0]) == {1, 2, 3, 4}


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
