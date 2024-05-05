"""
NOTE: this does *not* run with pytest, just run with python
"""

from magic_extract import extract, MagicExtractError

def main():
    x = 3
    extract()

try:
    main()
except MagicExtractError as e:
    pass
assert x == 3


from magic_extract import debug

def main(x):
    y = x - 2
    return x / y

try:
    debug(main, 4)  # returns 2
    debug(main, 3)  # returns 3
    debug(main, 2)  # raises ZeroDivisionError and extracts
except MagicExtractError as e:
    pass
assert x == 2
assert y == 0


from magic_extract import decorate

@decorate()
def main_dec(x):
    y = x - 3
    return x / y

main_dec(5)  # returns 2
main_dec(4)  # returns 3
try:
    main_dec(3)  # raises ZeroDivisionError and extracts
except MagicExtractError as e:
    pass
assert x == 3
assert y == 0
