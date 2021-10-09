# Dữ liệu nằm ở E:\VLSP\VLSP-2021\Statistic\annotation
# Trong đó bao gồm các folder là tên file gốc (....conll)
# yêu cầu đầu vào : gồm 2 file: 1 file định dạng conll và 1 fild dữ liệu gốc chưa gán NER

import os
import re
import string

def merge_paragraph_ner(data):
    state = True
    # print(data)
    # print(data)
    max_no_ners = len(data[0][2])
    for i in reversed(range(max_no_ners)):
        for j in range(len(data)):
            ner = data[j][2][i]
            if "B-" in ner:
                if state:
                    state = False
                else:
                    data[j-1][1] += "</ENAMEX>"
                    # print(data[j-1][1])
                data[j][1] = "<ENAMEX TYPE=\"" + ner[2:] + "\">" + data[j][1]
                # print(data[j][1])
            elif "I-" in ner:
                # print("***", data[j][1])
                continue
            else:
                if not state:
                    data[j-1][1] += "</ENAMEX>"
                    # print(data[j-1][1])
                state = True
    if not state:
        data[-1][1] += "</ENAMEX>"
    paragraph = merge_paragraph_no_ner(data)
    return paragraph

def merge_paragraph_no_ner(data):
    paragraph = ""
    for i in range(0, len(data) - 1):
        # print(data[i])
        word = data[i][1]
        span = data[i][0]
        end = span[1]

        span_after = data[i + 1][0]
        start_after = span_after[0]

        # Tại đây chia ra 2 trường hợp:
        # th1: các từ đơn lẻ k có dấu câu: (đồng nghĩa với kết thúc từ này k trùng với bắt đầu từ phía sau)
        if end != start_after:
            paragraph += word + " "
        # th2: các từ đơn lẻ với dấu câu hoặc từ dính liền nhau: (đồng nghĩa với kết thúc từ này trùng với bắt đầu từ
        # phía sau)
        else:
            paragraph += word
    # print(data)
    paragraph += data[-1][1]
    # print(paragraph)
    return paragraph

def clean_text(sentence):
    if "<ENAMEX TYPE=" in sentence:
        return re.sub(r'<ENAMEX TYPE="[A-Z|\-]*">|</ENAMEX>', '', sentence).strip(" ").replace("  ", " ")
    else:
        return sentence

def reformat(data_conll, data_org):
    text = ""
    id = 0
    for i in range(len(data_org)):
        paragraph = data_org[i]
        list_words = data_conll[i]
        index = 0
        paragraph = clean_text(paragraph)
        # print(paragraph)
        data = []
        for w in range(len(list_words)):
            token = list_words[w].split("\t")[0]
            ners = list_words[w].split("\t")[3:]

            if token not in string.punctuation:

                if token[0] in string.punctuation:
                    temp = "\\" + token
                    pattern = re.compile(temp)
                else:
                    pattern = re.compile(token)

            else:
                temp = "\\" + token
                pattern = re.compile(temp)

            match = pattern.search(paragraph, index)
            # print(match)
            if match is not None:
                start = match.start()
                end = match.end()
                index = end
                span = [id+start, id+end]

                # p_w = [i + 1, w + 1]
                data.append([span, token, ners])
                # print(p_w, span, token,ners)

        text += merge_paragraph_ner(data) + "\n"
        id += len(paragraph) + 1

    return text

def read_data(path_file):
    data = []
    if path_file[-5:] == "conll":
        with open(path_file, "r", encoding="utf-8") as file:
            sent = []
            for line in file:
                line = line.strip()
                if line != "":
                    sent.append(line)
                else:
                    data.append(sent)
                    sent = []

    elif path_file[-3:] == "txt":
        with open(path_file, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line != "":
                    data.append(line)
    else:
        return
    return data

def convert(path_conll, path_muc, path_out):
    data = []
    files_conll = os.listdir(path_conll)
    files_muc = os.listdir(path_muc)

    if len(files_conll) != len(files_muc):
        return "Lỗi"
    else:
        for i in range(len(files_conll)):
            path_file_conll = path_conll + "/" + files_conll[i]
            path_file_muc = path_muc + "/" + files_muc[i]

            data_conll = read_data(path_file_conll)
            data_org = read_data(path_file_muc)

            if len(data_conll) == 0 and len(data_org) == 0:
                return
            else:
                # print(data_conll)
                # print(data_org)
                print(files_conll[i])
                muc_text_converted = reformat(data_conll, data_org)
                # data.append([files_conll[i], muc_text_converted])
                write_data(path_out + "/" + files_conll[i][:-5] + "muc", muc_text_converted)
    return data

def write_data(path, data):
    file = open(path, "w", encoding="utf-8")
    file.write(data)
    file.close()


if __name__ == '__main__':
    path_folder_Muc_org = "E:/VLSP/Data-VLSP-2021/Data-Raw"
    path_folder_ConLL = "E:/VLSP/Data-VLSP-2021/Data-Conll2003"
    path_out = "E:/VLSP/Data-VLSP-2021/Data-Mucv2"
    convert(path_folder_ConLL, path_folder_Muc_org, path_out)
    print("DONE!")
