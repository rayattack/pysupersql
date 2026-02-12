from unittest import TestCase

from supersql.core.results import Result, Results


class TestResults(TestCase):
    def setUp(self):
        self.sample = Results([45, 56, 90, 100, 2, 10])
    def test_results_iteration(self):
        compare = []
        for s in self.sample:
            compare.append(s)
        self.assertEqual(compare[0].__, 45)
        self.assertEqual(compare[3].__, 100)

    def test_data(self):
        self.assertEqual(self.sample.data(), [45, 56, 90, 100, 2, 10])


class TestResult(TestCase):
    def setUp(self):
        self.sample = Results([{'name': 'aisha', 'age': 1}, {'name': 'khadija', 'age': 4}])
    
    def test_result_access(self):
        self.assertEqual(self.sample.cell(0, 'age'), 1)
        self.assertEqual(self.sample.cell(1, 'name'), 'khadija')

    def test_result_instantiation(self):
        row = self.sample.row(1)
        self.assertIsInstance(row, Result)
    
    def test_result(self):
        row = self.sample.row(2)
        self.assertEqual(row.name, 'khadija')

    def test_column(self):
        self.assertEqual(self.sample.column('age'), [1, 4])
        self.assertEqual(self.sample.column('name'), ['aisha', 'khadija'])

    def test_data(self):
        self.assertEqual(self.sample.data(), [{'name': 'aisha', 'age': 1}, {'name': 'khadija', 'age': 4}])

    def test_single_result_data(self):
        self.assertEqual(self.sample.row(1).data(), {'name': 'aisha', 'age': 1})

