import serial
import time
import sys

"""
LIDAR API for use with path_planning. 

"""
sys.path.append('../c1c0-movement/c1c0-movement/Locomotion') #Might need to be resolved
import SensorCode.R2Protocol2 as r2p

ser = None
startseq = None
endseq = None
lidar_tuple_array = []

def init_serial(port, baud):
	"""
	Opens serial port for LIDAR communication
	port should be a string linux port: Ex dev/ttyTHS1
	Baud is int the data rate, commonly multiples of 9600
	"""
	global ser, startseq, endseq
	
	ser = serial.Serial(port,
						baud)
	startseq = (16777215).to_bytes(3, 'big')
	endseq = (16777214).to_bytes(3, 'big')

def close_serial():
	global ser
	ser.close()

def pack(tup):
	return(tup[0]<<8 | tup[1])
	

def get_LIDAR_tuples():
	"""
	Acquires and returns one array of lidar data:
	Data is acquired in a tuple array of 50 data points
	The first entry in the tuple is an angle in [0,359]
	The second entry in the tuple is the distance, in mm, floored to nearest int
	
	"""
	global ser, startseq, endseq, lidar_tuple_array
	
	good_data = False
	
	while(not good_data):
		lidar_tuple_array = []
		ser_msg = ser.read(216)
			
		mtype, lidar_data, status = r2p.decode(ser_msg)
		
		# ~ print(mtype)
		# ~ print(lidar_data)
		
		
		if(status == 1):
			good_data = True
			if(mtype == b'LDR\x00'):
				for i in range(0, len(lidar_data), 4):
					# ~ print("Here")
					angle_msbs = lidar_data[i]
					angle_lsbs = lidar_data[i+1]
					distance_msbs = lidar_data[i+2]
					distance_lsbs = lidar_data[i+3]
					#print("Packet: " + str(i))
					# ~ print("Angle MSB: " + str(angle_msbs) + " Angle LSB: " + str(angle_lsbs))
					# ~ print("Distance MSB: " + str(distance_msbs) + " Distance LSB: " + str(distance_lsbs))
					angle = pack((angle_msbs, angle_lsbs))
					distance = pack((distance_msbs, distance_lsbs))
					# ~ print("Angle: " + str(angle))
					# ~ print("Distance: " + str(distance))
					# ~ print("")
					lidar_tuple_array.append((angle,distance))
		else:
			ser.reset_input_buffer()
			
	return lidar_tuple_array
		


if __name__ == '__main__':
	init_serial('/dev/ttyTHS1', 38400)
	
	try:
		while True:
			start = time.time()
			arr = get_LIDAR_tuples()
			# ~ for i in arr:
				# ~ print(i)
			print("End of seg")
			end = time.time() - start
			print(end)
			
	except KeyboardInterrupt:
		ser.close()
