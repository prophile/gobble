import functools
from .location import compute_location

class ParseError(ValueError):
    __slots__ = ('location',)

    def __init__(self, location, message):
        super().__init__('{}:{}: {}'.format(location[0], location[1], message))
        self.location = location

class Parser:
    __slots__ = ('parse',)

    def __init__(self, parse):
        self.parse = parse

    def execute(self, source):
        result, final_index = self.parse(source, 0)
        if final_index != len(source):
            location = compute_location(source, final_index)
            raise ParseError(location,
                             'Partial parse, residue is '
                             '{0!r}'.format(source[final_index:]))
        return result

    def __repr__(self):
        return '{}<{}>'.format(self.__class__.__name__,
                               self.parse.__name__)

    @property
    def plus(self):
        return _replicated(self, '+', 1)

    @property
    def star(self):
        return _replicated(self, '*', 0)

def _parse_location(source, index):
    return compute_location(source, index), index
_parse_location.__name__ = '<location>'
location = Parser(_parse_location)

def _parse_dot(source, index):
    if index == len(source):
        raise ParseError(compute_location(source, index),
                         'Unexpected EOF')
    return source[index], index + 1
_parse_dot.__name__ = '.'
dot = Parser(_parse_dot)

def character(character):
    def parse_character(source, index):
        if index == len(source):
            raise ParseError(compute_location(source, index),
                             'Unexpected EOF')
        char = source[index]
        if char in character:
            return char, index + 1
        else:
            raise ParseError(compute_location(source, index),
                             'Unexpected character, expected one of '
                             '{0!r}'.format(character))
    parse_character.__name__ = '[{}]'.format(repr(character)[1:-1])
    return Parser(parse_character)

def parser(fn):
    @functools.wraps(fn)
    def parse_group(source, index):
        iterator = fn()
        try:
            subexpression = next(iterator)
            while True:
                try:
                    subvalue, index = subexpression.parse(source, index)
                except ParseError as parse_error:
                    subexpression = iterator.throw(parse_error)
                else:
                    subexpression = iterator.send(subvalue)
        except StopIteration as exception:
            return exception.value, index
    return Parser(parse_group)

def error(message):
    @parser
    def parse_error():
        loc = yield location
        raise ParseError(loc, message)
    parse_error.parse.__name__ = '<error>'
    return parse_error

def literal(value, normalize=lambda x: x):
    normalized_value = normalize(value)
    # We could do this with @parser, but this way is more efficient
    def parse_literal(source, index):
        next_index = index + len(value)
        match = source[index:next_index]
        if normalize(match) == normalized_value:
            return value, next_index
        else:
            loc = compute_location(source, index)
            raise ParseError(loc, "Expected {0!r}".format(value))
    parse_literal.__name__ = repr(value)
    return Parser(parse_literal)

def either(a, b):
    @parser
    def parse_either():
        try:
            return (yield a)
        except ParseError:
            return (yield b)
    parse_either.parse.__name__ = '({} / {})'.format(a.parse.__name__,
                                                     b.parse.__name__)
    return parse_either

def then(a, b):
    @parser
    def parse_sequence():
        yield a
        second = yield b
        return second
    parse_sequence.parse.__name__ = a.parse.__name__ + ' ' + b.parse.__name__
    return parse_sequence

def followed_by(a, b):
    @parser
    def parse_sequence():
        first = yield a
        yield b
        return first
    parse_sequence.parse.__name__ = a.parse.__name__ + ' ' + b.parse.__name__
    return parse_sequence

def optional(a, default=None):
    @parser
    def parse_option():
        try:
            return (yield a)
        except ParseError:
            return default
    parse_option.parse.__name__ = '({})?'.format(a.parse.__name__)
    return parse_option

def _replicated(a, operator, min_count):
    @parser
    def parse_replicated():
        matches = []
        try:
            while True:
                matches.append((yield a))
        except ParseError:
            pass
        if len(matches) >= min_count:
            return matches
        else:
            yield error('Not enough matches of {}'.format(a.parse.__name__))
    parse_replicated.parse.__name__ = '({}){}'.format(a.parse.__name__,
                                                      operator)
    return parse_replicated

Parser.__truediv__ = either
Parser.__rshift__ = then
Parser.__lshift__ = followed_by

Parser.option = optional
