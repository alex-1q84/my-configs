from pathlib import Path

import my_configs

import unittest


class Test(unittest.TestCase):

    def test_to_user_home_dir_dot_dir(self):
        self.assertEqual(my_configs.to_user_home_dir("~+config"), Path("~/.config"))

    def test_to_user_home_dir_multi_dir(self):
        self.assertEqual(my_configs.to_user_home_dir("~+config-fish"), Path("~/.config/fish"))

    def test_to_user_home_dir_with_space_in_name(self):
        self.assertEqual(my_configs.to_user_home_dir("~+config-aa bb-cc"), Path("~/.config/aa bb/cc"))

    def test_symlink_to_user_home_dot(self):
        self.assertEqual(Path("~") / ".spacemacs", my_configs.symlink_to_user_home_dot("spacemacs.symlink"))


if __name__ == '__main__':
    unittest.main()
