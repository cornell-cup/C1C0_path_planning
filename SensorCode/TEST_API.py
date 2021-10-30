import serial
import time
import sys

"""
Terabee API for use with path_planning. 

"""
sys.path.append('../c1c0-movement/c1c0-movement/Locomotion') #Might need to be resolved
import R2Protocol2 as r2p

ser = None

terabee_array_1 = []
terabee_array_2 = []
terabee_array_3 = []
ldr_array = []
imu_gyro_array = []
imu_accel_array = []

def init_serial(port, baud):
	"""
	Opens serial port for LIDAR communication
	port should be a string linux port: Ex dev/ttyTHS1
	Baud is int the data rate, commonly multiples of 9600
	"""
	global ser, startseq, endseq
	
	ser = serial.Serial(port,
						baud)
	

def close_serial():
	global ser
	ser.close()
	
def get_array(array_type):
	"""
	Description: Returns the specified sensor array using the given parameter
	Parameters: String array_type
	Returns: Array
	"""
	if array_type == "TB1":
		return terabee_array_1
	elif array_type == "TB2":
		return terabee_array_2
	elif array_type == "TB3":
		return terabee_array_3
	elif array_type == "LDR":
		return ldr_array
	elif array_type == "IMUG":
		return imu_gyro_array
	elif array_type == "IMUA":
		return imu_accel_array
	else:
		print("array_type must be one of 'TB1', 'TB2', 'TB3', 'LDR', IMUG', or 'IMUA'" )
	
	

def decode_arrays():
	"""
	Description: Checks to see if the mtype bit is a valid type and then 
	calls the function to decode it based on the type indicated.
	Returns: Nothing 
	
	"""
	global ser, terabee_array_1, terabee_array_2, terabee_array_3, ldr_array
	global imu_gyro_array, imu_accel_array
	
	good_data = False
	print("GET ARRAY FUNCTION")
	while(not good_data):
		terabee_array_1 = []
		terabee_array_2 = []
		#terabee_array_3 = []
		ldr_array = []
		imu_gyro_array = []
		imu_accel_array = []
		
		print("IN LOOOP")
		ser_msg = ser.read(308)
		print("GOT MESSAGE")
		mtype, data, status = r2p.decode(ser_msg)
		
		print("TYPE: \n" + str(mtype))
		#print("DATA:" + str(data))
		
		if (mtype == b'IR\x00\x00'):
			decode_from_ir(data)
			good_data = True
			
		elif (mtype == b'IR2\x00'):
			decode_from_ir2(data)
			good_data = True
			
		elif (mtype == b'LDR\x00'):
			decode_from_ldr(data)
			good_data = True
			
			
		elif (mtype == b'IMU\x00'):
			decode_from_imu(data)
			good_data = True
			
		else:
			print("NO GOOD")
			ser.reset_input_buffer()
			

def decode_from_ir(data):
	"""
	Description: Function that decodes the data if the received mtype
	is that corresponding to Terabee 1.
	Returns: Nothing
	"""
	
	terabee1_data = data[0:16]
	terabee2_data = data[32:32+16]
	ldr_data = data[64:64+200]
	imu_data = data[264+16:]
	
	terabee_array_append(terabee1_data, terabee_array_1)
	terabee_array_append(terabee2_data, terabee_array_2)
	lidar_tuple_array_append(ldr_data, ldr_array)
	imu_array_append(imu_data[:6], imu_gyro_array)
	imu_array_append(imu_data[6:], imu_accel_array)
	
	print("TERABEE 1:")
	for item in terabee_array_1:
		print(item)
	
	print("TERABEE 2:")
	for item in terabee_array_2:
		print(item)
		
	print("LIDAR:")
	print(ldr_array)
	
	print("IMU GYRO: ")
	print(imu_gyro_array)
	
	print("IMU ACCEL: ")
	print(imu_accel_array)
		
