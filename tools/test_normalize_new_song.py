#!/usr/bin/env python3
import os
import unittest
from .normalize_new_song import normalize_title

class TestNormalizeTitle(unittest.TestCase):
    def test_basic_normalization(self):
        """Test basic normalization of English titles"""
        self.assertEqual(normalize_title("My New Song"), "my-new-song")
        self.assertEqual(normalize_title("A Simple Test"), "a-simple-test")
        self.assertEqual(normalize_title("Song With Spaces"), "song-with-spaces")

    def test_special_characters(self):
        """Test handling of special characters"""
        self.assertEqual(normalize_title("¿Habrá un Mañana?"), "habra-un-manana")
        self.assertEqual(normalize_title("Aura-t-il Demain ?"), "aura-t-il-demain")
        self.assertEqual(normalize_title("Ci Sarà un Domani?"), "ci-sara-un-domani")

    def test_multiple_spaces(self):
        """Test handling of multiple spaces"""
        self.assertEqual(normalize_title("Song  With   Multiple    Spaces"), "song-with-multiple-spaces")

    def test_leading_trailing_spaces(self):
        """Test handling of leading and trailing spaces"""
        self.assertEqual(normalize_title("  Leading Spaces"), "leading-spaces")
        self.assertEqual(normalize_title("Trailing Spaces  "), "trailing-spaces")
        self.assertEqual(normalize_title("  Both  "), "both")

    def test_mixed_case(self):
        """Test handling of mixed case titles"""
        self.assertEqual(normalize_title("MiXeD CaSe"), "mixed-case")
        self.assertEqual(normalize_title("ThIs Is A TeSt"), "this-is-a-test")

    def test_special_characters_removal(self):
        """Test removal of special characters"""
        self.assertEqual(normalize_title("!@#$%^&*()"), "")
        self.assertEqual(normalize_title("Song*With*Special*Chars"), "songwithspecialchars")
        self.assertEqual(normalize_title("Song\With\Backslashes"), "songwithbackslashes")

    def test_unicode_characters(self):
        """Test handling of Unicode characters"""
        self.assertEqual(normalize_title("Tatuajes del Corazón"), "tatuajes-del-corazon")
        self.assertEqual(normalize_title("Écoute-moi"), "ecoute-moi")
        self.assertEqual(normalize_title("Über den Wolken"), "uber-den-wolken")

if __name__ == '__main__':
    unittest.main()
