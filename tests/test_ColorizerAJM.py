import unittest
from pathlib import Path
import json
import io
from contextlib import redirect_stdout

from ColorizerAJM import Colorizer
from ColorizerAJM.color_converter import ColorConverter, TqdmMixin
from ColorizerAJM.errs import InvalidColorInputError, InvalidColorCodeError
from ColorizerAJM.custom_colors import CustomColorColorizer


class TestColorizer(unittest.TestCase):

    def setUp(self):
        self.colorizer = Colorizer()

    @classmethod
    def tearDownClass(cls):
        if Colorizer.DEFAULT_CUSTOM_COLOR_FILE_PATH.is_file():
            Colorizer.DEFAULT_CUSTOM_COLOR_FILE_PATH.unlink()

    def test_colorize(self):
        colored_text = self.colorizer.colorize('Hello World', 'RED')
        self.assertTrue(colored_text.startswith(self.colorizer.DEFAULT_COLOR_CODES['RED']))

    def test_custom_colors(self):
        self.colorizer = Colorizer(custom_colors={'MY_COLOR': 123})
        self.assertEqual(self.colorizer.custom_colors, {'MY_COLOR': '\x1b[38;5;123m'})

    def test_all_loaded_colors(self):
        self.assertIsNotNone(self.colorizer.all_loaded_colors)

    def test_random_color(self):
        color = Colorizer.random_color()
        self.assertTrue(color.startswith(self.colorizer.CUSTOM_COLOR_PREFIX))

    def test_print_color(self):
        self.assertIsNone(self.colorizer.print_color('Test', color='BLUE'))

    def test_preview_color_id(self):
        self.assertIsNone(self.colorizer.preview_color_id(50))

    def test_print_color_table(self):
        self.assertIsNone(self.colorizer.print_color_table(10))

    def test_stringify_color_id(self):
        s = Colorizer.stringify_color_id((255, 255, 255))
        self.assertEqual(s, "\x1b[38;2;255;255;255m")

    def test__parse_color_string(self):
        s = self.colorizer._parse_color_string('RED')
        self.assertEqual(s, self.colorizer.DEFAULT_COLOR_CODES['RED'])

    def test_get_color_code(self):
        code = self.colorizer.get_color_code('RED')
        self.assertEqual(code, self.colorizer.DEFAULT_COLOR_CODES['RED'])

    def test_base_colorizer_init(self):
        c = Colorizer(ignore_invalid_colors=True)
        self.assertTrue(c.ignore_invalid_colors)

    def test_stringify_color_id_errors(self):
        with self.assertRaises(InvalidColorCodeError):
            Colorizer.stringify_color_id(256)
        with self.assertRaises(InvalidColorCodeError):
            Colorizer.stringify_color_id((256, 0, 0))
        with self.assertRaises(InvalidColorCodeError):
            Colorizer.stringify_color_id((0, 0))
        with self.assertRaises(ValueError):
            Colorizer.stringify_color_id("not an int or tuple")

    def test_parse_color_string_invalid(self):
        # Case where it returns empty string when ignoring invalid colors
        c = Colorizer(ignore_invalid_colors=True)
        self.assertEqual(c._parse_color_string("INVALID_COLOR"), "")

        # Case where it raises error when not ignoring
        with self.assertRaises(InvalidColorCodeError):
            self.colorizer._parse_color_string("INVALID_COLOR")

    def test_get_color_code_variations(self):
        # Dict variation
        code = self.colorizer.get_color_code({"RED": 1})
        self.assertEqual(code, Colorizer.CUSTOM_COLOR_PREFIX + "1" + Colorizer.COLOR_SUFFIX)

        # Empty dict
        with self.assertRaises(ValueError):
            self.colorizer.get_color_code({})

        # Int variation
        with self.assertRaises(InvalidColorCodeError):
            self.colorizer.get_color_code(1)

        # Attribute Error
        with self.assertRaises(AttributeError):
            self.colorizer.get_color_code(1.5)

    def test_colorizer_init_with_file(self):
        test_file = Path("test_colors.json")
        with open(test_file, "w") as f:
            json.dump({"TEST_BLUE": 4}, f)

        try:
            c = Colorizer(custom_color_file_path=test_file, write_custom_colors_on_init=False)
            self.assertIn("TEST_BLUE", c.custom_colors)
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_colorizer_colorize_no_color(self):
        # Should use random color
        text = self.colorizer.colorize("Hello")
        self.assertTrue(text.startswith(Colorizer.CUSTOM_COLOR_PREFIX))
        self.assertTrue(text.endswith(Colorizer.RESET_COLOR_CODE))

    def test_colorizer_print_methods(self):
        f = io.StringIO()
        with redirect_stdout(f):
            self.colorizer.print_color("Test", color="RED", bold=True)
            self.colorizer.preview_color_id(10)
            self.colorizer.print_color_table(columns=5)
            self.colorizer.pretty_print_all_loaded_colors()
            self.colorizer.example_usage()
        output = f.getvalue()
        self.assertIn("Test", output)
        self.assertIn("10", output)
        self.assertIn("All Valid Color IDs", output)


