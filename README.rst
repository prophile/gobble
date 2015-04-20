Gobble
======

.. image:: https://travis-ci.org/prophile/gobble.svg
    :target: https://travis-ci.org/prophile/gobble

Simpler Parsing in Python.

Usage
-----

.. Yes, this is a bit pants, but it'll go into Sphinx eventually. Maybe.

.. code:: python

    from gobble import *

Basic parsers:

.. code:: python

    @parser
    def natural():
        digits = yield character('0123456789').star
        return int(''.join(digits))

Alternatives:

.. code:: python

    @parser
    def literal_null():
        yield literal('NULL')
        return None

    literal = natural / literal_null

Optional elements:

.. code:: python

    @parser
    def natural():
        sign = yield character('-+').option('+')
        factor = {'-': -1, '+': 1}
        value = yield natural
        return value * factor

Sequencing with operators:

.. code:: python

    whitespace = character(' \n\r\t').star

    literal_expr = literal << whitespace

Actually running a parser:

.. code:: python

    value = literal_expr.execute(input_string)
    print(value)
