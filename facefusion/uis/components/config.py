from typing import List, Optional, Any
import gradio
from facefusion.config import save_config
import facefusion.globals
import facefusion.choices
import facefusion.processors.frame.globals as frameglobals
import facefusion.processors.frame.choices as framechoices
from facefusion import wording

CONFIG_SAVE_BUTTON: Optional[gradio.Button] = None
CONFIG_SAVE_TEXTBOX: Optional[gradio.Textbox] = None


def render() -> None:
    global CONFIG_SAVE_TEXTBOX, CONFIG_SAVE_BUTTON
    CONFIG_SAVE_TEXTBOX = gradio.Textbox(label = wording.get('uis.config_save_textbox'),
                                         placeholder = facefusion.globals.config_path,
                                         max_lines = 1
                                         )
    CONFIG_SAVE_BUTTON = gradio.Button(value = 'SAVE',
                                       variant = 'primary',
                                       size = 'sm')
    

def listen() -> None:
    CONFIG_SAVE_BUTTON.click(save_config,inputs = CONFIG_SAVE_TEXTBOX)
    CONFIG_SAVE_BUTTON.click(fn=clear_text,inputs = CONFIG_SAVE_TEXTBOX, outputs=CONFIG_SAVE_TEXTBOX)


def clear_text(filename: str) -> None:
    save_info(filename)
    return gradio.update(value='')


def save_info(filename: str) -> None:
    gradio.Info(wording.get('config_file_saved').format(filepath = filename))
