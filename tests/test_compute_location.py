from gobble.location import compute_location
from nose.tools import eq_

import textwrap

SOURCE = textwrap.dedent("""
I am a koala

  meow
  meow
""").strip()

def test_zero():
    eq_(compute_location(SOURCE, 0), (1, 1))

def test_one():
    eq_(compute_location(SOURCE, 2), (1, 3))

def test_second_line():
    eq_(compute_location(SOURCE, 12), (2, 1))

def test_third_line():
    eq_(compute_location(SOURCE, 13), (3, 1))

def test_third_line_end():
    eq_(compute_location(SOURCE, 18), (3, 6))

def test_fourth_line_end():
    eq_(compute_location(SOURCE, 25), (4, 6))

def test_eof():
    eq_(compute_location(SOURCE, 27), (5, 1))

def test_empty():
    eq_(compute_location('', 0), (1, 1))
