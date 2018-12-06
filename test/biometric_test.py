from Models.WellthiServer import *

if __name__ == '__main__':
    bio_obj = Biometric(1, 1541515323, 1541515173,
                        242.22200062038348, 247.13926630016155, 807.6576576576576, 45668.848724130075, "mourits",
                        87613.41240988596, 4.793300312115103)

    json_str = bio_obj.decode()
    print(json_str)
    json_str2 = """{"status": 1, "from": 1541515173, "id": "mourits", "to": 1541515323, "val3": 242.22200062038348,
                "val2": 247.13926630016155, "val1": 807.6576576576576, "val6": 4.793300312115103,
                "val5": 87613.41240988596, "val4": 45668.848724130075}"""

    bio_obj_2 = Biometric.encode(json_str2)
    print(bio_obj_2.id)

