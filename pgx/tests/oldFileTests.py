import unittest
import os
import pygame

import pgx2 as pgx

# important note:
# tests seem to be isolated from each other, so a write test followed by a read test will not work
# because the read test will try to read where the write just happened and see nothing there


class FileTest(unittest.TestCase):

    file_start = (
        "[12, 13, 1.12382, True, string] #this is a comment\n"
        "[string, string, True, False]#another comment\n"
        "line\n"
        "line\n"
        "line\n"
        "line\n"
    )

    def setUp(self):
        file = open("pgx_test.txt", "w+")
        file.write(FileTest.file_start)
        file.close()
        self.testfile = pgx.File("pgx_test.txt")

    def test_list_write(self):
        self.testfile.set(["hello", 12], 2)

    def test_list_set(self):
        self.testfile.setElement("ingstr", 0, 1)

    def test_list_read(self):
        read_list = self.testfile.get(0)
        self.assertIsInstance(read_list[0], int)
        self.assertIsInstance(read_list[2], float)
        self.assertIsInstance(read_list[3], bool)

    def test_object_write(self):
        var = {"red": 1, "green": 2, "blue": 3}
        self.testfile.saveObj(var, 4)

    def test_object_read(self):
        var = {"red": 1, "green": 2, "blue": 3}
        self.testfile.saveObj(var, 4)
        self.assertEqual(var, self.testfile.loadObj(4))

    def test_copy_file(self):  # needs test
        pass

    def test_copy_path(self):  # needs test
        pass

    def tearDown(self):
        os.remove("pgx_test.txt")


if __name__ == "__main__":
    unittest.main()
