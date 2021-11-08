import serial
import time
import sys

"""
IMU API for use with path_planning. 

"""
sys.path.append('../c1c0-movement/c1c0-movement/Locomotion') #Might need to be resolved
import R2Protocol2 as r2p

ser = None

lin_accel_array = []
gyro_array = []

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
	
	

def get_imu_tuples():
	"""

	
	"""
	global ser, gyro_array, lin_accel_array
	
	good_data = False
	
	ser.reset_input_buffer()
	
	while(not good_data):
		
		gyro_array = []
		lin_accel_array = []
		
		ser_msg = ser.read(28)
		
		# ~ for i in range(0, len(ser_msg), 22):
			
		mtype, data, status = r2p.decode(ser_msg)
		
		print(mtype)
		#print(data)
		print(status)
		print(len(data))
		
		if(status == 1):
			good_data = True
			
			if(mtype==b'IMU\x00'):
				for i in range(0, len(data), 2):
					if (i < 6):
						gyro_array.append(int.from_bytes(data[i:i+2],
										  byteorder = 'big', signed = True))
					else:
						lin_accel_array.append(int.from_bytes(data[i:i+2],
										  byteorder = 'big', signed = True))
			
			# ~ if(mtype==b'IMU\x00'):
				# ~ for i in range(0, len(data), 2):
					# ~ gyro_array.append(int.from_bytes(data[i:i+2], 
									# ~ byteorder = 'big', signed = True))
			# ~ elif(mtype==b'LINA'):
				# ~ for i in range(0, len(data), 2):
					# ~ lin_accel_array.append(int.from_bytes(data[i:i+2], 
									# ~ byteorder = 'big', signed = True))
			
			
				
		else:
			ser.reset_input_buffer()

		
	return gyro_array, lin_accel_array
		


if __name__ == '__main__':
	init_serial('/dev/ttyTHS1', 38400)
	
	try:
		#while True:

		start = time.time()
		arr, arr1 = get_imu_tuples()
		print("Gyro: ")
		for i in arr:
			print(i)
		print("Linear Acceleration: ")
		for i in arr1:
			print(i)
		print("End of seg")
		end = time.time() - start
		print(end)
			
	except KeyboardInterrupt:
		ser.close()
