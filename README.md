# magic_extract

Based on https://andyljones.com/posts/post-mortem-plotting.html

Examples run in interactive python:

```python
from magic_extract import extract

def main():
    x = 3
    extract()

main()  # raises a RunTimeError
print(x)  # prints 3
```

```python
from magic_extract import debug

def main(x):
    y = x - 2
    return x / y

debug(main, 4)  # returns 2
debug(main, 3)  # returns 3
debug(main, 2)  # raises ZeroDivisionError and extracts
print(y)  # prints 0
```

```python
from magic_extract import decorate

@decorate()
def main(x):
    y = x - 2
    return x / y

main(4)  # returns 2
main(3)  # returns 3
main(2)  # raises ZeroDivisionError and extracts
print(y)  # prints 0
```
