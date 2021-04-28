import serial

def scan():
    available = []
    for i in range(256):
        try:
            s = serial.Serial('COM'+str(i))
            available.append( (s.portstr))
            s.close()   # explicit close 'cause of delayed GC in java
        except serial.SerialException:
            pass

    for s in available:
        print("%s" % (s))


if __name__=='__main__':
    print("Found ports:")
    print(scan())
