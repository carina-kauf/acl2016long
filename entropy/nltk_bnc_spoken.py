# Use the probability and model modules to re-calculate the entropy of BNC spoken part
# Also, do some basic statistics about BNC-DEM and BNC-CG
# Yang Xu
# 9/24/2015

import nltk
from nltk.model.ngram import NgramModel
from nltk.probability import LidstoneProbDist

from rep_genzel_bnc_nonspoken import raw_words

import os, random, sys
from lxml import etree



# the function that reads sentences from BNC-DEM to a dict object
def read_sents_DEM(root_dir, file_div_tuples, sent_num, local_idx = False, full_info = False):
    """
    root_dir: root path to BNC
    file_div_tuples: a list of tuples, e.g., [(file_id, div_idx),...].
        file_id is the name of the xml file, and div_idx is the index of the <div> elements, that contains only 2 speakers
    sent_num: the number of sentences to be extracted from the beginning of each conversation
    local_idx: determins the content of the returned dict, see below
    return: a dict object, with 1, 2, ..., sent_num as keys, and a list of sentences as values.
        When local_idx is True, a sentence is a list of words.
        When local_idx is False, a sentence is wrapped as a tuple, whose first element is the local index of the sentence, 
        and the second element is a list of words
    """
    if isinstance(file_div_tuples, tuple):
        file_div_tuples = [file_div_tuples]
    res = {i: [] for i in xrange(1, sent_num+1)}

    for (file_id, div_idx) in file_div_tuples:
        # read the xml tree
        tree = etree.parse(root_dir + file_id)

        # find the <div> indicated by div_idx
        div_path = 'stext/div[' + str(div_idx) + ']'
        try:
            div = tree.find(div_path)
        except Exception, e:
            raise e
        
        # extract sentences
        sid = 1
        utters = div.findall('u')
        for u_id, u in enumerate(utters):
            sents = u.findall('s')
            for i, s in enumerate(sents):
                # append to res
                if local_idx:
                    if full_info:
                        # full info includes: xml_id, div_index, turn_index, local
                        res[sid].append((file_id, div_idx, u_id+1, i+1, raw_words(s)))
                    else:
                        res[sid].append((i+1, raw_words(s)))
                else:
                    res[sid].append(raw_words(s))
                # increase sid
                sid += 1
                # check if sent_num is reached
                if sid > sent_num:
                    break
            # check if sent_num is reached
            if sid > sent_num:
                break
    # return 
    return res

# the function that reads sentences from BNC-CG to a dict object
def read_sents_CG(root_dir, files, sent_num, local_idx = False, full_info = False):
    """
    root_dir: root path to BNC corpus
    files: names of xml files
    sent_num: number of sentences to be extracted
    local_idx: see read_sents_DEM
    """
    if isinstance(files, str):
        files = [files]
    res = {i: [] for i in xrange(1, sent_num+1)}

    for f in files:
        # read the xml tree
        tree = etree.parse(root_dir + f)

        # extract sentences
        sid = 1
        utters = tree.findall('.//u')
        for u in utters:
            sents = u.findall('s')
            for i, s in enumerate(sents):
                # append to res
                if local_idx:
                    res[sid].append((i+1, raw_words(s)))
                else:
                    res[sid].append(raw_words(s))
                sid += 1
                # check if sent_num is reached
                if sid > sent_num:
                    break
            # check if sent_num is reached
            if sid > sent_num:
                break
    # return
    return res

# the function that makes folds for cross-validation
def make_folds(source, fold_num):
    fold_len = len(source) / fold_num
    src_cpy = source[:]
    random.shuffle(src_cpy)
    folds = [src_cpy[i:i+fold_len] for i in xrange(0, len(src_cpy), fold_len)]

    # if the resulting folds have fold_num + 1 elements
    # merge the last two folds
    if len(folds) == fold_num + 1:
        tmp = folds[:fold_num-1]
        tmp.append(folds[-2] + folds[-1])
        folds = tmp

    return folds


