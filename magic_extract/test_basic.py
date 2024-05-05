import magic_extract


def raises_exception():
    v1 = 1
    v2 = 2
    raise ValueError('test')

# @magic_extract.decorate(launch_ipython=True)
@magic_extract.decorate()
def main():
    raises_exception()

main()


"""
python -i test_basic.py
print(v1)
print(v2)
"""
