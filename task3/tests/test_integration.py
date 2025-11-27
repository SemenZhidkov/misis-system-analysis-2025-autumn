"""
Интеграционные тесты для проверки работы с реальными данными
"""
import json
import pytest
from main import find_core_and_consistent_ranking


class TestIntegrationWithFiles:
    """Интеграционные тесты с данными из файлов"""
    
    def test_load_from_json_files(self):
        """Проверка загрузки данных из JSON файлов"""
        # Читаем данные из файлов
        with open('data/Ранжировка  A.json', 'r', encoding='utf-8') as f:
            ranking_a_data = json.load(f)
        
        with open('data/Ранжировка  B.json', 'r', encoding='utf-8') as f:
            ranking_b_data = json.load(f)
        
        # Преобразуем обратно в строки для функции
        ranking_a = json.dumps(ranking_a_data)
        ranking_b = json.dumps(ranking_b_data)
        
        result = find_core_and_consistent_ranking(ranking_a, ranking_b)
        
        # Проверяем структуру
        assert "core" in result
        assert "consistent_ranking" in result
        
        # Проверяем сохранность данных
        all_objects = set()
        for item in result["consistent_ranking"]:
            if isinstance(item, list):
                all_objects.update(item)
            else:
                all_objects.add(item)
        
        expected_objects = set(range(1, 11))  # {1, 2, ..., 10}
        assert all_objects == expected_objects


class TestPropertyBased:
    """Тесты на основе свойств (property-based testing)"""
    
    def test_all_elements_preserved(self):
        """Проверка: все элементы сохраняются"""
        test_cases = [
            ('[1, 2, 3]', '[3, 2, 1]'),
            ('[1, [2, 3], 4]', '[[1, 2], 3, 4]'),
            ('[[1, 2, 3, 4]]', '[1, 2, 3, 4]'),
            ('[1]', '[1]'),
        ]
        
        for ranking_a, ranking_b in test_cases:
            result = find_core_and_consistent_ranking(ranking_a, ranking_b)
            
            # Собираем все элементы из входных данных
            input_a = json.loads(ranking_a)
            input_b = json.loads(ranking_b)
            
            expected = set()
            for item in input_a:
                if isinstance(item, list):
                    expected.update(item)
                else:
                    expected.add(item)
            
            # Собираем все элементы из результата
            actual = set()
            for item in result["consistent_ranking"]:
                if isinstance(item, list):
                    actual.update(item)
                else:
                    actual.add(item)
            
            assert actual == expected, f"Failed for {ranking_a} vs {ranking_b}"
    
    def test_result_is_valid_ranking(self):
        """Проверка: результат является валидной ранжировкой"""
        ranking_a = '[1, 2, 3, 4, 5]'
        ranking_b = '[5, 4, 3, 2, 1]'
        
        result = find_core_and_consistent_ranking(ranking_a, ranking_b)
        
        # Проверяем что результат - это список
        assert isinstance(result["consistent_ranking"], list)
        
        # Проверяем что нет дубликатов
        all_elements = []
        for item in result["consistent_ranking"]:
            if isinstance(item, list):
                all_elements.extend(item)
            else:
                all_elements.append(item)
        
        assert len(all_elements) == len(set(all_elements)), "Дубликаты в результате!"
    
    def test_symmetry_property(self):
        """Проверка симметричности: swap(A, B) должен давать схожий результат"""
        ranking_a = '[1, 2, 3]'
        ranking_b = '[3, 2, 1]'
        
        result_ab = find_core_and_consistent_ranking(ranking_a, ranking_b)
        result_ba = find_core_and_consistent_ranking(ranking_b, ranking_a)
        
        # Элементы должны быть те же
        elements_ab = set()
        for item in result_ab["consistent_ranking"]:
            if isinstance(item, list):
                elements_ab.update(item)
            else:
                elements_ab.add(item)
        
        elements_ba = set()
        for item in result_ba["consistent_ranking"]:
            if isinstance(item, list):
                elements_ba.update(item)
            else:
                elements_ba.add(item)
        
        assert elements_ab == elements_ba
    
    def test_idempotence(self):
        """Проверка идемпотентности: применение дважды не должно менять результат"""
        ranking_a = '[1, 2, 3, 4]'
        ranking_b = '[1, 3, 2, 4]'
        
        result1 = find_core_and_consistent_ranking(ranking_a, ranking_b)
        
        # Используем результат как новую ранжировку A
        consistent = json.dumps(result1["consistent_ranking"])
        
        # "Согласование" с самим собой должно дать тот же результат
        result2 = find_core_and_consistent_ranking(consistent, consistent)
        
        # Элементы должны быть те же
        elements1 = set()
        for item in result1["consistent_ranking"]:
            if isinstance(item, list):
                elements1.update(item)
            else:
                elements1.add(item)
        
        elements2 = set()
        for item in result2["consistent_ranking"]:
            if isinstance(item, list):
                elements2.update(item)
            else:
                elements2.add(item)
        
        assert elements1 == elements2


