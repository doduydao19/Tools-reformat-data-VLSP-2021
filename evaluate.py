import re
import os
import sys

stringRegex = "<ENAMEX TYPE[^>]*>([^<]*)</ENAMEX>"
nestStringRegex = "<ENAMEX TYPE[^>]*>([^<]*<ENAMEX TYPE[^>]*>([^<]*<ENAMEX TYPE[^>]*>([^<]*<ENAMEX TYPE[^>]*>[^<]*</ENAMEX>[^<]*|[^<]*)*</ENAMEX>[^<]*|[^<]*)*</ENAMEX>[^<]*)*</ENAMEX>"
list_ner = ['ADDRESS', 'DATETIME', 'DATETIME-DATE', 'DATETIME-DATERANGE',
            'DATETIME-DURATION', 'DATETIME-SET', 'DATETIME-TIME',
            'DATETIME-TIMERANGE', 'EMAIL', 'EVENT', 'EVENT-CUL',
            'EVENT-GAMESHOW', 'EVENT-NATURAL', 'EVENT-SPORT', 'IP',
            'LOCATION', 'LOCATION-GEO', 'LOCATION-GPE', 'LOCATION-STRUC',
            'MISCELLANEOUS', 'ORGANIZATION', 'ORGANIZATION-MED', 'ORGANIZATION-SPORTS',
            'ORGANIZATION-STOCK', 'PERSON', 'PERSONTYPE', 'PHONENUMBER', 'PRODUCT',
            'PRODUCT-COM', 'PRODUCT-LEGAL', 'QUANTITY', 'QUANTITY-AGE', 'QUANTITY-CUR',
            'QUANTITY-DIM', 'QUANTITY-NUM', 'QUANTITY-ORD', 'QUANTITY-PER', 'QUANTITY-TEM',
            'SKILL', 'URL']


# list_ner =["PERSON", "ORGANIZATION", "LOCATION"]

def get_content(file_path):
    if not os.path.exists(file_path):
        sys.exit("An error occurred while opening the file", file_path)
    with open(file_path, "r", encoding='utf-8') as f:
        content = f.read()
    return content
    pass


def get_original(content):
    # tách các thành phần có chứa "<ENAMEX .." ra khỏi câu:
    return re.sub(r'<ENAMEX TYPE="[A-Z|\-]*">|</ENAMEX>', '', content).strip(" ").replace("  ", " ")
    pass


def findStringRegex(text, rule):
    matchList = dict()
    regex = re.compile(rule)
    id = 0
    while regex.search(text, id) is not None:
        regexMatcher = regex.search(text, id)
        # print(regexMatcher.group())
        matchList[regexMatcher.start()] = regexMatcher.group()
        id = regexMatcher.end() + 1
    return matchList
    pass


def extractEntities(original_content, labeled_content):
    entities = dict()
    labeledEntities = findStringRegex(labeled_content, stringRegex)

    nestedEntities = dict()
    labeledNestedEntities = findStringRegex(labeled_content, nestStringRegex)

    # print("labeledEntities =",labeledEntities)
    # print("labeledNestedEntities =",labeledNestedEntities)
    index = 0
    for key in labeledNestedEntities.keys():
        entity = get_original(labeledNestedEntities.get(key))
        # print(entity)
        type = ""
        for e in list_ner:
            e_full = "<ENAMEX TYPE=\"" + e + "\">"
            if labeledNestedEntities.get(key).startswith(e_full):
                # print("e_full = ", e_full)
                type = e

        begin_entity = original_content.find(entity, index)
        end_entity = begin_entity + len(entity)
        index = end_entity
        # print(begin_entity)
        nestedEntities[str(begin_entity) + "_" + str(end_entity) + "_" + type + "_" + "outer"] = entity
        entities[str(begin_entity) + "_" + str(end_entity) + "_" + type + "_" + "outer"] = entity

    index = 0
    for key in labeledEntities.keys():
        entity = get_original(labeledEntities.get(key))

        type = ""
        for e in list_ner:
            e_full = "<ENAMEX TYPE=\"" + e + "\">"
            if labeledEntities.get(key).startswith(e_full):
                type = e
        begin_entity = original_content.find(entity, index)
        end_entity = begin_entity + len(entity)
        index = end_entity

        flag = False
        for props in nestedEntities.keys():
            props = props.split('_')
            if int(props[0]) <= begin_entity and int(props[1]) >= end_entity:
                entities[str(begin_entity) + "_" + str(end_entity) + "_" + type + "_" + "inner"] = entity
                flag = True
                break
        if not flag:
            entities[str(begin_entity) + "_" + str(end_entity) + "_" + type + "_" + "outer"] = entity

    return entities
    pass

