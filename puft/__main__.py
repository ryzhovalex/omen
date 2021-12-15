"""
Invoke cli interface when puft executed as a script:
```py
python -m puft
```
"""
from .helpers import cli


if __name__ == "__main__":
    cli.main()