import serial
import sys
import time
import os

"""
Terabee API for use with path_planning. 
"""
path = os.path.abspath("SensorCode")
sys.path.append(path) #Might need to be resolved
sys.path.append('/Users/angelachao/Documents/Academics/C1C0_path_planning/SensorCode')
import R2Protocol2 as r2p

ser = None

LIDAR_DATA_POINTS = 360
LIDAR_DATA_LEN = LIDAR_DATA_POINTS * 4

TERABEE_DATA_POINTS = 8
TERABEE_DATA_LEN = TERABEE_DATA_POINTS * 2

IMU_DATA_POINTS = 3
IMU_DATA_LEN = IMU_DATA_POINTS * 2

# variables for indexing
ENCODING_BYTES = 16
ENCODING_BYTES_TOTAL = ENCODING_BYTES * 5 # 16 EACH FOR LIDAR, IMU, AND 3 TERABEES

TOTAL_BYTES = LIDAR_DATA_LEN + TERABEE_DATA_LEN*3 + IMU_DATA_LEN + ENCODING_BYTES_TOTAL

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
        print("array_type must be one of 'TB1', 'TB2', 'TB3', 'LDR', IMUG', or 'IMUA'")


def decode_arrays():
    """
    Description: Checks to see if the mtype bit is a valid type and then
    calls the function to decode it based on the type indicated.
    Functions using API must call this to update global arrays
    Returns: Nothing
    """
    global ser, terabee_array_1, terabee_array_2, terabee_array_3, ldr_array
    global imu_array

    good_data = False
    print("GET ARRAY FUNCTION")
    while(not good_data):
        terabee_array_1 = []
        terabee_array_2 = []
        terabee_array_3 = []
        ldr_array = []
        imu_array = []

        # ~ print("IN LOOOP")
        ser.read_until(b"\xd2\xe2\xf2")
        time.sleep(0.001)
        ser_msg = ser.read(TOTAL_BYTES) #IMU +IR1+IR2+IR3+LIDAR+ENCODING
        # ~ print(ser_msg)
        # ~ print("GOT MESSAGE")
        mtype, data, status = r2p.decode(ser_msg)
        """
        print("TYPE: " + str(mtype))
        print("")
        print("Data: " + str(data))
        print("")
        print("Status: " + str(status))
        """
        print("TYPE: \n" + str(mtype))
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
            print("NO GOOD")
            ser.reset_input_buffer()
            time.sleep(0.01)


def decode_from_ir(data):
    """
    Description: Function that decodes the data if the received mtype
    is that corresponding to Terabee 1.
    Returns: Nothing
    """
    terabee1_data = data[:TERABEE_DATA_LEN]
    terabee2_data = data[TERABEE_DATA_LEN + ENCODING_BYTES:TERABEE_DATA_LEN + ENCODING_BYTES + TERABEE_DATA_LEN]
    terabee3_data = data[TERABEE_DATA_LEN*2 + ENCODING_BYTES*2:TERABEE_DATA_LEN*2 + ENCODING_BYTES*2 + TERABEE_DATA_LEN]
    ldr_data      = data[TERABEE_DATA_LEN*3 + ENCODING_BYTES*3:TERABEE_DATA_LEN*3 + ENCODING_BYTES*3 + LIDAR_DATA_LEN]
    imu_data      = data[TERABEE_DATA_LEN*3 + LIDAR_DATA_LEN + ENCODING_BYTES*4:TOTAL_BYTES]


