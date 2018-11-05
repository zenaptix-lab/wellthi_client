import os

known_files = []


def detect_file(watch_folder_path):
    files = os.listdir(watch_folder_path)
    for f in files:
        if f not in known_files:
            print("let's kick off the processing of file: " + f)
            start_hrv_processing(f)
            known_files.append(f)


def start_hrv_processing(file_path):
    print("Starting processing file: " + file_path)
    result = 1
    print(result)


while True:
    detect_file("/Users/mouritsdebeer/Desktop/watchme")
