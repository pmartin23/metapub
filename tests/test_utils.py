import unittest
from hamcrest import assert_that, is_

from metapub.utils import parameterize

class TestUtils(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parameterize(self):
        j = 'Muscle & Nerve'
        j_param = parameterize(j)
        assert_that(j_param, is_("Muscle+Nerve"))