def decode_from_ir2(data):
	"""
	Description: Function that decodes the data if the received mtype
	is that corresponding to Terabee 2.
	Returns: Nothing
	"""
	
	terabee2_data = data[0:16]
	ldr_data = data[32:32+200]
	imu_data = data[232+16:232+16+12]
	terabee1_data = data[260+16:]
	
	terabee_array_append(terabee1_data, terabee_array_1)
	terabee_array_append(terabee2_data, terabee_array_2)
	lidar_tuple_array_append(ldr_data, ldr_array)
	imu_array_append(imu_data[:6], imu_gyro_array)
	imu_array_append(imu_data[6:], imu_accel_array)
	
	print("TERABEE 1:")
	for item in terabee_array_1:
		print(item)
	
	print("TERABEE 2:")
	for item in terabee_array_2:
		print(item)
		
	print("LIDAR:")
	print(ldr_array)
	
	print("IMU GYRO: ")
	print(imu_gyro_array)
	
	print("IMU ACCEL: ")
	print(imu_accel_array)
	
def decode_from_ldr(data):
	"""
	Description: Function that decodes the data if the received mtype
	is that corresponding to LIDAR.
	Returns: Nothing
	"""
	
	ldr_data = data[:200]
	imu_data = data[200+16:228]
	terabee1_data = data[228+16:228+16+12]
	terabee2_data = data[256+16:]
	
	terabee_array_append(terabee1_data, terabee_array_1)
	terabee_array_append(terabee2_data, terabee_array_2)
	lidar_tuple_array_append(ldr_data, ldr_array)
	imu_array_append(imu_data[:6], imu_gyro_array)
	imu_array_append(imu_data[6:], imu_accel_array)
	
	print("TERABEE 1:")
	for item in terabee_array_1:
		print(item)
	
	print("TERABEE 2:")
	for item in terabee_array_2:
		print(item)
		
	print("LIDAR:")
	print(ldr_array)
	
	print("IMU GYRO: ")
	print(imu_gyro_array)
	
	print("IMU ACCEL: ")
	print(imu_accel_array)
	
def decode_from_imu(data):
	"""
	Description: Function that decodes the data if the received mtype
	is that corresponding to IMU.
	Parameters: 
	Returns: Nothing
	"""
	
	imu_data = data[:12]
	terabee1_data = data[12+16:28+16]
	terabee2_data = data[44+16:60+16]
	ldr_data = data[76+16:]
	
	# ~ print(terabee1_data)
	# ~ print(terabee2_data)
	# ~ print(ldr_data)
	
	terabee_array_append(terabee1_data, terabee_array_1)
	terabee_array_append(terabee2_data, terabee_array_2)
	lidar_tuple_array_append(ldr_data, ldr_array)
	imu_array_append(imu_data[:6], imu_gyro_array)
	imu_array_append(imu_data[6:], imu_accel_array)
	
	print("TERABEE 1:")
	for item in terabee_array_1:
		print(item)
	
	print("TERABEE 2:")
	for item in terabee_array_2:
		print(item)
		
	print("LIDAR:")
	print(ldr_array)
	
	print("IMU GYRO: ")
	print(imu_gyro_array)
	
	print("IMU ACCEL: ")
	print(imu_accel_array)
	
def imu_array_append(data, target_array):
	"""
	Description: Copies the data received into the corresponding IMU array.
	Parameters: 
		bytes Array data - the data to be placed in the target array
		target_array - the corresponding array for data to be copied to
	"""
	for i in range(0, 6, 2):
		target_array.append(int.from_bytes(data[i:i+2],
							byteorder = 'big', signed = True))
	

def terabee_array_append(data, target_array):
	"""
	Description: Copies the data received into the corresponding Terabee array.
	Parameters: 
		bytes Array data - the data to be placed in the target array
		target_array - the corresponding array for data to be copied to
	"""
	for i in range(0, 16, 2):
		value = (data[i]<<8) | data[i+1]
		target_array.append(value)
		
def lidar_tuple_array_append(data, target_array):
	"""
	Description: Copies the data received into the corresponding LDR array.
	Parameters: 
		bytes Array data - the data to be placed in the target array
		target_array - the corresponding array for data to be copied to
	"""
	for i in range(0, 200, 4):
		angle_msbs = data[i]
		angle_lsbs = data[i+1]
		distance_msbs = data[i+2]
		distance_lsbs = data[i+3]
		angle = angle_msbs<<8 | angle_lsbs
		distance = distance_msbs<<8 | distance_lsbs
		target_array.append((angle,distance))
		
if __name__ == '__main__':
	init_serial('/dev/ttyTHS1', 115200)
	
	print("STARTED")
	
	try:
		while True:
			decode_arrays()
			ldr = get_array('LDR')
			for tup in ldr:
				print(tup)

	except KeyboardInterrupt:
		ser.close()
