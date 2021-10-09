import os


def make_text(data, max_no_ner):
    paragraph = ""

    for word in data:
        struct_inline = []
        # nếu thực thể chỉ có 1 phần thì không có dấu * ở hay đánh số tăng lên
        if type(word) is list:

            w = word[0]
            pos = "_"
            phrase = "_"
            struct_inline.append(w)
            struct_inline.append(pos)
            struct_inline.append(phrase)
            for i in range(0, max_no_ner):
                if i < len(word[1]):
                    struct_inline.append(word[1][i])
                else:
                    struct_inline.append("O")
        else:
            pos = "_"
            phrase = "_"
            struct_inline.append(word)
            struct_inline.append(pos)
            struct_inline.append(phrase)

            for i in range(0, max_no_ner):
                struct_inline.append("O")
        line = ""
        for i in struct_inline:
            line += i + "\t"
        paragraph += line.strip() + "\n"

    # print(paragraph.strip())
    return paragraph


def read_data_tsv_format(data):
    result = []
    data_paragraph = []
    for line in data[4:]:
        line = line.strip()
        # print(line)
        if "#" in line:
            continue
        elif line == '':
            result.append(data_paragraph)
            data_paragraph = []
        else:
            dataframe = line.strip().split('\t')
            word = dataframe[2]
            if len(dataframe) == 5:
                ner = dataframe[4]
                data_paragraph.append([word, ner])

            if len(dataframe) == 3:
                ner = "_"
                data_paragraph.append([word, ner])

    if len(data_paragraph) > 0:
        result.append(data_paragraph)

    # for i in result:
    #     print(i)
    return result


def write_data_conll2003_format(data):
    max_no_ner = 0
    id_ner = 0
    for p in range(len(data)):
        for w in range(len(data[p])):
            if data[p][w][1] == "_":
                data[p][w] = data[p][w][0]
            else:
                list_ners = data[p][w][1].split('|')
                if max_no_ner < len(list_ners):
                    max_no_ner = len(list_ners)
                new_list_ners = []
                for i in range(len(list_ners)):
                    if "[" in list_ners[i]:
                        # print(list_ners[i])
                        temp_id_ner = int(list_ners[i][list_ners[i].find('[') + 1:-1])
                        ner = list_ners[i][:list_ners[i].find('[')]

                        if id_ner < temp_id_ner:
                            id_ner = temp_id_ner
                            new_list_ners.append("B-" + ner)
                        else:
                            new_list_ners.append("I-" + ner)

                    else:
                        new_list_ners.append("B-" + list_ners[i])
                data[p][w][1] = new_list_ners
        # print(data[p])
        # print()

    content = ""
    for p in data:
        content += make_text(p, max_no_ner) + "\n"

    return content


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
        data = read_data_tsv_format(data)
        content = write_data_conll2003_format(data)
        # print(content)
        write_data(path_out + "/" + f[:-3] + "conll", content)
        print("-->", f[:-3] + "conll")


if __name__ == '__main__':
    path_in = "E:/VLSP/data/Data-TSV"
    path_out = "E:/VLSP/data/Data-Conll"
    convert(path_in, path_out)
    print("DONE!")