def print_table(table_scores, table_F_score):
    total_TP = 0
    total_TP_FP = 0
    total_TP_FN = 0
    header = ["NER", "TP", "TP+FP", "TP+FN", "P", "R", "F1"]
    for i in header:
        print(i, end="\t\t\t")
    print()
    for i in range(len(table_scores)):
        print(list_ner[i], end="\t\t\t")
        for j in table_scores[i]:
            print(j, end="\t\t")
        for j in table_F_score[i]:
            print(j, end="\t\t")
        print()
        total_TP += table_scores[i][0]
        total_TP_FP += table_scores[i][1]
        total_TP_FN += table_scores[i][2]

        # print(table_scores[i], table_F_score[i])

    if total_TP_FP == 0:
        P = 0
    else:
        P = total_TP / total_TP_FP
    if total_TP_FP == 0:
        R = 0
    else:
        R = total_TP / total_TP_FN
    if P == R == 0:
        F = 0
    else:
        F = 2 * P * R / (P + R)
    print("--->Overall:" + "\t" + str(total_TP) + "\t" + str(total_TP_FP) + "\t" + str(total_TP_FN) + "\t" + str(P) + "\t" + str(R) + "\t" + str(F))
    pass

def get_scores(table_scores):
    table_F_score = []
    for i in range(len(list_ner)):
        table_F_score.append([0.0, 0.0, 0.0])
    for i in range(len(table_scores)):
        # P:
        if table_scores[i][1] == 0:
            table_F_score[i][0] = 0
        else:
            table_F_score[i][0] = float(table_scores[i][0] / table_scores[i][1])
        # R:
        if table_scores[i][2] == 0:
            table_F_score[i][1] = 0
        else:
            table_F_score[i][1] = float(table_scores[i][0] / table_scores[i][2])
        # F:
        if table_F_score[i][0] != 0 and table_F_score[i][1] != 0:
            table_F_score[i][2] = 2 * table_F_score[i][0] * table_F_score[i][1] / (
                    table_F_score[i][0] + table_F_score[i][1])
    return table_F_score

def evaluate(path_test, path_anno, toplevel):
    score_total = [0, 0, 0, 0, 0, 0]
    if not os.path.exists(path_test):
        sys.exit("An error occurred while opening the folder test data")
    if not os.path.exists(path_anno):
        sys.exit("An error occurred while opening the the folder annotation data")

    total_scores = []
    for i in range(len(list_ner)):
        total_scores.append([0, 0, 0])

    subFolders = os.listdir(path_anno)
    for subFolder in subFolders:
        print("-----------------------------")
        print(subFolder)
        print("-----------------------------")

        table_scores = []
        for i in range(len(list_ner)):
            table_scores.append([0, 0, 0])

        path_anno_subFolder = path_anno + "/" + subFolder
        list_anno_files = os.listdir(path_anno_subFolder)

        path_test_subFolder = path_test + "/" + subFolder
        list_test_files = os.listdir(path_test_subFolder)

        if len(list_anno_files) != len(list_test_files):
            sys.exit("The number of files in two folder is not equal.")
        else:
            for i in range(len(list_anno_files)):
                labeledFile = list_anno_files[i]
                labeled_content = get_content(path_anno_subFolder + "/" + labeledFile)
                testFile = list_test_files[i]
                test_content = get_content(path_test_subFolder + "/" + testFile)
                original_content = get_original(labeled_content)

                testEntities = extractEntities(original_content, test_content)
                annEntities = extractEntities(original_content, labeled_content)

                # count TP+FP
                for key in testEntities.keys():
                    key = key.split('_')
                    if toplevel:
                        if key[3] == "inner":
                            continue
                    for j in range(len(list_ner)):
                        if key[2] == list_ner[j]:
                            table_scores[j][1] += 1
                # count TP+FN
                for key in annEntities.keys():
                    key = key.split('_')
                    # print(key)
                    if toplevel:
                        if key[3] == "inner":
                            continue
                    for j in range(len(list_ner)):
                        if key[2] == list_ner[j]:
                            table_scores[j][2] += 1
                # count TP
                for key1 in annEntities.keys():
                    key_1 = key1.split('_')
                    for key2 in testEntities.keys():
                        key_2 = key2.split('_')
                        if toplevel:
                            if key_2[3] == "inner":
                                continue
                        for j in range(len(list_ner)):
                            if key_1[0] == key_2[0] and \
                                    key_1[1] == key_2[1] and \
                                    key_1[2] == key_2[2] and \
                                    annEntities.get(key1) == testEntities.get(key2) and \
                                    key_1[2] == list_ner[j]:
                                table_scores[j][0] += 1

        table_F_score = get_scores(table_scores)
        print_table(table_scores, table_F_score)

        for i in range(len(total_scores)):
            for j in range(len(total_scores[i])):
                total_scores[i][j] += table_scores[i][j]
    print("\n-----------------------------")
    print("Total Evaluation")
    print("-----------------------------")
    table_F_score = get_scores(total_scores)
    print_table(total_scores, table_F_score)

    return
    pass


if __name__ == '__main__':
    path_test = "E:/VLSP/Evaluate/Test"
    path_anno = "E:/VLSP/Evaluate/Ann"

    print("=====================Top-level evaluation=====================")
    evaluate(path_test, path_anno, toplevel=True)

    print("\n=====================Nested evaluation=====================")
    evaluate(path_test, path_anno, toplevel=False)

    print("Evaluate completed!")
