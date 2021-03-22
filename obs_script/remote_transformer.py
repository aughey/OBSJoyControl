import obspython as obs
import urllib.request
import urllib.error
import math
import time

import socket

# Globals (if you will)
sock = None
pansource         = ""
   


def script_tick(seconds):
	global pansource
	global sock

	if sock is None:
		return

	values = []
	data = None


	try:
		while True:
			data = sock.recv(1024)
	except Exception:
		pass

	if data is None:
		return

	data = data.decode('utf8')
	values = [float(v) for v in data.split(' ')]

	defaults = [0,0,0,0,0,0,90]
	for i in range(len(defaults)):
		if i >= len(values):
			values.append(defaults[i])

	source = obs.obs_get_source_by_name(pansource)
	if source is not None:
		filter = obs.obs_source_get_filter_by_name(source,"3D Transform")
		if filter is not None:
			filter_settings = obs.obs_source_get_settings(filter)
			obs.obs_data_set_double(
					filter_settings,
					"Filter.Transform.Rotation.X",
					values[0]
				)
			obs.obs_data_set_double(
					filter_settings,
					"Filter.Transform.Rotation.Y",
					values[1]
				)
			obs.obs_data_set_double(
					filter_settings,
					"Filter.Transform.Rotation.Z",
					values[2]
				)
			obs.obs_data_set_double(
					filter_settings,
					"Filter.Transform.Position.X",
					values[3]
				)
			obs.obs_data_set_double(
					filter_settings,
					"Filter.Transform.Position.Y",
					values[4]
				)
			obs.obs_data_set_double(
					filter_settings,
					"Filter.Transform.Position.Z",
					values[5]
				)
			obs.obs_data_set_double(
					filter_settings,
					"Filter.Transform.Camera.FieldOfView",
					values[6]
				)
			obs.obs_data_set_double(
					filter_settings,
					"Filter.Transform.Camera",
					1
				)
			
			obs.obs_source_update(filter, filter_settings)

			# Release the resources
			obs.obs_data_release(filter_settings)
			obs.obs_source_release(filter)

		obs.obs_source_release(source)

def script_description():
	return "Controls a 3D Transform through a remote UDP message"


def script_update(settings):
	global pansource
	global sock

	pansource = obs.obs_data_get_string(settings, "pansource")
	UDP_IP = obs.obs_data_get_string(settings, 'ip')
	UDP_PORT = obs.obs_data_get_int(settings,'port')
	if sock is not None:
		sock.close()
		sock = None

	sock = socket.socket(socket.AF_INET, # Internet
						socket.SOCK_DGRAM) # UDP
	sock.bind((UDP_IP, UDP_PORT))
	sock.setblocking(0)

def script_unload():
	global sock
	if sock is not None:
		sock.close()
		sock = None

def script_defaults(settings):
	obs.obs_data_set_default_string(settings, "pansource", "PanCamera")
	obs.obs_data_set_default_string(settings, "ip", "127.0.0.1")
	obs.obs_data_set_default_int(settings, "port", 5005)

def script_properties():
	props = obs.obs_properties_create()

	obs.obs_properties_add_text(props, "pansource", "Source to pan", obs.OBS_TEXT_DEFAULT)
	obs.obs_properties_add_text(props, "ip", "Local address to bind to", obs.OBS_TEXT_DEFAULT)
	obs.obs_properties_add_int(props, "port", "Local port to bind to",1024,30000,5005)

	return props
