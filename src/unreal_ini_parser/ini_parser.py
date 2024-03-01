from typing import Self
from pathlib import Path
import re

from pathvalidate import is_valid_filepath

from .exceptions import KeyNotFoundException, SectionNotFoundException, KeyValueException


# converters


def _convert_bool(value: str, key: str):
    if value.lower() == "true":
        return True
    elif value.lower() == "false":
        return False
    else:
        raise KeyValueException(key, value, "value should be True or False")


def _convert_path(value: str, key: str) -> Path:
    if not is_valid_filepath(value, "auto"):
        raise KeyValueException(key, value, "value is not valid path")

    return Path(value)


def _convert_int(value: str, key: str) -> int:
    try:
        return int(value)
    except ValueError:
        raise KeyValueException(key, value, "value is not a valid integer")


def _convert_float(value: str, key: str) -> float:
    try:
        return float(value)
    except ValueError:
        raise KeyValueException(key, value, "value is not a valid float")


class IniParser():

    def __init__(self) -> None:
        self.sections = dict()

        self.paths: set[Path] = set()
        self.requirements: set[Path] = set()

        self.converters = {
            bool: _convert_bool,
            Path: _convert_path,
            int: _convert_int,
            float: _convert_float,
        }


    def read(self, path: Path | str):
        if isinstance(path, str):
            path = Path(path)

        if path in self.paths:
            return

        self.paths.add(path)
        text = path.read_text()
        self.parse(text)


    def parse(self, text: str):
        current_section_name = None

        for line in text.splitlines():
            # serarch not escaped comment symbol and remove rest of line
            res = re.search(r"^(.*?)(?<!\\)[;#].+$", line)
            if res is not None:
                line = res.group(1)

            # check for requirement add it if the path is valid
            res = re.search(r"^\s*@requires +(.+?)\s*$", line)
            if res is not None:
                requirement_strpath = res.group(1)
                if is_valid_filepath(requirement_strpath, "auto"):
                    requirement_path = Path(requirement_strpath)

                    if not requirement_path.is_file():
                        raise FileNotFoundError(f"Required file {requirement_path} does not exist")

                    self.requirements.add(requirement_path)
                else:
                    raise KeyValueException("@requires", requirement_strpath, "value is not valid path")

            # try search section
            res = re.search(r"^\s*\[(.+)\]\s*$", line)
            if res is not None:
                current_section_name = res.group(1)

                # init section if not inited
                if current_section_name not in self.sections:
                    self.sections[current_section_name] = dict()

                continue

            # try get key and value
            if "=" in line:
                k, v = (x.strip() for x in line.split("=", 1))

                if current_section_name is None:
                    raise SectionNotFoundException(current_section_name, 
                                                   f"Assigning values outside of a section is not allowed: {k}={v}")

                values = self.sections[current_section_name].setdefault(k, list())
                values.append(v)
                continue


    def get_ini_text(self):
        """converts config object to ini text"""
        lines = []
        for section, data in self.sections.items():
            lines.append(f"[{section}]")

            for key, values in data.items():
                for item in values:
                    lines.append(f"{key}={item}")
            lines.append("")
        return "\n".join(lines)


    def print_ini(self):
        print(self.get_ini_text(self.sections))


    def extend(self, other: Self):
        # iterate over "other" sections
        for section, section_data in other.sections.items():
            # search for that section in "self"
            comb_section_data = self.sections.setdefault(section, {})

            # iterate over "other" section data and add it to "self"
            for key, values in section_data.items():
                comb_values = comb_section_data.setdefault(key, [])
                comb_values.extend(values)

        # add "other" requirements and paths
        self.paths.update(other.paths)
        self.requirements.update(other.requirements)

        # remove all requirements that exist in paths
        for requirement in list(self.requirements):
            if requirement in self.paths:
                self.requirements.remove(requirement)


    def get_values[T](self, section: str, key: str,
                      convert_type: type[T] = str, default: list[T] | None = None) -> list[T]:
        data = self.sections.get(section)

        # return default value if no section or key
        try:
            if data is None:
                raise SectionNotFoundException(section)

            values = data.get(key)
            if values is None:
                raise KeyNotFoundException(key)

        except (SectionNotFoundException, KeyNotFoundException):
            if default is None:
                raise
            else:
                return default

        if convert_type is not str:
            if convert_type in self.converters:
                converter = self.converters[convert_type]
                return [converter(value, key) for value in values]
            else:
                raise TypeError(f"convert_type {convert_type} is not supported")

        return values


    def get_value[T](self, section: str, key: str,
                     convert_type: type[T] = str, default: T | None = None) -> T:
        try:
            values = self.get_values(section, key)
        except (SectionNotFoundException, KeyNotFoundException):
            if default is None:
                raise
            else:
                return default

        if values_count := len(values) > 1:
            raise KeyValueException(key, None, f"found {values_count} values, expected 1")

        value = values[0]
        if convert_type is not str:
            if convert_type in self.converters:
                converter = self.converters[convert_type]
                return converter(value, key)
            else:
                raise TypeError(f"convert_type {convert_type} is not supported")

        return value
