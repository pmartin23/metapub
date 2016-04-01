import unittest

from metapub.utils import parameterize


class TestUtils(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parameterize(self):
        j = 'Muscle & Nerve'
        j_param = parameterize(j)
        assert j_param == 'Muscle+Nerve'
