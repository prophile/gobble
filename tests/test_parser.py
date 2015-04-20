from gobble.parser import Parser, ParseError, dot, character, location, \
                          either, then, followed_by, parser, literal
from nose.tools import eq_, raises

def test_dot():
    eq_(dot.execute('a'), 'a')

@raises(ParseError)
def test_eof():
    dot.execute('')

@raises(ParseError)
def test_incomplete():
    dot.execute('ab')

def test_range():
    eq_(character('123').execute('1'), '1')

@raises(ParseError)
def test_range_outside():
    character('123').execute('4')

@raises(ParseError)
def test_range_eof():
    character('123').execute('')

def test_location():
    eq_(location.execute(''), (1, 1))

def test_either_left():
    eq_(either(character('123'),
               character('456')).execute('3'), '3')

def test_either_right():
    eq_(either(character('123'),
               character('456')).execute('4'), '4')

def test_then():
    eq_(then(dot, dot).execute('12'),
        '2')

def test_followed_by():
    eq_(followed_by(dot, dot).execute('12'),
        '1')

@raises(ParseError)
def test_either_neither():
    either(character('123'),
           character('456')).execute('7')

def test_sequence():
    @parser
    def sequence():
        a = yield dot
        b = yield dot
        c = yield dot
        return (a, b, c)
    eq_(sequence.execute('123'), ('1', '2', '3'))

def test_star():
    eq_(dot.star.execute('123'), ['1', '2', '3'])

def test_star_empty():
    eq_(dot.star.execute(''), [])

def test_star_star():
    eq_(dot.star.star.execute('1'), [['1'], []])

def test_plus():
    eq_(dot.plus.execute('123'), ['1', '2', '3'])

@raises(ParseError)
def test_plus_empty():
    dot.plus.execute('')

def test_optional_match():
    eq_(dot.option('bees').execute('1'), '1')

def test_optional_no_match():
    eq_(dot.option('bees').execute(''), 'bees')

def test_optional_default_none():
    eq_(dot.option().execute(''), None)

def test_literal():
    eq_(literal('horse').execute('horse'), 'horse')

@raises(ParseError)
def test_literal_fail():
    literal('horse').execute('')

@raises(ParseError)
def test_literal_fail_partial():
    literal('horse').execute('hors')

def test_literal_norm():
    eq_(literal('horse', normalize=lambda x: x.lower()).execute('HorSE'), 'horse')