class TestCustomColorColorizer(unittest.TestCase):

    def test_custom_color_colorizer_read_write(self):
        test_file = Path("test_custom.json")
        c = CustomColorColorizer(custom_colors={"GOLD": (255, 215, 0)},
                                 custom_color_file_path=test_file,
                                 write_custom_colors_on_init=True)
        self.assertTrue(test_file.exists())

        c2 = CustomColorColorizer(custom_color_file_path=test_file, write_custom_colors_on_init=False)
        c2.read_custom_colors()
        self.assertIn("GOLD", c2.custom_colors)

        # Test invalid read
        c2.custom_color_file_path = Path("non_existent.txt")
        with self.assertRaises(AttributeError):
            c2.read_custom_colors()

        if test_file.exists():
            test_file.unlink()

    def test_custom_colors_setter(self):
        c = CustomColorColorizer(write_custom_colors_on_init=False)
        c.custom_colors = {"c1": 10, "c2": (1, 2, 3), "c3": "\033[31m"}
        self.assertEqual(c.custom_colors["C1"], Colorizer.CUSTOM_COLOR_PREFIX + "10" + Colorizer.COLOR_SUFFIX)
        self.assertEqual(c.custom_colors["C2"], Colorizer.RGBA_COLOR_PREFIX + "1;2;3" + Colorizer.COLOR_SUFFIX)
        self.assertEqual(c.custom_colors["C3"], "\033[31m")


class TestColorConverter(unittest.TestCase):

    def test_rgb_to_hex(self):
        self.assertEqual(ColorConverter.rgb_to_hex(255, 255, 255), "#ffffff")
        self.assertEqual(ColorConverter.rgb_to_hex(0, 0, 0), "#000000")

    def test_rgb_to_hex_errors(self):
        with self.assertRaises(ValueError):
            ColorConverter.rgb_to_hex(256, 0, 0)
        with self.assertRaises(ValueError):
            ColorConverter.rgb_to_hex(-1, 0, 0)

    def test_color_converter_ansi_256(self):
        # Basic ANSI
        self.assertEqual(ColorConverter.ansi_256_to_hex(1), "#800000")

        # RGB Cube
        self.assertEqual(ColorConverter.ansi_256_to_hex(16), "#000000")

        # Grayscale
        self.assertEqual(ColorConverter.ansi_256_to_hex(232), "#080808")

        # Out of range
        with self.assertRaises(ValueError):
            ColorConverter.ansi_256_to_hex(256)

    def test_color_converter_ansi_escape_to_hex(self):
        # Truecolor
        self.assertEqual(ColorConverter.ansi_escape_to_hex("\033[38;2;255;0;0m"), "#ff0000")
        self.assertEqual(ColorConverter.ansi_escape_to_hex("\033[48;2;0;255;0m"), "#00ff00")

        # 256 color
        self.assertEqual(ColorConverter.ansi_escape_to_hex("\033[38;5;16m"), "#000000")

        # Basic 16
        self.assertEqual(ColorConverter.ansi_escape_to_hex("\033[31m"), "#800000")

        # Unsupported
        with self.assertRaises(ValueError):
            ColorConverter.ansi_escape_to_hex("\033[999m")

    def test_color_converter_edge_cases(self):
        self.assertEqual(ColorConverter._calc_grayscale(100), 100)


class TestTqdmMixin(unittest.TestCase):

    def test_tqdm_mixin(self):
        class Sub(TqdmMixin):
            ANSI_OCT_ESCAPE_PREFIX = "\033"
            ANSI_HEX_ESCAPE_PREFIX = "\x1b"
            @classmethod
            def ansi_escape_to_hex(cls, ansi_escape): return "#ffffff"

        # Test to_tqdm_colour
        self.assertIsNone(Sub.to_tqdm_colour(None, allow_none=True))
        with self.assertRaises(TypeError):
            Sub.to_tqdm_colour(None, allow_none=False)

        self.assertEqual(Sub.to_tqdm_colour("\033[31m"), "#ffffff")

        # Test bar_colors
        bc = Sub.bar_colors()
        self.assertIsInstance(bc, dict)

        if bc:
            some_color = list(bc.keys())[0]
            self.assertEqual(Sub.to_tqdm_colour(some_color), some_color.upper())

        # Test invalid color
        with self.assertRaises(InvalidColorInputError):
            Sub.to_tqdm_colour("not-a-color")

    def test_tqdm_mixin_init_error(self):
        with self.assertRaises(TypeError):
            class BadSub(TqdmMixin):
                pass


if __name__ == '__main__':
    unittest.main()
