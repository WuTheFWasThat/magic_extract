# magic_extract

Based on https://andyljones.com/posts/post-mortem-plotting.html

```python
from magic_extract import extract

def main():
    x = 3
    extract()

main()
print(x)  # prints 3
```

```python
from magic_extract import debug

def main():
    x = 3
    raise Exception()

debug(main)
print(x)  # prints 3
```
