import serial
import sys
import time

"""
Terabee API for use with path_planning. 

"""
sys.path.append('../c1c0-movement/c1c0-movement/Locomotion') #Might need to be resolved
#import SensorCode.R2Protocol2 as r2p
import R2Protocol2 as r2p

ser = None

LIDAR_DATA_POINTS = 360
LIDAR_DATA_LEN = LIDAR_DATA_POINTS * 4

terabee_array_1 = []
terabee_array_2 = []
terabee_array_3 = []
ldr_array = []
imu_array = []

def init_serial(port, baud):
	"""
	Opens serial port for LIDAR communication
	port should be a string linux port: Ex dev/ttyTHS1
	Baud is int the data rate, commonly multiples of 9600
	For using all all three types of sensors, baud should be 115200
	"""
	global ser, startseq, endseq

	ser = serial.Serial(port, baud)


def close_serial():
	"""
	Closes serial port for sensor communication
	"""
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
	elif array_type == "IMU":
		return imu_array
	else:
		print("array_type must be one of 'TB1', 'TB2', 'TB3', 'LDR', IMUG', or 'IMUA'" )



def decode_arrays():
	"""
	Description: Checks to see if the mtype bit is a valid type and then
	calls the function to decode it based on the type indicated.
	Returns: Nothing

	"""
	global ser, terabee_array_1, terabee_array_2, terabee_array_3, ldr_array
	global imu_array

	good_data = False
	#print("GET ARRAY FUNCTION")
	while(not good_data):
		terabee_array_1 = []
		terabee_array_2 = []
		terabee_array_3 = []
		ldr_array = []
		imu_array = []

		#print("IN LOOOP")
		ser_msg = ser.read(22+32+32+32+LIDAR_DATA_LEN+16) #IMU +IR1+IR2+IR3+LIDAR
		#print(ser_msg)
		#print("GOT MESSAGE")
		mtype, data, status = r2p.decode(ser_msg)
		"""
		print("TYPE: " + str(mtype))
		print("")
		print("Data: " + str(data))
		print("")
		print("Status: " + str(status))
		"""
		#print("TYPE: \n" + str(mtype))
		#print("DATA:" + str(data))

		if (mtype == b'IR\x00\x00'):
			decode_from_ir(data)
			good_data = True

		elif (mtype == b'IR2\x00'):
			decode_from_ir2(data)
			good_data = True

		elif (mtype == b'IR3\x00'):
			decode_from_ir3(data)
			good_data = True

		elif (mtype == b'LDR\x00'):
			decode_from_ldr(data)
			good_data = True


		elif (mtype == b'IMU\x00'):
			decode_from_imu(data)
			good_data = True

		else:
			#print("NO GOOD")
			ser.reset_input_buffer()


def decode_from_ir(data):
	"""
	Description: Function that decodes the data if the received mtype
	is that corresponding to Terabee 1.
	Returns: Nothing
	"""

	terabee1_data = data[0:16]
	terabee2_data = data[32:32+16]
	terabee3_data = data[64:64+16]
	ldr_data = data[96:96+LIDAR_DATA_LEN]
	imu_data = data[96+LIDAR_DATA_LEN+16:]

	terabee_array_append(terabee1_data, terabee_array_1)
	terabee_array_append(terabee2_data, terabee_array_2)
	terabee_array_append(terabee3_data, terabee_array_3)
	lidar_tuple_array_append(ldr_data, ldr_array)
	imu_array_append(imu_data, imu_array)

def decode_from_ir2(data):
	"""
	Description: Function that decodes the data if the received mtype
	is that corresponding to Terabee 2.
	Returns: Nothing
	"""

	terabee2_data = data[0:16]
	terabee3_data = data[32:32+16]
	ldr_data = data[64:64+LIDAR_DATA_LEN]
	imu_data = data[80+ LIDAR_DATA_LEN:80+LIDAR_DATA_LEN+6]
	terabee1_data = data[86+LIDAR_DATA_LEN+16:]

	terabee_array_append(terabee1_data, terabee_array_1)
	terabee_array_append(terabee2_data, terabee_array_2)
	terabee_array_append(terabee3_data, terabee_array_3)
	lidar_tuple_array_append(ldr_data, ldr_array)
	imu_array_append(imu_data, imu_array)

def decode_from_ir3(data):
	"""
	Description: Function that decodes the data if the received mtype
	is that corresponding to Terabee 3.
	Returns: Nothing
	"""

	terabee3_data = data[0:16]
	ldr_data = data[32:32+LIDAR_DATA_LEN]
	imu_data = data[48+LIDAR_DATA_LEN:48+LIDAR_DATA_LEN+12]
	terabee1_data = data[70+LIDAR_DATA_LEN:70+LIDAR_DATA_LEN+16]
	terabee2_data = data[86+LIDAR_DATA_LEN+16:]

	terabee_array_append(terabee1_data, terabee_array_1)
	terabee_array_append(terabee2_data, terabee_array_2)
	terabee_array_append(terabee3_data, terabee_array_3)
	lidar_tuple_array_append(ldr_data, ldr_array)
	imu_array_append(imu_data, imu_array)


def decode_from_ldr(data):
	"""
	Description: Function that decodes the data if the received mtype
	is that corresponding to LIDAR.
	Returns: Nothing
	"""

	ldr_data = data[0:LIDAR_DATA_LEN]
	imu_data = data[16+LIDAR_DATA_LEN:16+LIDAR_DATA_LEN+6]
	terabee1_data = data[38+LIDAR_DATA_LEN:38+LIDAR_DATA_LEN+16]
	terabee2_data = data[70+LIDAR_DATA_LEN:70+LIDAR_DATA_LEN+16]
	terabee3_data = data[86+LIDAR_DATA_LEN+16:]

	terabee_array_append(terabee1_data, terabee_array_1)
	terabee_array_append(terabee2_data, terabee_array_2)
	terabee_array_append(terabee3_data, terabee_array_3)
	lidar_tuple_array_append(ldr_data, ldr_array)
	imu_array_append(imu_data, imu_array)


def decode_from_imu(data):
	"""
	Description: Function that decodes the data if the received mtype
	is that corresponding to IMU.
	Parameters:
	Returns: Nothing
	"""

	imu_data = data[0:6]
	terabee1_data = data[22:22+16]
	terabee2_data = data[54:54+16]
	terabee3_data = data[86:86+16]
	ldr_data = data[102+16:]

	terabee_array_append(terabee1_data, terabee_array_1)
	terabee_array_append(terabee2_data, terabee_array_2)
	terabee_array_append(terabee3_data, terabee_array_3)
	lidar_tuple_array_append(ldr_data, ldr_array)
	imu_array_append(imu_data, imu_array)

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
	for i in range(0, LIDAR_DATA_LEN, 4):
		angle_msbs = data[i]
		angle_lsbs = data[i+1]
		distance_msbs = data[i+2]
		distance_lsbs = data[i+3]
		angle = angle_msbs<<8 | angle_lsbs
		distance = distance_msbs<<8 | distance_lsbs
		target_array.append((angle,distance))

if __name__ == '__main__':
	init_serial('/dev/ttyTHS1', 115200)

	#print("STARTED")

	try:
		start = time.time()
		for i in range(20):
			decode_arrays()
			print(i)
			ldr = get_array('LDR')
			print(ldr)
			raise Exception
			tb1 = get_array('TB1')
			tb2 = get_array('TB2')
			tb3 = get_array('TB3')
			imu = get_array('IMU')
		print(f"Elapsed time for 20 iters is {time.time() - start}")
			#print(ldr)

	except KeyboardInterrupt:
		ser.close()