# the function that does the cross validation
def cross_validate(result_file, root_dir, folds, read_func, sent_num):
    if os.path.isfile(result_file):
        os.system('rm ' + result_file)
    print 'cross-validation started'

    for i, fold in enumerate(folds):
        print 'fold %d/%d started' % (i+1, len(folds))
        # read test
        test = read_func(root_dir, fold, sent_num, local_idx = True, full_info = True)
        # read train
        train_files = reduce(lambda a,b: a+b, folds[:i] + folds[i+1:])
        train = read_func(root_dir, train_files, sent_num)
        # open result file
        fw = open(result_file, 'ab')
        # train and compute
        count = 1
        for key in test.iterkeys():
            lm = NgramModel(3, train[key])
            for s in test[key]:
                if len(s[-1]) > 0:
                    e = lm.entropy(s[-1])
                    # s[0] is xml id
                    # s[1] is div index
                    # key is global index
                    # s[2] is turn index
                    # s[3] is local index
                    fw.write(','.join(map(str, (s[0], s[1], key, s[2], s[3], e))) + '\n')
            # print progress
            sys.stdout.write('\rkey = %d/%d done' % (count, len(test)))
            sys.stdout.flush()
            count += 1
        print 'fold %d/%d done' % (i+1, len(folds))



# main
if __name__ == '__main__':
    
    # corpus dir
    # bnc_dir = '/Users/yangxu/Documents/BNC corpus/2554/Texts/'
    bnc_dir = '/Users/yvx5085/Desktop/bnc/corpus/Texts/'


    ################# 
    # BNC-DEM
    #################
    
    # read (file_id, div_idx) tuples
    file_div_all = []
    with open('BNC-DEM_2sp_plain.txt', 'rb') as fr:
        for line in fr:
            line = line.strip()
            file_div_all.append(tuple(line.split(',')))

    # # sample the train and test set
    # TRAIN_RATE = 0.9
    # file_div_train = random.sample(file_div_all, int(TRAIN_RATE * len(file_div_all)))
    # file_div_test = [tup for tup in file_div_all if tup not in file_div_train]

    # # read the sentences
    # SENT_NUM = 100
    # DEM_train = read_sents_DEM(bnc_dir, file_div_train, SENT_NUM)
    # DEM_test = read_sents_DEM(bnc_dir, file_div_test, SENT_NUM, local_idx = True)

    # # train and compute
    # with open('results_bnc_nltk_sample100.txt', 'wb') as fw:
    #     for key in DEM_train.iterkeys():
    #         lm = NgramModel(3, DEM_train[key])
    #         for s in DEM_test[key]:
    #             if len(s[1]) > 0: # avoid empty sentence
    #                 e = lm.entropy(s[1])
    #                 fw.write(','.join((str(key), str(s[0]), str(e))) + '\n')


    ##################
    # BNC-CG
    ##################

    file_all = []
    with open('BNC-CG_2sp_plain.txt', 'rb') as fr:
        for line in fr:
            line = line.strip()
            file_all.append(line)

    # # sample the train and test set
    # TRAIN_RATE = 0.9
    # file_train = random.sample(file_all, int(TRAIN_RATE * len(file_all)))
    # file_test = [f for f in file_all if f not in file_train]

    # # read the sentences
    # SENT_NUM = 100
    # CG_train = read_sents_CG(bnc_dir, file_train, SENT_NUM)
    # CG_test = read_sents_CG(bnc_dir, file_test, SENT_NUM, local_idx = True)

    # # train and compute
    # with open('results_bnc_CG_nltk_sample.txt', 'wb') as fw:
    #     for key in CG_train.iterkeys():
    #         lm = NgramModel(3, CG_train[key])
    #         for s in CG_test[key]:
    #             if len(s[1]) > 0: # avoid empty sentence
    #                 e = lm.entropy(s[1])
    #                 fw.write(','.join((str(key), str(s[0]), str(e))) + '\n')


    ###################
    # cross-validation for DEM and CG, respectively
    ###################
    
    TRAIN_RATE = 0.9
    SENT_NUM = 100
    FOLD_NUM = 10
    
    # DEM 
    res_file_DEM = 'results_BNC-DEM_CV_fullInfo.txt'
    folds_DEM = make_folds(file_div_all, FOLD_NUM)
    cross_validate(res_file_DEM, bnc_dir, folds_DEM, read_sents_DEM, SENT_NUM)

    # CG
    # res_file_CG = 'result_BNC-CG_CV.txt'
    # folds_CG = make_folds(file_all, FOLD_NUM)
    # cross_validate(res_file_CG, bnc_dir, folds_CG, read_sents_CG, SENT_NUM)
