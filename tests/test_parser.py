from unreal_ini_parser import IniParser
import pytest
from pathlib import Path

from unreal_ini_parser.exceptions import SectionNotFoundException


def test_read_str():
    parser = IniParser()
    parser.parse(
        """
        [MySection]
        MyString = Hello, World!
        MyEmptyString = 
        """
    )

    assert parser.get_values("MySection", "MyString") == ["Hello, World!"]
    assert parser.get_value("MySection", "MyString") == "Hello, World!"
    assert parser.get_value("MySection", "MyEmptyString") == ""



def test_str_trim():
    parser = IniParser()
    parser.parse(
        """
        [MySection]
        MyStringWithSpaces =     Some Value     
        MyStringWithoutSpaces=AnotherValue
        """
    )

    assert parser.get_value("MySection", "MyStringWithSpaces") == "Some Value"
    assert parser.get_value("MySection", "MyStringWithoutSpaces") == "AnotherValue"


def test_read_int():
    parser = IniParser()
    parser.parse(
        """
        [MySection]
        MyPositiveInt = 123
        MyNegativeInt = -456
        MyZeroInt = 0
        """
    )

    assert isinstance(parser.get_value("MySection", "MyPositiveInt", int), int)
    assert isinstance(parser.get_value("MySection", "MyNegativeInt", int), int)
    assert isinstance(parser.get_value("MySection", "MyZeroInt", int), int)
    assert parser.get_value("MySection", "MyPositiveInt", int) == 123
    assert parser.get_value("MySection", "MyNegativeInt", int) == -456
    assert parser.get_value("MySection", "MyZeroInt", int) == 0


def test_read_float():
    parser = IniParser()
    parser.parse(
        """
        [MySection]
        MyPositiveFloat = 123.456
        MyNegativeFloat = -654.321
        MyZeroFloat = 0.0
        """
    )

    assert isinstance(parser.get_value("MySection", "MyPositiveFloat", float), float)
    assert isinstance(parser.get_value("MySection", "MyNegativeFloat", float), float)
    assert isinstance(parser.get_value("MySection", "MyZeroFloat", float), float)
    assert parser.get_value("MySection", "MyPositiveFloat", float) == 123.456
    assert parser.get_value("MySection", "MyNegativeFloat", float) == -654.321
    assert parser.get_value("MySection", "MyZeroFloat", float) == 0.0


def test_read_bool():
    parser = IniParser()
    parser.parse(
        """
        [MySection]
        MyBool = true
        MyBool2 = True
        MyBool3 = false
        MyBool4 = False
        """
    )

    assert parser.get_value("MySection", "MyBool", bool) is True
    assert parser.get_value("MySection", "MyBool2", bool) is True
    assert parser.get_value("MySection", "MyBool3", bool) is False
    assert parser.get_value("MySection", "MyBool4", bool) is False


def test_read_path_win():
    parser = IniParser()
    parser.parse(
        """
        [Paths]
        AbsolutePath = C:\\Users\\Admin\\Desktop\\MordhauProjects\\file.txt
        RelativePath = ..\\another_folder\\file.txt
        """
    )

    assert parser.get_value("Paths", "AbsolutePath", Path) == \
        Path("C:\\Users\\Admin\\Desktop\\MordhauProjects\\file.txt")
    assert parser.get_value("Paths", "RelativePath", Path) == Path("..\\another_folder\\file.txt")


def test_read_path_unix():
    parser = IniParser()
    parser.parse(
        """
        [UnixPaths]
        HomePath = /home/user
        ConfigPath = /etc/config
        """
    )

    assert parser.get_value("UnixPaths", "HomePath", Path) == Path("/home/user")
    assert parser.get_value("UnixPaths", "ConfigPath", Path) == Path("/etc/config")


def test_not_supported_converter():
    parser = IniParser()
    parser.parse(
        """
        [MySection]
        MyKey = Some value
        """
    )

    class MyType:
        ...

    with pytest.raises(TypeError):
        parser.get_value("MySection", "MyKey", MyType)


def test_get_multiple_values():
    parser = IniParser()
    parser.parse(
        """
        [MySection]
        MyKey = Value1
        MyKey = Value2
        MyKey = Value3
        """
    )

    assert parser.get_values("MySection", "MyKey") == ["Value1", "Value2", "Value3"]


def test_get_multiple_values_bool():
    parser = IniParser()
    parser.parse(
        """
        [MySection]
        MyBool = true
        MyBool = false
        MyBool = true
        """
    )

    assert parser.get_values("MySection", "MyBool", bool) == [True, False, True]


def test_get_multiple_values_path():
    parser = IniParser()
    parser.parse(
        """
        [MySection]
        MyPath = /path/to/file1
        MyPath = /path/to/file2
        MyPath = /path/to/file3
        """
    )

    assert parser.get_values("MySection", "MyPath", Path) == [Path(
        '/path/to/file1'), Path('/path/to/file2'), Path('/path/to/file3')]


def test_get_multiple_values_int():
    parser = IniParser()
    parser.parse(
        """
        [MySection]
        MyInt = 1
        MyInt = 2
        MyInt = 3
        """
    )

    assert all(isinstance(x, int) for x in parser.get_values("MySection", "MyInt", int))
    assert parser.get_values("MySection", "MyInt", int) == [1, 2, 3]


def test_get_multiple_values_float():
    parser = IniParser()
    parser.parse(
        """
        [MySection]
        MyFloat = 1.0
        MyFloat = 2.0
        MyFloat = 3.0
        """
    )

    assert all(isinstance(x, float) for x in parser.get_values("MySection", "MyFloat", float))
    assert parser.get_values("MySection", "MyFloat", float) == [1.0, 2.0, 3.0]


def test_read_from_different_sections():
    parser = IniParser()
    parser.parse(
        """
        [MySection]
        MyKey = Value1

        [MyOtherSection]
        MyKey = Value2
        """
    )

    assert parser.get_value("MySection", "MyKey") == "Value1"
    assert parser.get_value("MyOtherSection", "MyKey") == "Value2"


def test_raises_error_if_value_without_section():
    parser = IniParser()
    with pytest.raises(SectionNotFoundException):
        parser.parse(
            """
            MyKey = Value1

            [MyOtherSection]
            MyKey = Value2
            """
        )
