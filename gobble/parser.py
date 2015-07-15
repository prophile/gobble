"""Main parser implementation."""

import functools
from .location import compute_location

class ParseError(ValueError):
    """Exception class used to indicate actual errors in parsing.
    
    Takes a location for more helpful error messages.
    """
    __slots__ = ('location',)

    def __init__(self, location, message):
        """Standard constructor.
        
        `location` is a (line, column) tuple; `message` takes its usual meaning for
        exception classes.
        """
        super().__init__('{}:{}: {}'.format(location[0], location[1], message))
        self.location = location

class Parser:
    """Single parser type.
    
    A wrapper around a function from (source, index) to either raising a `ParseError` or
    returning (value, new_index).
    
    Highly composable.
    """
    __slots__ = ('parse',)

    def __init__(self, parse):
        """Construct directly with underlying parser function.
        
        You shouldn't need to do this much.
        """
        self.parse = parse

    def execute(self, source):
        """Run on source, forbidding residue.
        
        That is, if the parser does not consume the entire input, it is an error.
        """
        result, final_index = self.parse(source, 0)
        if final_index != len(source):
            location = compute_location(source, final_index)
            raise ParseError(location,
                             'Partial parse, residue is '
                             '{0!r}'.format(source[final_index:]))
        return result

    def __repr__(self):
        """Pretty-printed representation for debugging."""
        return '{}<{}>'.format(self.__class__.__name__,
                               self.parse.__name__)

    @property
    def plus(self):
        """One-or-more."""
        return _replicated(self, '+', 1)

    @property
    def star(self):
        """Zero-or-more."""
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
    """Parse from a character range.
    
    Accepts any character within the Container `character`, returning it."""
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
    """Wrapper for creating parsers from generator expressions.
    
    The function should be nullary; yield <parser> within it to parse from
    <parser>, which returns whatever the parser evaluated, or throws a
    ParseError. Letting ParseErrors escape is probably what you want in most
    cases.
    """
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
    """Parser which always errors out with the same message."""
    @parser
    def parse_error():
        loc = yield location
        raise ParseError(loc, message)
    parse_error.parse.__name__ = '<error>'
    return parse_error

def literal(value, normalize=lambda x: x):
    """Parser which accepts exactly a literal value.
    
    Pass `normalize` for a normalization stage before comparison; by default
    it's the identity function but, for instance, lambda x: x.lower() gives
    you case-insensitive matching.
    
    Returns `value` on a successful match.
    """
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
    """Alternation.
    
    Tries a; if that raises a ParseError tries b.
    
    You can also access this as parser | parser.
    """
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
    """Right-sequencing.
    
    Parses a, then parses b, then returns from b discarding the result from a.
    
    You can also access this as parser >> parser. The arrows point to
    the result.
    """
    @parser
    def parse_sequence():
        yield a
        second = yield b
        return second
    parse_sequence.parse.__name__ = a.parse.__name__ + ' ' + b.parse.__name__
    return parse_sequence

def followed_by(a, b):
    """Left-sequencing.
    
    Parses a, then parses b, then returns from a discarding the result from b.
    
    You can also access this as parser << parser. The arrows point to
    the result.
    """
    @parser
    def parse_sequence():
        first = yield a
        yield b
        return first
    parse_sequence.parse.__name__ = a.parse.__name__ + ' ' + b.parse.__name__
    return parse_sequence

def optional(a, default=None):
    """Optional a.
    
    Parses a; if that's successful returns from there; otherwise, returns the value
    of `default`.
    """
    @parser
    def parse_option():
        try:
            return (yield a)
        except ParseError:
            return default
    parse_option.parse.__name__ = '({})?'.format(a.parse.__name__)
    return parse_option

def _parse_index(_, index):
    return index, index
_parse_index.__name__ = '<index>'
_index = Parser(_parse_index)

def _replicated(a, operator, min_count):
    @parser
    def parse_replicated():
        matches = []
        try:
            while True:
                idx = yield _index
                submatch = yield a
                idx_prime = yield _index
                matches.append(submatch)
                if idx_prime == idx:
                    # `a` accepts epsilon, this will end up matching forever
                    # instead assume that's not what the user wants
                    break
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
