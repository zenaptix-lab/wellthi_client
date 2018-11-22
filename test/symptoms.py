from Models.WellthiServer import *

if __name__ == '__main__':
    symp = Symptoms()
    value = symp.encode(["COLD", "FEVER", "DIZZY"])
    print(value)

