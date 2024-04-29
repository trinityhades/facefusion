import multiprocessing
import gradio
import os
from configparser import ConfigParser
from argparse import ArgumentParser, HelpFormatter
from facefusion import content_analyser, face_analyser, face_masker, voice_extractor
from facefusion.execution import decode_execution_providers
from facefusion.filesystem import is_image, is_video, list_directory
from facefusion.memory import limit_system_memory
from facefusion.normalizer import normalize_fps, normalize_padding
from facefusion.processors.frame.core import get_frame_processors_modules, load_frame_processor_module
import facefusion.uis.components
import facefusion.uis.core as ui
import facefusion.globals
import facefusion.choices 
from facefusion.core import apply_args, conditional_process, force_download, validate_args,pre_check
from facefusion.vision import create_image_resolutions, create_video_resolutions, detect_image_resolution, detect_video_fps, detect_video_resolution, pack_resolution
def apply_config(config_file_name: str) -> None:
	config_dir = 'configs'  # Subdirectory name
	config_path = os.path.join(config_dir, config_file_name)
	config = ConfigParser()
	config.read(config_path, encoding = 'utf-8')
	#General
	facefusion.globals.source_paths = config['general']['source_paths']
	facefusion.globals.target_path = config['general']['target_path']
	facefusion.globals.output_path = config['general']['output_path']
    # misc
	facefusion.globals.force_download = config['misc']['force_download']
	facefusion.globals.skip_download = config['misc']['skip_download']
	facefusion.globals.headless = config['misc']['headless']
	facefusion.globals.log_level = config['misc']['log_level']
	# execution
	facefusion.globals.execution_providers = decode_execution_providers(config['execution']['execution_providers'])
	facefusion.globals.execution_thread_count = config['execution']['execution_thread_count']
	facefusion.globals.execution_queue_count = config['execution']['execution_queue_count']
	# memory
	facefusion.globals.video_memory_strategy = config['memory']['video_memory_strategy']
	facefusion.globals.system_memory_limit = config['memory']['system_memory_limit']
	# face analyser
	facefusion.globals.face_analyser_order = config['face_analyser']['face_analyser_order']
	facefusion.globals.face_analyser_age = config['face_analyser']['face_analyser_age']
	facefusion.globals.face_analyser_gender = config['face_analyser']['face_analyser_gender']
	facefusion.globals.face_detector_model = config['face_analyser']['face_detector_model']
	#if config['face_analyser']['face_detector_size'] in facefusion.choices.face_detector_set[config['face_analyser']['face_detector_model']]:
	#	facefusion.globals.face_detector_size = config['face_analyser']['face_detector_size']
	#else:
	#	facefusion.globals.face_detector_size = '640x640'
	facefusion.globals.face_detector_score = config['face_analyser']['face_detector_score']
	facefusion.globals.face_landmarker_score = config['face_analyser']['face_landmarker_score']
	# face selector
	facefusion.globals.face_selector_mode = config['face_selector']['face_selector_mode']
	facefusion.globals.reference_face_position = config['face_selector']['reference_face_position']
	facefusion.globals.reference_face_distance = config['face_selector']['reference_face_distance']
	facefusion.globals.reference_frame_number = config['face_selector']['reference_frame_number']
	# face mask
	facefusion.globals.face_mask_types = config['face_mask']['face_mask_types']
	facefusion.globals.face_mask_blur = config['face_mask']['face_mask_blur']
	facefusion.globals.face_mask_padding = normalize_padding(config['face_mask']['face_mask_padding'])
	facefusion.globals.face_mask_regions = config['face_mask']['face_mask_regions']
	# frame extraction
	facefusion.globals.trim_frame_start = config['frame_extraction']['trim_frame_start']
	facefusion.globals.trim_frame_end = config['frame_extraction']['trim_frame_end']
	facefusion.globals.temp_frame_format = config['frame_extraction']['temp_frame_format']
	facefusion.globals.keep_temp = config['frame_extraction']['keep_temp']
	# output creation
	facefusion.globals.output_image_quality = config['output_creation']['output_image_quality']
	if is_image(config['general']['target_path']):
		output_image_resolution = detect_image_resolution(config['general']['target_path'])
		output_image_resolutions = create_image_resolutions(output_image_resolution)
		if config['output_creation']['output_image_resolution'] in output_image_resolutions:
			facefusion.globals.output_image_resolution = config['output_creation']['output_image_resolution']
		else:
			facefusion.globals.output_image_resolution = pack_resolution(output_image_resolution)
	facefusion.globals.output_video_encoder = config['output_creation']['output_video_encoder']
	facefusion.globals.output_video_preset = config['output_creation']['output_video_preset']
	facefusion.globals.output_video_quality = config['output_creation']['output_video_quality']
	if is_video(config['general']['target_path']):
		output_video_resolution = detect_video_resolution(config['general']['target_path'])
		output_video_resolutions = create_video_resolutions(output_video_resolution)
		if config['output_creation']['output_video_resolution'] in output_video_resolutions:
			facefusion.globals.output_video_resolution = config['output_creation']['output_video_resolution']
		else:
			facefusion.globals.output_video_resolution = pack_resolution(output_video_resolution)
	if config['output_creation']['output_video_fps'] or is_video(config['general']['target_path']):
		facefusion.globals.output_video_fps = normalize_fps(config['output_creation']['output_video_fps']) or detect_video_fps(config['general']['target_path'])
	facefusion.globals.skip_audio = config['output_creation']['skip_audio']
	# frame processors
	available_frame_processors = list_directory('facefusion/processors/frame/modules')
	facefusion.globals.frame_processors = config['frame_processors']['frame_processors']
	for frame_processor in available_frame_processors:
		frame_processor_module = load_frame_processor_module(frame_processor)
		#frame_processor_module.apply_args(program)
	print(facefusion.globals.output_path)
	
def run() -> None:

	if facefusion.globals.system_memory_limit and int(facefusion.globals.system_memory_limit) > 0:
		limit_system_memory(facefusion.globals.system_memory_limit)
	if facefusion.globals.force_download:
		force_download()
		return
	if not pre_check() or not content_analyser.pre_check() or not face_analyser.pre_check() or not face_masker.pre_check() or not voice_extractor.pre_check():
		return
	for frame_processor_module in get_frame_processors_modules(facefusion.globals.frame_processors):
		if not frame_processor_module.pre_check():
			return
	if facefusion.globals.headless:
		conditional_process()
	else:
		import facefusion.uis.core as ui

		for ui_layout in ui.get_ui_layouts_modules(facefusion.globals.ui_layouts):
			if not ui_layout.pre_check():
				return
		ui.launch()	