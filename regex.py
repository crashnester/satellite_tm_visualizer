import re

file_pattern = r'F1[-\s:_]{0,3}0F[-\s:_]{0,3}[0-9A-F]{2}[-\s:_]{0,3}6[01][-\s:_]{0,3}([0-9A-F]{2}[-\s:_]{0,3}){123}[0-9A-F]{2}'		# parse source file to frames
frame_pattern = r'[0-9A-F]{2}'																										# parse one frame to bytes
file_name_pattern = r'[0-9]{8}-[0-9]{6,7}'																							# parse file name to extract unload date-time

stp_iss_beebee_test_pattern = r'BE[\s]E0[\s]BE[\s]E0[\s]([0-9A-F]{2}[\s]){199}[0-9A-F]{2}'
stp_iss_deadbeaf_test_pattern = r'DE[\s]AD[\s]BE[\s]AF[\s]([0-9A-F]{2}[\s]){199}[0-9A-F]{2}'
stp_iss_badbee_test_pattern = r'BA[\s]D0[\s]BE[\s]E0[\s]([0-9A-F]{2}[\s]){199}[0-9A-F]{2}'

iteration_pattern = r'([0-9A-F]{2}[\s]){3}[0-9A-F]{2}'

file_regex = re.compile(file_pattern)
frame_regex = re.compile(frame_pattern)
file_name_regex = re.compile(file_name_pattern)

stp_iss_beebee_test_regex = re.compile(stp_iss_beebee_test_pattern)
stp_iss_deadbeaf_test_regex = re.compile(stp_iss_deadbeaf_test_pattern)
stp_iss_badbee_test_regex = re.compile(stp_iss_badbee_test_pattern)

iteration_regex = re.compile(iteration_pattern)