def decode_from_ir2(data):
    """
    Description: Function that decodes the data if the received mtype
    is that corresponding to Terabee 2.
    Returns: Nothing
    """
    terabee2_data = data[:TERABEE_DATA_LEN]
    terabee3_data = data[TERABEE_DATA_LEN + ENCODING_BYTES:TERABEE_DATA_LEN + ENCODING_BYTES + TERABEE_DATA_LEN]
    ldr_data      = data[TERABEE_DATA_LEN*2 + ENCODING_BYTES*2:TERABEE_DATA_LEN*2 + ENCODING_BYTES*2 + LIDAR_DATA_LEN]
    imu_data      = data[TERABEE_DATA_LEN*2 + LIDAR_DATA_LEN + ENCODING_BYTES*3:
                         TERABEE_DATA_LEN*2 + LIDAR_DATA_LEN + ENCODING_BYTES*3 + IMU_DATA_LEN]
    terabee1_data = data[TERABEE_DATA_LEN*2 + LIDAR_DATA_LEN + ENCODING_BYTES*4 + IMU_DATA_LEN:TOTAL_BYTES]
    
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
    terabee3_data = data[:TERABEE_DATA_LEN]
    ldr_data      = data[TERABEE_DATA_LEN + ENCODING_BYTES:TERABEE_DATA_LEN + ENCODING_BYTES + LIDAR_DATA_LEN]
    imu_data      = data[TERABEE_DATA_LEN + LIDAR_DATA_LEN + ENCODING_BYTES*2:
                         TERABEE_DATA_LEN + LIDAR_DATA_LEN + ENCODING_BYTES*2 + IMU_DATA_LEN]
    terabee1_data = data[TERABEE_DATA_LEN + LIDAR_DATA_LEN + IMU_DATA_LEN + ENCODING_BYTES*3:
                         TERABEE_DATA_LEN + LIDAR_DATA_LEN + IMU_DATA_LEN + ENCODING_BYTES*3 + TERABEE_DATA_LEN]
    terabee2_data = data[TERABEE_DATA_LEN*2 + LIDAR_DATA_LEN + IMU_DATA_LEN + ENCODING_BYTES*4:
                         TOTAL_BYTES]

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
    ldr_data      = data[:LIDAR_DATA_LEN]
    imu_data      = data[LIDAR_DATA_LEN + ENCODING_BYTES:LIDAR_DATA_LEN + ENCODING_BYTES + IMU_DATA_LEN]
    terabee1_data = data[LIDAR_DATA_LEN + IMU_DATA_LEN + ENCODING_BYTES*2 :
                         LIDAR_DATA_LEN + IMU_DATA_LEN + ENCODING_BYTES*2 + TERABEE_DATA_LEN]
    terabee2_data = data[LIDAR_DATA_LEN + IMU_DATA_LEN + TERABEE_DATA_LEN + ENCODING_BYTES*3:
                         LIDAR_DATA_LEN + IMU_DATA_LEN + TERABEE_DATA_LEN + ENCODING_BYTES*3 + TERABEE_DATA_LEN]
    terabee3_data = data[LIDAR_DATA_LEN + IMU_DATA_LEN + TERABEE_DATA_LEN*2 + ENCODING_BYTES*4:]

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
    imu_data      = data[:IMU_DATA_LEN]
    terabee1_data = data[IMU_DATA_LEN + ENCODING_BYTES:IMU_DATA_LEN + ENCODING_BYTES + TERABEE_DATA_LEN]
    terabee2_data = data[IMU_DATA_LEN + TERABEE_DATA_LEN + ENCODING_BYTES*2:
                         IMU_DATA_LEN + TERABEE_DATA_LEN + ENCODING_BYTES*2 + TERABEE_DATA_LEN]
    terabee3_data = data[IMU_DATA_LEN + TERABEE_DATA_LEN*2 + ENCODING_BYTES*3:
                         IMU_DATA_LEN + TERABEE_DATA_LEN*3 + ENCODING_BYTES*3:]
    ldr_data      = data[IMU_DATA_LEN + TERABEE_DATA_LEN*3 + ENCODING_BYTES*4:]


def imu_array_append(data, target_array):
    """
    Description: Copies the data received into the corresponding IMU array.
    Parameters:
        bytes Array data - the data to be placed in the target array
        target_array - the corresponding array for data to be copied to
    """
    for i in range(0, 6, 2):
        target_array.append(int.from_bytes(data[i:i + 2],
                                           byteorder='big', signed=True))


def terabee_array_append(data, target_array):
    """
    Description: Copies the data received into the corresponding Terabee array.
    Parameters:
        bytes Array data - the data to be placed in the target array
        target_array - the corresponding array for data to be copied to
    """
    for i in range(0, 16, 2):
        value = (data[i] << 8) | data[i + 1]
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
        
def sensor_permissions (send_permission):
    """
    Parameter: send_permission is either a 0 or 1. 1 if sensors should send data
    0 if sensors should cease to send data. 
    """
    send_message = r2p.encode(bytes("SND","utf-8"),bytearray([send_permission]))
    ser.write(send_message)
    print(send_message)

    

if __name__ == '__main__':
    init_serial('/dev/ttyTHS1', 115200)
    ser.reset_input_buffer()

    #print("STARTED")

    try:
    
        while True:
            
        
            if ser.in_waiting:
                decode_arrays()
                ldr = get_array('LDR')
                tb1 = get_array('TB1')
                tb2 = get_array('TB2')
                tb3 = get_array('TB3')
                imu = get_array('IMU')
            
                print(tb2)
            # ~ else:
                # ~ print("NOT GOT")
            # ~ time.sleep(1)
        ser.close()
    

    except KeyboardInterrupt:
        ser.close()
