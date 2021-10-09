import os
import re
import sys
from nltk import word_tokenize

stringRegex = "<ENAMEX TYPE[^>]*>([^<]*)</ENAMEX>"
nestStringRegex = "<ENAMEX TYPE[^>]*>([^<]*<ENAMEX TYPE[^>]*>([^<]*<ENAMEX TYPE[^>]*>([^<]*<ENAMEX TYPE[^>]*>[^<]*</ENAMEX>[^<]*|[^<]*)*</ENAMEX>[^<]*|[^<]*)*</ENAMEX>[^<]*)*</ENAMEX>"


def split_tokenize(sentence):
    nestData = []
    regex = re.compile(stringRegex)
    nestRegex = re.compile(nestStringRegex)

    i = 0
    while nestRegex.search(sentence, i) is not None:
        regexMatcher = nestRegex.search(sentence, i)
        if regexMatcher is not None:
            nestData.append(sentence[i:regexMatcher.start()])
            nestData.append(regexMatcher.group())
            i = regexMatcher.end() + 1
    if i != len(sentence):
        nestData.append(sentence[i:])
    # print("nestData:", nestData)
    data = []
    for d in nestData:
        i = 0
        while regex.search(d, i) is not None:
            # print("có")
            if nestRegex.search(d, i) is not None:
                data.append(d)
                i = len(d)
                break
            else:
                regexMatcher = regex.search(d, i)
                if regexMatcher is not None:
                    data.append(d[i:regexMatcher.start()])
                    data.append(regexMatcher.group())
                    # print(c.group())
                    i = regexMatcher.end() + 1
        if i != len(d):
            data.append(d[i:])

    tokens = []
    for d in data:
        if "<ENAMEX" in d:
            tokens.append(d)
        else:
            for w in word_tokenize(d):
                tokens.append(w)
        # print(d)
    # for t in tokens:
    #     print(t)
    return tokens

def merger_nest_entities(sentence):
    nestData_sent = []
    regex = re.compile(stringRegex)
    regexMatcher = regex.search(sentence)
    textMatch = regexMatcher.group()
    g = "<ENAMEX TYPE=\"([^<]*)\">"
    e = re.compile(g)
    labeledEntity = e.search(textMatch)
    # print(regexMatcher.groups()[0], "\t", labeledEntity.groups()[0])

    ws = word_tokenize(regexMatcher.groups()[0])
    nestData_sent.append([ws[0], "B-" + labeledEntity.groups()[0]])
    textMerger = ws[0] + "_" + "B-" + labeledEntity.groups()[0] + " "
    for w in range(1, len(ws)):
        nestData_sent.append([ws[w], "I-" + labeledEntity.groups()[0]])
        textMerger += ws[w] + "_" + "I-" + labeledEntity.groups()[0] + " "

    # print(textMatch)

    return textMatch, textMerger[:-1], nestData_sent

def make_text(data):
    text = ""
    for d in data:
        for w in d:
            line = w[0] + "\t_" + "\t_"
            for e in w[1]:
                line += "\t" + e
            text += line + "\n"

        text += "\n"
    return text

def make_form(data):
    new_data = []
    num_maximum_entities = 0
    for d in data:
        # print("sentence = ",d)
        tokens = split_tokenize(d)
        # this token includes the word(raw text), ner(not nested) and nested ner.
        # định dạng ConLL 2003 gồm:
        # cột 0     cột 1       cột 2           cột 3       cột 4->>>
        # word      POS(k có)   Phrase(k có)    NER_main    Ner_extension
        data_sent = []
        for token in tokens:
            # print("token = ", token)
            # xử lý thực thể
            if "<ENAMEX" in token:
                nestRegex = re.compile(nestStringRegex)
                regex = re.compile(stringRegex)
                # thực thể đơn
                # print(nestRegex.search(token))
                if nestRegex.search(token) is None:
                    # print("-> Nhãn đơn: ")
                    regexMatcher = regex.search(token)

                    textMatch = regexMatcher.group()
                    g = "<ENAMEX TYPE=\"([^<]*)\">"
                    e = re.compile(g)
                    labeledEntity = e.search(textMatch)

                    # print(regexMatcher.groups()[0], "\t", labeledEntity.groups()[0])
                    ws = word_tokenize(regexMatcher.groups()[0])
                    data_sent.append(ws[0] + "_" + "B-"+labeledEntity.groups()[0])
                    for w in range(1, len(ws)):
                        data_sent.append(ws[w] + "_" + "I-" + labeledEntity.groups()[0])

                # thực thể lồng ghép
                else:
                    # tái sử dụng hàm split_tokenize(sentence)
                    # print("---> Nhãn lồng: ")
                    # print(nestRegex.search(token).groups()[0])
                    if nestRegex.search(token).groups()[0] is None:
                        print(token)
                        # continue
                        sys.exit("Error: NER is not exits")

                    while nestRegex.search(token) is not None and regex.search(token) is not None:
                        textMatch, textMerger, nestData_sent = merger_nest_entities(token)
                        # print("textMatch = ",textMatch)

                        g = token.replace(textMatch, textMerger)
                        # print("g = ", g)
                        token = g

                    textMatch, textMerger, nestData_sent = merger_nest_entities(token)
                    for d_s in nestData_sent:
                        data_sent.append(d_s[0]+"_"+d_s[1])
                        # print(d_s[0]+"_"+d_s[1])

            else:
                data_sent.append(token)
        pass

        for i in range(len(data_sent)):
            labeledEntities = data_sent[i].split("_")

            word = labeledEntities[0]
            entities = labeledEntities[1:]
            # print(word, entities)
            if num_maximum_entities < len(entities):
                num_maximum_entities = len(entities)
            entities = entities[::-1]

            data_sent[i] = [word, entities]
        pass
        new_data.append(data_sent)
        # split_tokenize(d, nestStringRegex)
        # print()

    for i in range(len(new_data)):
        for j in range(len(new_data[i])):
            # print(new_data[i])
            while len(new_data[i][j][1]) < num_maximum_entities:
                new_data[i][j][1].append("O")

    return make_text(new_data)


def get_sentence_origin(sentence):
    # tách các thành phần có chứa "<ENAMEX .." ra khỏi câu:
    return re.sub(r'<ENAMEX TYPE="[A-Z|\-]*">|</ENAMEX>', '', sentence).strip(" ").replace("  ", " ")


def read_input_file(filename):
    if os.path.isfile(filename):
        print(filename)
    with open(filename, "r", encoding="utf-8") as f:
        text = []
        lines = f.readlines()
        for i in range(0, len(lines)):
            line = lines[i].strip("\n")
            # if line != "":
            text.append(line)
            # text += lines[i]

        return text


def write_output_file(filename, text):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)


def convert(path_in, path_out):
    list_files = os.listdir(path_in)
    if not os.path.exists(path_out):
        os.mkdir(path_out)
    for file in list_files:
        file_path = path_in + "/" + file
        data = read_input_file(file_path)
        output = make_form(data)
        file_out = path_out + "/" + file[:-3] + "conll"
        write_output_file(file_out, output)

    print("Done!")


if __name__ == '__main__':
    '''file'''
    # data = "E:/VLSP/data/Data-Muc/kinhte_0004.muc"
    # doc = read_input_file(data)
    # doc = make_form(doc)
    # write_output_file("E:/VLSP/data/Data-test/kinhte_0004.conll", doc)

    '''folder'''
    path_in = "E:/VLSP/data/Data-Muc"
    path_out = "E:/VLSP/data/Data-test"
    convert(path_in, path_out)

    pass
