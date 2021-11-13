import re
import os
import sys
import numpy as np

stringRegex = "<ENAMEX TYPE[^>]*>[^<]+</ENAMEX>"
nestStringRegex = "<ENAMEX TYPE[^>]*>([^<]*<ENAMEX TYPE[^>]*>([^<]*<ENAMEX TYPE[^>]*>([^<]*<ENAMEX TYPE[^>]*>[^<]+</ENAMEX>[^<]*|[^<]+)</ENAMEX>[^<]*|[^<]*)*</ENAMEX>[^<]*)*</ENAMEX>"
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
        print(file_path)
        sys.exit("An error occurred while opening the file")
    with open(file_path, "r", encoding='utf-8') as f:
        content = f.read()
    return content
    pass


def get_original(content):
    # tách các thành phần có chứa "<ENAMEX .." ra khỏi câu:
    # return re.sub(r'<ENAMEX TYPE="[A-Z|\-]*">|</ENAMEX>', '', content)
    return re.sub(r'<ENAMEX TYPE="[A-Z|\-]*">|</ENAMEX>', '', content).strip(" ").replace("  ", " ")
    pass


def findStringRegex(text, rule):
    matchList = dict()
    regex = re.compile(rule)
    # id = 0
    # while regex.search(text, id) is not None:
    #     regexMatcher = regex.search(text, id)
    #     # print(regexMatcher.group())
    #     matchList[regexMatcher.start()] = regexMatcher.group()
    #     id = regexMatcher.end() + 1


    id = len(text)
    while id > -1:
        if regex.search(text, id) is not None:
            regexMatcher = regex.search(text, id)
            matchList[regexMatcher.start()] = regexMatcher.group()
        id = id - 1
    # print(matchList)
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
    # print(entities)
    return entities
    pass

def print_table(table_scores, table_F_score):
    total_TP = 0
    total_TP_FP = 0
    total_TP_FN = 0
    header = ["NER", "TP", "TP+FP", "TP+FN", "P", "R", "F1"]

    print("%-20s%-10s%-10s%-10s%-10s%-10s%-10s" % (
    header[0], header[1], header[2], header[3], header[4], header[5], header[6]))

    for i in range(len(table_scores)):
        print("%-20s%-10d%-10d%-10d%-10.4f%-10.4f%-10.4f" % (
        list_ner[i], table_scores[i][0], table_scores[i][1], table_scores[i][2], table_F_score[i][0],
        table_F_score[i][1], table_F_score[i][2]))

        total_TP += table_scores[i][0]
        total_TP_FP += table_scores[i][1]
        total_TP_FN += table_scores[i][2]

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

    print("%-20s%-10d%-10d%-10d%-10.4f%-10.4f%-10.4f" % ("--->Overall", total_TP, total_TP_FP, total_TP_FN, P, R, F))
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

                if labeledFile != testFile:
                    sys.exit("The annotation file is not equal to test file")
                else:
                    # print("testEntities")
                    testEntities = extractEntities(original_content, test_content)
                    # print("annEntities")
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
                    # print("TP:")

                    # print("annot:", annEntities.keys())
                    # print("test:", testEntities.keys())
                    for key1 in annEntities.keys():
                        key_1 = key1.split('_')
                        for key2 in testEntities.keys():
                            key_2 = key2.split('_')
                            if toplevel:
                                if key_2[3] == "outer":
                                    continue
                            for j in range(len(list_ner)):
                                if key_1[0] == key_2[0] and \
                                        key_1[1] == key_2[1] and \
                                        key_1[2] == key_2[2] and \
                                        key_1[3] == key_2[3] and \
                                        annEntities.get(key1) == testEntities.get(key2) and \
                                        key_1[2] == list_ner[j]:
                                    table_scores[j][0] += 1
                            # print(key_2)
        table_F_score = get_scores(table_scores)
        print_table(table_scores, table_F_score)

        for i in range(len(total_scores)):
            for j in range(len(total_scores[i])):
                total_scores[i][j] += table_scores[i][j]
    print("\n-----------------------------")
    print("Total evaluation of test")
    print("-----------------------------")
    table_F_score = get_scores(total_scores)
    print_table(total_scores, table_F_score)

    return total_scores
    pass

def print_overall_eval(top, nested):
    header = ["TP", "TP+FP", "TP+FN", "P", "R", "F1"]

    print("\n-----------------------------")
    print("Total evaluation of all tests")
    print("-----------------------------")
    print("=====================Top-level evaluation=====================")
    print("%-10s%-10s%-10s%-10s%-10s%-10s" % (header[0], header[1], header[2], header[3], header[4], header[5]))
    P = top[0]/top[1]
    R = top[0]/top[2]
    if P != 0 and R != 0:
        F1 = (2*P*R)/(P+R)
        print("%-10d%-10d%-10d%-10.4f%-10.4f%-10.4f" % (top[0], top[1], top[2], P, R, F1))
    else:
        print("%-10d%-10d%-10d%-10.4f%-10.4f%-10.4f" % (top[0], top[1], top[2], P, R, 0))
    # print(top_level_score)
    print("\n=====================Nested evaluation=====================")
    print("%-10s%-10s%-10s%-10s%-10s%-10s" % (header[0], header[1], header[2], header[3], header[4], header[5]))
    P = nested[0] / nested[1]
    R = nested[0] / nested[2]
    if P != 0 and R != 0:
        F1 = (2 * P * R) / (P + R)
        print("%-10d%-10d%-10d%-10.4f%-10.4f%-10.4f" % (nested[0], nested[1], nested[2], P, R, F1))
    else:
        print("%-10d%-10d%-10d%-10.4f%-10.4f%-10.4f" % (nested[0], nested[1], nested[2], P, R, 0))
    # print(nested_score)
    return
if __name__ == '__main__':
    path_test = "E:\VLSP\CacDoiSubmit-20211112T002336Z-001\CacDoiSubmit\DoanXuanDung\VLSP_Bluesky_Team\Test-Data-Output1"
    path_anno = "E:\VLSP\CacDoiSubmit-20211112T002336Z-001\CacDoiSubmit\Annot"
    list_tests = os.listdir(path_test)
    list_annos = os.listdir(path_anno)
    top_level_score = [0, 0, 0]
    nested_score = [0, 0, 0]
    for i in range(len(list_tests)):
        print("==>>>Test:",list_tests[i])
        test_folder = path_test + "/" + list_tests[i]
        anno_folder = path_anno + "/" + list_annos[i]
        print("\n=====================Top-level evaluation=====================")
        total_scores = evaluate(test_folder, anno_folder, toplevel=True)

        scores = np.array(total_scores).sum(0)
        for j in range(len(scores)):
            top_level_score[j] += scores[j]

        print("\n=====================Nested evaluation=====================")
        total_scores = evaluate(test_folder, anno_folder, toplevel=False)
        scores = np.array(total_scores).sum(0)
        for j in range(len(scores)):
            nested_score[j] += scores[j]
        print()
    print_overall_eval(top_level_score, nested_score)

    print("Evaluate completed!")
