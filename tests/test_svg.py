# -*- encoding: utf-8 -*-

from os.path import join, dirname, abspath
from unittest import TestCase

from pss.svg import QuerySvg

FILE_LOCATION = dirname(abspath(__file__))


class SvgHandlerTestCase(TestCase):
    def setUp(self):
        self.valid_path = join(FILE_LOCATION, "..", "resources", "test_query.svg")

    def test_can_create_with_correct_path(self):
        self.assertIsNotNone(QuerySvg(self.valid_path))

    def test_raise_exception_when_invalid_path_given(self):
        invalid_path = join("..", "resources", "invalid.svg")
        self.assertRaises(FileNotFoundError, QuerySvg, invalid_path)

    def test_when_valid_svg_given_names_and_symbol_group_should_not_be_empty(self):
        svg_handler = QuerySvg(self.valid_path, "Query")
        symbol_group = svg_handler.svg_symbol_groups[0]

        self.assertEqual(svg_handler.names[0], "Query")
        self.assertEqual(svg_handler.get_symbol_group_size(symbol_group), 16)