class TestPerformance:
    """Тесты производительности"""
    
    def test_medium_size_ranking(self):
        """Тест на средних данных (50 элементов)"""
        elements = list(range(1, 51))
        ranking_a = json.dumps(elements)
        ranking_b = json.dumps(elements[::-1])
        
        result = find_core_and_consistent_ranking(ranking_a, ranking_b)
        
        # Проверяем что все элементы сохранились
        all_objects = set()
        for item in result["consistent_ranking"]:
            if isinstance(item, list):
                all_objects.update(item)
            else:
                all_objects.add(item)
        
        assert all_objects == set(elements)
    
    def test_many_clusters(self):
        """Тест с множеством кластеров"""
        # Создаем ранжировку с 10 кластерами по 3 элемента
        clusters_a = [[i*3+1, i*3+2, i*3+3] for i in range(10)]
        clusters_b = [cluster[::-1] for cluster in clusters_a[::-1]]
        
        ranking_a = json.dumps(clusters_a)
        ranking_b = json.dumps(clusters_b)
        
        result = find_core_and_consistent_ranking(ranking_a, ranking_b)
        
        # Все 30 элементов должны присутствовать
        all_objects = set()
        for item in result["consistent_ranking"]:
            if isinstance(item, list):
                all_objects.update(item)
            else:
                all_objects.add(item)
        
        assert all_objects == set(range(1, 31))


class TestErrorHandling:
    """Тесты обработки ошибок"""
    
    def test_invalid_json(self):
        """Проверка обработки невалидного JSON"""
        ranking_a = '[1, 2, 3'  # Невалидный JSON
        ranking_b = '[1, 2, 3]'
        
        with pytest.raises(json.JSONDecodeError):
            find_core_and_consistent_ranking(ranking_a, ranking_b)
    
    def test_mismatched_elements(self):
        """Проверка с разными наборами элементов (должно работать)"""
        ranking_a = '[1, 2, 3]'
        ranking_b = '[1, 2, 3, 4]'  # Дополнительный элемент
        
        # Функция использует flatten_ranking(ranking_a) для определения объектов
        # Поэтому элемент 4 будет проигнорирован
        result = find_core_and_consistent_ranking(ranking_a, ranking_b)
        
        all_objects = set()
        for item in result["consistent_ranking"]:
            if isinstance(item, list):
                all_objects.update(item)
            else:
                all_objects.add(item)
        
        # Должны быть только элементы из ranking_a
        assert all_objects == {1, 2, 3}


class TestSpecialCases:
    """Тесты специальных случаев"""
    
    def test_nested_clusters_same_size(self):
        """Кластеры одинакового размера"""
        ranking_a = '[[1, 2], [3, 4], [5, 6]]'
        ranking_b = '[[5, 6], [3, 4], [1, 2]]'
        
        result = find_core_and_consistent_ranking(ranking_a, ranking_b)
        
        all_objects = set()
        for item in result["consistent_ranking"]:
            if isinstance(item, list):
                all_objects.update(item)
            else:
                all_objects.add(item)
        
        assert all_objects == {1, 2, 3, 4, 5, 6}
    
    def test_alternating_pattern(self):
        """Чередующийся паттерн: 1,2,3,4,5 vs 2,1,4,3,5"""
        ranking_a = '[1, 2, 3, 4, 5]'
        ranking_b = '[2, 1, 4, 3, 5]'
        
        result = find_core_and_consistent_ranking(ranking_a, ranking_b)
        
        # 5 должна остаться на своем месте (согласована в обеих)
        # 1,2 и 3,4 должны быть обработаны как противоречивые пары
        all_objects = set()
        for item in result["consistent_ranking"]:
            if isinstance(item, list):
                all_objects.update(item)
            else:
                all_objects.add(item)
        
        assert all_objects == {1, 2, 3, 4, 5}
    
    def test_progressive_clustering(self):
        """Прогрессивная кластеризация"""
        ranking_a = '[1, 2, 3, 4, 5, 6]'
        ranking_b = '[[1, 2], [3, 4], [5, 6]]'
        
        result = find_core_and_consistent_ranking(ranking_a, ranking_b)
        
        all_objects = set()
        for item in result["consistent_ranking"]:
            if isinstance(item, list):
                all_objects.update(item)
            else:
                all_objects.add(item)
        
        assert all_objects == {1, 2, 3, 4, 5, 6}


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
