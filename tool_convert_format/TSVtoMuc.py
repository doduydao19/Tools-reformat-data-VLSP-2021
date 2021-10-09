import os
def process_case_3(data):
    # print("trước khi")
    seg = "<ENAMEX TYPE=\"" + data[0][4][:data[0][4].find('[')] + "\">"
    for i in range(len(data)):
        if '|' in data[i][3]:
            data[i][3] = "*" + data[i][3][data[i][3].find('|') + 1:]
            data[i][4] = data[i][4][data[i][4].find('|') + 1:]
        else:
            data[i][3] = '_'
            data[i][4] = '_'
    new_data = merge_paragraph_ner(data)
    seg += merge_paragraph_no_ner(new_data)
    # print(merge_paragraph_ner(data))
    seg += "</ENAMEX>"

    p_w = data[0][0]  # p_w: là paragraph_word
    start = data[0][1][0]
    end = data[-1][1][1]
    span = [start, end]
    word = seg
    id_ner = "_"
    ner = "_"
    new_data = [p_w, span, word, id_ner, ner]
    return new_data


def process_case_2(data):
    seg = "<ENAMEX TYPE=\"" + data[0][4][:data[0][4].find('[')] + "\">"
    for i in range(len(data)):
        data[i][3] = "_"
        data[i][4] = "_"
    seg += merge_paragraph_no_ner(data)
    seg += "</ENAMEX>"

    # tiến hành gộp lại
    # print(data)
    p_w = data[0][0]  # p_w: là paragraph_word
    start = data[0][1][0]
    end = data[-1][1][1]
    span = [start, end]
    word = seg
    id_ner = "_"
    ner = "_"
    new_data = [p_w, span, word, id_ner, ner]
    # print(new_data)
    return new_data


def segment_ner(data):
    seg = []
    matrix = []
    matrix_extend = []
    id = 0
    state = False
    # kiểm tra xem thuộc trường hợp nào?
    for i in range(len(data)):
        # print(data[i])
        if data[i][3] == '*':
            # print("--->Case 1",data[i])
            # seg += "<ENAMEX TYPE=\"" + data[i][4] + "\">"+ data[i][2] + "</ENAMEX>"
            data[i][2] = "<ENAMEX TYPE=\"" + data[i][4] + "\">" + data[i][2] + "</ENAMEX>"
            data[i][3] = "_"
            data[i][4] = "_"
            seg.append(data[i])

        else:
            if '|' not in data[i][3]:
                temp = int(data[i][3].replace('*', ''))
                if temp > id:
                    id = temp
                    if len(matrix) > 0:
                        # print("--->Case 2")
                        seg.append(process_case_2(matrix))

                        # print(seg)
                        matrix = [data[i]]
                    else:
                        matrix.append(data[i])
                elif temp < id:
                    continue
                else:
                    matrix.append(data[i])

            if '|' in data[i][3]:
                list_id_ner = data[i][3].replace('*', '').split('|')
                # nếu id thuộc vào trong list dưới thì có nghĩa là thuộc vào trường hợp 3
                if str(id) in list_id_ner and state == False:
                    state = True
                    for e in matrix:
                        matrix_extend.append(e)
                    matrix = []
                matrix_extend.append(data[i])

    if len(matrix) > 0 and state == False:
        # print("--->Case 2")
        seg.append(process_case_2(matrix))
        # print(seg)

    if len(matrix_extend) > 0 or state == True:
        # print("--->Case 3")
        for e in matrix:
            matrix_extend.append(e)
        seg.append(process_case_3(matrix_extend))

    # print("Seg = ", seg)
    return seg


def merge_paragraph_ner(data):
    # print("data = ", data)
    paragraph = []
    data_ner = []
    for i in range(0, len(data)):
        # tách phần k có thực thể ra:
        if data[i][3] == "_":
            # xử lí phần dữ liệu có ner trc đó:
            if len(data_ner) != 0:
                new_data = segment_ner(data_ner)
                for d in new_data:
                    paragraph.append(d)
                data_ner = []
            paragraph.append(data[i])
        else:
            # kiểm tra xem phải cùng dãy thực thể hay k?
            data[i][3] = data[i][3].replace('[', '').replace(']', '')
            data_ner.append(data[i])

    if len(data_ner) != 0:
        new_data = segment_ner(data_ner)
        for d in new_data:
            paragraph.append(d)

    return paragraph


