

def convertToMap(lens: list):
    x = ""
    for i in lens:
        x+=chr(i)
    return x

def main():
    l = []

    for i in range(30):
        l.append(130)
        l.append(70)

    l.append(200*10)

    for i in range(100):
        l.append(100)
        l.append(100)

    for i in range(60):
        l.append(40)
        l.append(20)
        l.append(110)
        l.append(30)

    print(convertToMap(l))

main()