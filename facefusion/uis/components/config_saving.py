from typing import Tuple, Optional, List, Dict
from time import sleep
import gradio
from argparse import ArgumentParser, HelpFormatter
from configparser import ConfigParser
from types import ModuleType
import os
from facefusion.execution import encode_execution_providers
import facefusion.globals
import facefusion.choices
import facefusion.processors.frame.globals as frameglobals
import facefusion.processors.frame.choices as framechoices
from facefusion import wording

CONFIG_SAVE_BUTTON: Optional[gradio.Button] = None
CONFIG_SAVE_TEXTBOX: Optional[gradio.Textbox] = None


def render():
    global CONFIG_SAVE_TEXTBOX, CONFIG_SAVE_BUTTON
    CONFIG_SAVE_TEXTBOX = gradio.Textbox(label = 'NEW CONFIG FILE', 
                                         value = '', 
                                         max_lines = 1
                                         )
    CONFIG_SAVE_BUTTON = gradio.Button(value = 'SAVE CONFIG',
                                       variant = 'primary',
                                       size = 'sm')
    

def listen():
    CONFIG_SAVE_BUTTON.click(create_new_config_file,inputs = CONFIG_SAVE_TEXTBOX)
    CONFIG_SAVE_BUTTON.click(fn=clear_text, outputs=CONFIG_SAVE_TEXTBOX)


def clear_text():
    return gradio.update(value='')


def save_info(filepath: str)-> None:
    gradio.Info(wording.get('config_file_saved').format(filepath = filepath))

def create_new_config_file(filename: str) -> None:
    if not filename.endswith('.ini'):
        filename = filename + '.ini'
    config_dir = 'configs'
    modules = [facefusion.globals,facefusion.choices,frameglobals,framechoices]
    os.makedirs(config_dir, exist_ok=True)
    filepath = os.path.join(config_dir, filename)
    config = new_config(modules)

    with open(filepath, 'w') as configfile:
        config.write(configfile)
    save_info(filepath)


def new_config(modules: list[ModuleType]) -> ConfigParser:
    config = ConfigParser()
    sections = {
        'general': ['source_paths', 'target_path', 'output_path'],
        'misc': ['force_download', 'skip_download', 'headless', 'log_level'],
        'execution': ['execution_providers', 'execution_thread_count', 'execution_queue_count'],
        'memory': ['video_memory_strategy', 'system_memory_limit'],
        'face_analyser': ['face_analyser_order', 'face_analyser_age', 'face_analyser_gender', 
                        'face_detector_model', 'face_detector_size', 'face_detector_score', 
                        'face_landmarker_score'],
        'face_selector': ['face_selector_mode', 'reference_face_position', 'reference_face_distance', 
                        'reference_frame_number'],
        'face_mask': ['face_mask_types', 'face_mask_blur', 'face_mask_padding', 'face_mask_regions'],
        'frame_extraction': ['trim_frame_start', 'trim_frame_end', 'temp_frame_format', 'keep_temp'],
        'output_creation': ['output_image_quality', 'output_image_resolution', 'output_video_encoder', 
                            'output_video_preset', 'output_video_quality', 'output_video_resolution', 
                            'output_video_fps', 'skip_audio'],
        'frame_processors': ['frame_processors', 'face_debugger_items', 'face_enhancer_model', 
                            'face_enhancer_blend', 'face_swapper_model', 'frame_colorizer_model', 
                            'frame_colorizer_blend', 'frame_colorizer_size', 'frame_enhancer_model', 
                            'frame_enhancer_blend', 'lip_syncer_model'],
        'uis': ['ui_layouts']
    }

    for module in modules:
        for section, variables in sections.items():
            if section not in config:
                config[section] = {}
            for key in variables:
                try:
                    value = getattr(module, key)
                except AttributeError:
                    continue  # Skip attributes not found in the module
                if value is not None:
                    if key == 'execution_providers':
                        value = ' '.join(encode_execution_providers(value))
                    config[section][key] = format_value(value)
                else:
                    config[section][key] = ''
    return config

def format_value(value) -> str:
    if isinstance(value, list):
        return ' '.join(map(str, value))
        
    elif isinstance(value, Tuple):
        return ' '.join(map(str, value))
    else:
        return str(value)

def create_config_from_globals_module(module) -> ConfigParser:
    config = ConfigParser()
    sections = {
        'general': ['source_paths', 'target_path', 'output_path'],
        'misc': ['force_download', 'skip_download', 'headless', 'log_level'],
        'execution': ['execution_providers', 'execution_thread_count', 'execution_queue_count'],
        # Add more sections and variables as needed
    }
    
    for section, variables in sections.items():
        config[section] = {}
        for var in variables:
            value = getattr(module, var)
            if value is not None:
                config[section][var] = str(value)
    return config
