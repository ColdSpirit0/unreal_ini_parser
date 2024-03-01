# Unreal INI Parser

Parser for Unreal Engine config files.

## How to install

```bash
pip install unreal-ini-parser
```

## Usage example

```python
from pathlib import Path
from unreal_ini_parser import IniParser


def example_print(obj):
    print(type(obj).__name__, obj, sep=" | ")


# Create an instance of IniParser
parser = IniParser()

# read ini file
# parser.read("example.ini")

# or parse string
parser.parse("""
[MySection]
IsBool = True
Path = path/to/file
IntValue = 123
FloatValue = 123.456
JustArray = one
JustArray = two
JustArray = three
""")

# all ini data stored in sections
example_print(parser.sections)
# dict | {'MySection': {'IsBool': ['True'], 'Path': ['path/to/file'], 'JustArray': ['one', 'two', 'three']}}

# all paths that was read
# you can read more files, all data will be added to "sections"
# ini parser also supports @requires keyword to validate required ini files was parsed
example_print(parser.paths)
# set | {WindowsPath('example.ini')}

# get string value of "IsBool" key
is_bool = parser.get_value("MySection", "IsBool")
# same as:
# is_bool = parser.get_value("MySection", "IsBool", str)
example_print(is_bool)
# str | True

# get bool value of "IsBool" key
is_bool = parser.get_value("MySection", "IsBool", bool)
example_print(is_bool)
# bool | True

# get int value of "IntValue" key
int_value = parser.get_value("MySection", "IntValue", int)
example_print(int_value)
# int | 123

# get float value of "FloatValue" key
float_value = parser.get_value("MySection", "FloatValue", float)
example_print(float_value)
# float | 123.456

# get path value of "Path" key
path = parser.get_value("MySection", "Path", Path)
example_print(path)
# Path | path/to/file

# get array of "JustArray" key
# you can use type converters in this case
just_array = parser.get_values("MySection", "JustArray")
example_print(just_array)
# list | ['one', 'two', 'three']
```