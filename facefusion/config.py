from configparser import ConfigParser
from typing import Any, Optional, List

import facefusion.globals
from facefusion.execution import encode_execution_providers
from facefusion.processors.frame import globals as frame_processors_globals

CONFIG = None


def get_config() -> ConfigParser:
	global CONFIG

	if CONFIG is None:
		CONFIG = ConfigParser()
		CONFIG.read(facefusion.globals.config_path, encoding = 'utf-8')
	return CONFIG


def write_config(filename: str) -> None:
	config = get_config()
	with open(filename, 'w') as configfile:
		config.write(configfile)


def save_config(filename: str) -> None:
	config = get_config()
	if not filename:
		filename = facefusion.globals.config_path
	if not filename.endswith('.ini'):
		filename = filename + '.ini'
	for section in config.sections():
		for key in config.options(section):
			value = None
			if hasattr(facefusion.globals, key):
				value = getattr(facefusion.globals, key)
			if hasattr(frame_processors_globals, key):
				value = getattr(frame_processors_globals, key)
			if key == 'execution_providers':
				value = encode_execution_providers(value)
			if isinstance(value, (list, tuple)):
				value = ' '.join(map(str, value))
			if value:
				config.set(section, key, str(value))
			else:
				config.set(section, key, '')
	write_config(filename)


def clear_config() -> None:
	global CONFIG

	CONFIG = None


def get_str_value(key : str, fallback : Optional[str] = None) -> Optional[str]:
	value = get_value_by_notation(key)

	if value or fallback:
		return str(value or fallback)
	return None


def get_int_value(key : str, fallback : Optional[str] = None) -> Optional[int]:
	value = get_value_by_notation(key)

	if value or fallback:
		return int(value or fallback)
	return None


def get_float_value(key : str, fallback : Optional[str] = None) -> Optional[float]:
	value = get_value_by_notation(key)

	if value or fallback:
		return float(value or fallback)
	return None


def get_bool_value(key : str, fallback : Optional[str] = None) -> Optional[bool]:
	value = get_value_by_notation(key)

	if value == 'True' or fallback == 'True':
		return True
	if value == 'False' or fallback == 'False':
		return False
	return None


def get_str_list(key : str, fallback : Optional[str] = None) -> Optional[List[str]]:
	value = get_value_by_notation(key)

	if value or fallback:
		return [ str(value) for value in (value or fallback).split(' ') ]
	return None


def get_int_list(key : str, fallback : Optional[str] = None) -> Optional[List[int]]:
	value = get_value_by_notation(key)

	if value or fallback:
		return [ int(value) for value in (value or fallback).split(' ') ]
	return None


def get_float_list(key : str, fallback : Optional[str] = None) -> Optional[List[float]]:
	value = get_value_by_notation(key)

	if value or fallback:
		return [ float(value) for value in (value or fallback).split(' ') ]
	return None


def get_value_by_notation(key : str) -> Optional[Any]:
	config = get_config()

	if '.' in key:
		section, name = key.split('.')
		if section in config and name in config[section]:
			return config[section][name]
	if key in config:
		return config[key]
	return None
