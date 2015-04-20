from gobble import *
from collections import namedtuple
from functools import reduce
from nose.tools import eq_

AddExpr = namedtuple('AddExpr', 'lhs rhs')
SubExpr = namedtuple('SubExpr', 'lhs rhs')
MulExpr = namedtuple('MulExpr', 'lhs rhs')
DivExpr = namedtuple('DivExpr', 'lhs rhs')
LitExpr = namedtuple('LitExpr', 'value')

@parser
def natural():
    digits = ''.join((yield character('0123456789').plus))
    yield whitespace
    return int(digits)

@parser
def integer():
    sign = yield character('-+').option('+')
    factor = {'+': 1, '-': -1}[sign]
    nat = yield natural
    return nat * factor

@parser
def literal_expression():
    return LitExpr(value = (yield integer))

whitespace = character(' \t\r\n').star

@parser
def additive_suffix():
    operator = yield character('+-')
    yield whitespace
    type = {'+': AddExpr, '-': SubExpr}[operator]
    next = yield mul_expression
    return lambda lhs: type(lhs=lhs, rhs=next)

@parser
def additive_expression():
    root = yield mul_expression
    suffices = yield additive_suffix.star
    return reduce(lambda l, r: r(l), suffices, root)

@parser
def mul_suffix():
    operator = yield character('*/')
    yield whitespace
    type = {'*': MulExpr, '/': DivExpr}[operator]
    next = yield base_expression
    return lambda lhs: type(lhs=lhs, rhs=next)

@parser
def mul_expression():
    root = yield base_expression
    suffices = yield mul_suffix.star
    return reduce(lambda l, r: r(l), suffices, root)

@parser
def paren_expression():
    yield character('(')
    yield whitespace
    sub = yield additive_expression
    yield character(')')
    yield whitespace
    return sub

base_expression = paren_expression / literal_expression

program = whitespace >> additive_expression

def test_exec():
    syntax_tree = program.execute('1 + (2*3 + 4)')
    eq_(syntax_tree, AddExpr(lhs=LitExpr(1),
                             rhs=AddExpr(lhs=MulExpr(lhs=LitExpr(2),
                                                     rhs=LitExpr(3)),
                                         rhs=LitExpr(4))))