def merge_paragraph_no_ner(data):
    paragraph = ""

    for i in range(0, len(data) - 1):
        word = data[i][2]
        span = data[i][1]
        end = span[1]

        span_a = data[i + 1][1]
        start_a = span_a[0]

        # Tại đây chia ra 2 trường hợp:
        # th1: các từ đơn lẻ k có dấu câu: (đồng nghĩa với kết thúc từ này k trùng với bắt đầu từ phía sau)
        if end != start_a:
            paragraph += word + " "
        # th2: các từ đơn lẻ với dấu câu hoặc từ dính liền nhau: (đồng nghĩa với kết thúc từ này trùng với bắt đầu từ
        # phía sau)
        else:
            paragraph += word
    # print(data)
    paragraph += data[-1][2]

    # print(paragraph)
    return paragraph


def make_form_muc(data_tsv):
    text = ""

    for paragraph in data_tsv:
        max_no_ner = 0
        paragraph_data = []
        for word in paragraph:
            line_data = word.split("\t")
            # print(line_data)
            ners = []
            if line_data[3] != "_":
                ners = line_data[4].split("|")
                if max_no_ner < len(ners):
                    max_no_ner = len(ners)
            word = line_data[2]
            span = line_data[1].split('-')
            # print(span)
            start = int(span[0])
            end = int(span[1])
            span = [start, end]
            paragraph_data.append([span, word, ners])
        # print(max_no_ner)
        # print(paragraph_data)
        for p in range(len(paragraph_data)):

            while len(paragraph_data[p][2]) < max_no_ner:
                paragraph_data[p][2].append('_')
            # print(paragraph_data[p])

        state = True
        id_temp = 0
        for i in reversed(range(max_no_ner)):
            id_temp = 0
            for j in range(len(paragraph_data)):
                ner = paragraph_data[j][2][i]
                if "_" not in ner:
                    print(paragraph_data[j])
                    if "[" in ner:
                        id_ner_a = int(ner[ner.find("[") + 1: -1])
                        if id_temp == id_ner_a:
                            continue
                        else:
                            print(str(paragraph_data[j][1]) + "</ENAMEX>")
                        print("<ENAMEX TYPE=\"" + str(ner) + "\">" + paragraph_data[j][1])
                    else:
                        print("<ENAMEX TYPE=\"" + str(ner) +"\">"+ paragraph_data[j][1] + "</ENAMEX>")
                paragraph_data[j][2] = paragraph_data[j][2][:-1]


            print()
        print()
    return text



def convert(path_in, path_out):
    list_files = os.listdir(path_in)
    for f in list_files:
        path_file = path_in + "/" + f
        data_tsv = read_data(path_file)
        vlsp_2021_text = make_form_muc(data_tsv)
        file_name_out = f[:-3] + "muc"
        # write_data(path_out +"/" + file_name_out, vlsp_2021_text)
        print("-->", file_name_out)
        break
    return "DONE!"

def read_data(path):
    data = []
    with open(path, "r", encoding="utf-8") as file:
        paragraph = []
        lines = file.readlines()
        for line in lines[4:]:
            line = line.strip()
            # print(line)
            if "#" in line:
                continue
            elif line == '' and paragraph != []:
                data.append(paragraph)
                paragraph = []
            else:
                paragraph.append(line)
    data.append(paragraph)
    return data

def write_data(path, data):
    file = open(path, "w", encoding="utf-8")
    file.write(data)
    file.close()

def bubble_sort(arr):
    for i in range(len(arr)):
        for j in range(len(arr)):
            if arr[i][1] > arr[j][1]:
                temp = arr[i]
                arr[i] = arr[j]
                arr[j] = temp
    return arr

if __name__ == '__main__':
    path_in = "E:/VLSP/Data-VLSP-2021/Data-TSV"
    path_out = "E:/VLSP/Data-VLSP-2021/Data-Muc"
    convert(path_in, path_out)
    print("Done!")
