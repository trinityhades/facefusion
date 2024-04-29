from typing import Tuple, Optional, List, Dict
from time import sleep
import gradio
from argparse import ArgumentParser, HelpFormatter
import os
import facefusion.globals
import facefusion.choices
from facefusion.uis.components import refresh
from facefusion import process_manager, wording
from facefusion.core import conditional_process
from facefusion.config import get_config
from facefusion.memory import limit_system_memory
from facefusion.normalizer import normalize_output_path
from facefusion.uis.core import get_ui_component, register_ui_component
from facefusion.filesystem import clear_temp, is_image, is_video, list_directory
CONFIG_SAVE_DROPDOWN: Optional[gradio.Dropdown] = None
CONFIG_SAVE_BUTTON: Optional[gradio.Button] = None
CONFIG_SAVE_TEXTBOX: Optional[gradio.Textbox] = None
CONFIG_DEBUG_BUTTON: Optional[gradio.Button] = None
OUTPUT_PATH_TEXTBOX: Optional[gradio.Textbox] = None

saved_config_options = ['FaceFusion.ini']
config_files_path = list_directory('configs')
print(config_files_path)
OUTPUT_PATH_TEXTBOX = gradio.Textbox(
		label = wording.get('uis.output_path_textbox'),
		value = facefusion.globals.output_path,
		max_lines = 1
	)
def render():
    global CONFIG_DEBUG_BUTTON, CONFIG_SAVE_DROPDOWN, CONFIG_SAVE_TEXTBOX, CONFIG_SAVE_BUTTON
    CONFIG_DEBUG_BUTTON = gradio.Button(value = 'DEBUG', 
                                        variant = 'secondary', 
                                        size =  'sm')
    CONFIG_SAVE_DROPDOWN = gradio.Dropdown(label = 'CONFIG DROPDOWN',
                                           choices = config_files_path, 
                                           value = facefusion.globals.active_config_file)
    CONFIG_SAVE_TEXTBOX = gradio.Textbox(label = 'CONFIG FILE', 
                                         value = '', 
                                         max_lines = 1
                                         )
    CONFIG_SAVE_BUTTON = gradio.Button(value = 'Launch With New Config',
                                       variant = 'primary',
                                       size = 'sm')
    register_ui_component('config_save_textbox', CONFIG_SAVE_TEXTBOX)
    register_ui_component('config_save_button', CONFIG_SAVE_BUTTON)
    register_ui_component('config_save_buttondropdown', CONFIG_SAVE_DROPDOWN)
    


def listen():
    CONFIG_SAVE_DROPDOWN.change(update_active_config_file,
                                inputs = CONFIG_SAVE_DROPDOWN)
    CONFIG_SAVE_TEXTBOX.change(update_config_name,
                               inputs = CONFIG_SAVE_TEXTBOX)
    CONFIG_SAVE_TEXTBOX.submit(update_saved_config_options,
                             inputs = [CONFIG_SAVE_TEXTBOX],
                             outputs = [CONFIG_SAVE_DROPDOWN])
    CONFIG_SAVE_BUTTON.click(relaunch)
    CONFIG_DEBUG_BUTTON.click(print(config_files_path))


def update_config_name(CONFIG_SAVE_TEXTBOX = None):
    facefusion.globals.textbox = CONFIG_SAVE_TEXTBOX
    print('textbox: ' + facefusion.globals.textbox)


def update_active_config_file(active_config_file = str):
    facefusion.globals.active_config_file = active_config_file
    print('active config: ' + facefusion.globals.active_config_file)
    active_config_file_with_extension = active_config_file + '.ini'
    facefusion.globals.config_path = active_config_file_with_extension
    print(active_config_file_with_extension)
    refresh.apply_config(active_config_file_with_extension)
    OUTPUT_PATH_TEXTBOX = gradio.Textbox(
		label = wording.get('uis.output_path_textbox'),
		value = facefusion.globals.output_path,
		max_lines = 1
	)
    register_ui_component('output_path_textbox', OUTPUT_PATH_TEXTBOX)
    
    

def update_saved_config_options(category = None):
    #config_files_path.append(facefusion.globals.textbox)
    create_new_config_file(facefusion.globals.textbox + '.ini')
    update_active_config_file(facefusion.globals.textbox)
    #update_dropdown()
    #update_textbox()
    options = list_directory('configs')
    return gradio.Dropdown(choices = options, value = facefusion.globals.textbox, interactive = True)

def relaunch():
    refresh.run()

def update_textbox():
    return gradio.Textbox(value = '')

def update_dropdown():
    options = list_directory('configs')
    return gradio.Dropdown(choices = options, interactive = True)

def create_new_config_file(filename: str) -> None:
    config = get_config()
    config_dir = 'configs'
    os.makedirs(config_dir, exist_ok=True)
    filepath = os.path.join(config_dir, filename)
    # Write the configuration to a file
    with open(filepath, 'w') as configfile:
        config.write(configfile)
    print(f"New config file '{filename}' created successfully.")

def update_all_globals():
    refresh.run()
