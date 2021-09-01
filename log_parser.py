import os
import numpy as np
import pandas as pd
import regex

class LogParser():
	def __init__(self):
		self.frame_columns = ['file_date', 'file_time', 'frame_type', 'n_mas', 'board_time', 'data_frames_num']
		self.telemetry = [
			'pl',
			'voltage', 
			'current', 
			'input_states', 
			'output_states', 
			'temperature', 
			'pl_errors_num', 
			'pl_errors',
			'pl_status'
		]

		self.telemetry = [list(map(lambda x: x + str(i), self.telemetry)) for i in range(8)]
		self.telemetry = list(np.append([], self.telemetry))

		self.frame_columns += self.telemetry

	def get_logs_from_directory(self, directory):
		root_files = os.listdir(directory)

		if directory[-1] != '/' and directory[-1] != '\\' :
			directory += '/'

		frames = pd.DataFrame({})

		for file in root_files:
			if os.path.isfile(directory + file):
				frames = frames.append(self.parse_logs(directory, file))
			elif os.path.isdir(directory + file):
				frames = frames.append(self.get_logs_from_directory(directory + file))

		return frames.reset_index(drop=True)

	def parse_logs(self, directory, log_filename):
		file_date_time = regex.file_name_regex.findall(log_filename)

		if len(file_date_time) == 0:	# неверный формат файла
			return []

		file_date_time = file_date_time[0].split('-')
		if len(file_date_time) != 2 :	# неверный формат файла
			return

		file_date, file_time = int(file_date_time[0]), int(file_date_time[1])

		file = open(directory + log_filename, 'r')
		raw_frames = [x.group() for x in regex.file_regex.finditer(file.read())]
		frames = pd.DataFrame({})

		for frame in raw_frames :
			bytes_ = regex.frame_regex.findall(frame)
			if len(bytes_) != 128:	# wrong frame
				continue

			parsed_frame = self.parse_frame(bytes_, file_date, file_time)
			tmp = pd.DataFrame(parsed_frame)
			frames = frames.append(tmp)

		return frames

	def parse_frame(self, frame, file_date, file_time):
		id_loc = frame[2] + frame[3]
		if id_loc == '8960' :
			frame_type = 'tm_frame'
		elif id_loc == '8961' :
			frame_type = 'data_frame'
		else :
			frame_type = 'unknown_type'

		n_mas = int(frame[5] + frame[4], 16)

		if frame_type == 'tm_frame' :
			time = int(frame[9] + frame[8] + frame[7] + frame[6], 16)
			data_frames_num = int(frame[11] + frame[10], 16)
			data = ' '.join(frame[12:126])
			crc = int(frame[127] + frame[126], 16)
		else :
			time = ''
			data_frames_num = int(frame[7] + frame[6], 16)
			data = ' '.join(frame[8:126])
			crc = int(frame[127] + frame[126], 16)


		tmp = {}
		for i in range(len(self.telemetry)):
			tmp[self.telemetry[i]] = None


		tm_data = data
		if frame_type == 'tm_frame':
			tm_data = tm_data.split()
			counter = 0
			for i in range(1, 9) :
				cyclogram_data = self.parse_tmi(list(map(lambda x: int(x, 16), tm_data[6 + 12 * i : 6 + 12 * (i + 1)])))	# 18-30, 30-42, 42-54 etc.

				for key in cyclogram_data.keys():
					tmp[self.telemetry[counter]] = cyclogram_data[key]
					counter += 1

		series = [file_date, file_time, frame_type, n_mas, time, data_frames_num]
		series += tmp.values()

		frames = {}
		for i in range(len(self.frame_columns) - 1) :
			frames[self.frame_columns[i]] = [series[i]]

		#frames['raw_frame'] = [' '.join(frame)]

		return frames

	def parse_tmi(self, raw_tmi) :		# parse one tmi slice
		tmi = {}

		nan = False
		if raw_tmi[0] == 0xFE and raw_tmi[1] == 0xFE and raw_tmi[2] == 0xFE :		# reserved
			raw_tmi = [np.nan] * len(raw_tmi)
			nan = True
	
		#tmi['cut_num'] = raw_tmi[0]
		tmi['pl_num'] = raw_tmi[1]
		tmi['voltage'] = float('{:.3f}'.format(raw_tmi[2] / 16))
		tmi['current'] = float('{:.3f}'.format(raw_tmi[3] / 16))
		tmi['input_states'] = raw_tmi[4]
		tmi['output_states'] = raw_tmi[5]
		temperature = raw_tmi[6]
		if temperature > 100 :
			temperature -= 256
		tmi['temperature'] = temperature
		tmi['pl_errors_num'] = raw_tmi[7]

		if nan:
			tmi['pl_errors'] = np.nan
			tmi['pl_status'] = np.nan
		else:
			tmi['pl_errors'] = (raw_tmi[9] << 8) + raw_tmi[8]
			tmi['pl_status'] = (raw_tmi[11] << 8) + raw_tmi[10]	

		return tmi