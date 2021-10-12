import os


# Dữ liệu nằm ở E:\VLSP\VLSP-2021\Statistic\annotation
# Trong đó bao gồm các folder là tên file gốc (....conll)
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
    # print("ner = ")
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
                # print("new_data = ", new_data)
                for d in new_data:
                    paragraph.append(d)
                # paragraph.append(new_data[:-1])
                data_ner = []
            paragraph.append(data[i])
        else:
            # kiểm tra xem phải cùng dãy thực thể hay k?
            data[i][3] = data[i][3].replace('[', '').replace(']', '')
            data_ner.append(data[i])

    if len(data_ner) != 0:
        new_data = segment_ner(data_ner)
        # print("new_data = ", new_data)
        for d in new_data:
            paragraph.append(d)
        # paragraph.append(new_data[:-1])
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

def clear_paragraph(paragraph):
    # print(paragraph)
    if len(paragraph) > 1:
        new_paragraph = []
        i = 0
        while i < len(paragraph)-1:
            id_word_a = int(paragraph[i][0].split("-")[1])
            id_word_b = int(paragraph[i+1][0].split("-")[1])
            # print(paragraph[i])
            if id_word_a > id_word_b:
                # print("loix ")
                # print(paragraph[i])
                # print(paragraph[i+1])
                new_paragraph.append(paragraph[i+1])
                i+=1
            else:
                new_paragraph.append(paragraph[i])
            i+=1
        id_word_a = int(paragraph[-2][0].split("-")[1])
        id_word_b = int(paragraph[-1][0].split("-")[1])
        if id_word_a > id_word_b:
            new_paragraph = new_paragraph[:-1]
        new_paragraph.append(paragraph[-1])
        return new_paragraph
    else:
        return paragraph

def make_Muc(data):
    text = ""
    # print(data)
    data_paragraph = []
    state = False  # trạng thái này kiểm tra xem có ner trong đoạn hay k?. Khởi tạo là True
    for line in data[4:]:
        line = line.strip()
        # print(line)
        if "#" in line:
            continue
        elif line == '':
            # chia thành 2 trường hợp:
            # Trường hợp 1: Không có nhãn trong đoạn:

            if not state and len(data_paragraph) > 0:
                # print("day")
                paragraph = merge_paragraph_no_ner(data_paragraph)
                text += paragraph

            # Trường hợp 2: Có nhãn trong đoạn:
            else:
                paragraph = merge_paragraph_ner(data_paragraph)
                # print("paragraph = ")
                paragraph = clear_paragraph(paragraph)
                # for p in paragraph:
                #     print(p)
                text += merge_paragraph_no_ner(paragraph)
                # ở đây thực chất là ghép ner vào trong từ sau đó là bỏ phần ner phía sau đi

                # text += paragraph
                state = False

            text += "\n"
            data_paragraph = []

        else:
            # print(line)
            dataframe = line.strip().split('\t')
            p_w = dataframe[0]  # p_w: là paragraph_word
            span = dataframe[1]  # span: vị trí của từ trong text
            span = span.split('-')
            # print(span)
            start = int(span[0])
            end = int(span[1])
            span = [start, end]
            word = dataframe[2]

            if len(dataframe) == 5:
                id_ner = dataframe[3]
                ner = dataframe[4]
                data_paragraph.append([p_w, span, word, id_ner, ner])
                if id_ner != '_':
                    state = True

            if len(dataframe) == 3:
                id_ner = "_"
                ner = "_"
                data_paragraph.append([p_w, span, word, id_ner, ner])
                state = False

    if len(data_paragraph) > 0 and state == False:
        # print("day2")
        paragraph = merge_paragraph_no_ner(data_paragraph)
        text += paragraph
    if len(data_paragraph) > 0 and state == True:
        paragraph = merge_paragraph_ner(data_paragraph)
        # print("paragraph = ")
        paragraph = clear_paragraph(paragraph)
        # for p in paragraph:
        #     print(p)
        text += merge_paragraph_no_ner(paragraph)
    # print(text)
    text += "\n"
    return text


def bubble_sort(arr):
    for i in range(len(arr)):
        for j in range(len(arr)):
            if arr[i][1] > arr[j][1]:
                temp = arr[i]
                arr[i] = arr[j]
                arr[j] = temp
    return arr


def convert(path, path_out):
    data = []

    list_files = os.listdir(path)
    for f in list_files:
        file_name = path + "/" + f
        with open(file_name, "r", encoding="utf-8") as file:
            d = file.readlines()
            # print(d)
            vlsp_2021_text = make_Muc(d)
            file_out = f[:-3] + "muc"
            data.append([file_out, vlsp_2021_text])
            # print(f)
            # # print(path)
            # # write_data("E:/VLSP/VLSP-2021/Data_VLSP_2021/"+f[:-5]+"muc", vlsp_2021_text)
            write_data(path_out+"/" + f[:-3] + "muc", vlsp_2021_text)
            # print(c)
            # print(vlsp_2021_text)
    # print(dict_ner)
    # return data
    pass

def write_data(path, data):
    file = open(path, "w", encoding="utf-8")
    file.write(data)
    file.close()
    print("-->", path)
    pass

def main():
    # path_in = "E:/VLSP/data/Data-TSV"
    # path_out = "E:/VLSP/data/Data-Muc"
    # path_in = "E:/VLSP/data/Data-TSV-Addtion"
    # path_out = "E:/VLSP/data/Data-Muc-Addtion"
    path_in = "E:/VLSP/Data-VLSP-2021-v2/tsv"
    path_out = "E:/VLSP/Data-VLSP-2021-v2/muc"
    convert(path_in, path_out)

    return "DONE!"


if __name__ == '__main__':
    main()
