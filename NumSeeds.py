import random

def numericalSeed():
    try:
        x = int(input("Please enter a seed (1 to 10^9): "))
        random.seed(x)
        print("The seed is " + str(x))
    except:
        x = random.randint(1, 10 ** 9)
        print("That didn't work. The seed is " + str(x))
        random.seed(x)