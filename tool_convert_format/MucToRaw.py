import os
import re

def get_sentence_origin(sentence):
    # tách các thành phần có chứa "<ENAMEX .." ra khỏi câu:
    return re.sub(r'<ENAMEX TYPE="[A-Z|\-]*">|</ENAMEX>', '', sentence).strip(" ").replace("  ", " ")

def write_data_muc_format(data):
    text = ""

    for line in data:
        text += get_sentence_origin(line)
    return text


def read_file(path):
    with open(path, "r", encoding="utf-8") as file:
        d = file.readlines()
        return d

def write_data(path, data):
    file = open(path, "w", encoding="utf-8")
    file.write(data)
    file.close()
    return

def convert(path_in, path_out):
    list_files = os.listdir(path_in)
    for f in list_files:
        path_file = path_in + "/" + f
        data = read_file(path_file)
        content = write_data_muc_format(data)
        # print(content)
        write_data(path_out + "/" + f[:-3] + "txt", content)
        print("-->",f[:-3] + "txt")


if __name__ == '__main__':
    path_in = "E:/VLSP/data/Data-Muc"
    path_out = "E:/VLSP/data/Data-Raw"
    convert(path_in, path_out)
    print("DONE!")
