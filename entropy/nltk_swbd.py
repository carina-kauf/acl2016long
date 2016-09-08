#!/usr/local/bin/python
# Compute the entropy of the first 50 sentences of the randomly sampled 100 conversations from Switchboard
# Yang Xu
# 9/21/2015

import nltk
from nltk.model.ngram import NgramModel
from nltk.probability import LidstoneProbDist

import os, random, sys, pickle, re, glob
import MySQLdb


# the function that reads sentences from db to a dict object
def read_firstN_sents(cursor, conv_ids, first_n, include_loc = False):
    """
    param cursor: cursor of a db connection
    param conv_ids: conversation IDs to be read
    param first_n: the number of the first sentences to be read from each conversation
    return: 
        a dict object with int 1,2,...,first_n as keys, and sentences (list of words) as values
    """
    # make conv_ids a list
    if not isinstance(conv_ids, list):
        conv_ids = [conv_ids]

    res = {i: [] for i in xrange(1, first_n+1)}

    for cid in conv_ids:
        # fetch all sentences
        if include_loc:
            sql = 'SELECT localID, rawWord FROM entropy WHERE convID = %s AND globalID <= %s'
            cursor.execute(sql, (cid, first_n))
            sents = [tup[:2] for tup in cursor.fetchall()]
            # convert to lists of words, and append to res
            for i, s in enumerate(sents):
                if s[1] != '':
                    res[i+1].append((cid, s[0], s[1].split())) # s[0] is the localID
        else:
            sql = 'SELECT rawWord FROM entropy WHERE convID = %s AND globalID <= %s'
            cursor.execute(sql, (cid, first_n))
            sents = [tup[0] for tup in cursor.fetchall()]
            # convert to lists of words, and append to res
            for i, s in enumerate(sents):
                if s != '':
                    res[i+1].append(s.split())
    return res

# the function that reads all the sentences in a conversation/conversations
def read_all(cursor, conv_ids, include_loc = False):
    # make conv_ids a list
    if not isinstance(conv_ids, list):
        conv_ids = [conv_ids]

    # store sentences in a list
    res = []
    for cid in conv_ids:
        # fetch all sentences
        if include_loc:
            sql = 'SELECT localID, rawWord FROM entropy WHERE convID = %s'
            cursor.execute(sql, [cid])
            sents = [tup[:2] for tup in cursor.fetchall()]
            # convert to lists of words, and append to res
            for s in sents:
                res.append((s[0], s[1].split())) # s[0] is the localID
        else:
            sql = 'SELECT rawWord FROM entropy WHERE convID = %s'
            cursor.execute(sql, [cid])
            sents = [tup[0] for tup in cursor.fetchall()]
            # convert to lists of words, and append to res
            for s in sents:
                res.append(s.split())
    return res

# the function that reads sentences by bin
def read_sents_bin(cursor, conv_ids, bin_size = 10, bin_num = 10, include_loc = False):
    """
    bin_size: the number of sentences in each bin
    bin_num: the number of bins
    """
    if not isinstance(conv_ids, list):
        conv_ids = [conv_ids]

    res = {i: [] for i in xrange(1, bin_num+1)}

    for cid in conv_ids:
        if include_loc:
            sql = 'SELECT localID, rawWord FROM entropy WHERE convID = %s AND globalID <= %s'
            cursor.execute(sql, (cid, bin_size*bin_num))
            sents = [tup[:2] for tup in cursor.fetchall()]
            # append to res by bins
            for idx, s in enumerate(sents):
                bn = idx / bin_size + 1
                if s[1] != '': # remove empty str
                    res[bn].append((idx+1, s[0], s[1].split()))
        else:
            sql = 'SELECT rawWord FROM entropy WHERE convID = %s AND globalID <= %s'
            cursor.execute(sql, (cid, bin_size*bin_num))
            sents = [tup[0] for tup in cursor.fetchall()]
            # append
            for idx, s in enumerate(sents):
                bn = idx / bin_size + 1
                if s != '': # remove empty str
                    res[bn].append(s.split())
    return res



# main
if __name__ == '__main__':

    # db init: ssh yvx5085@brain.ist.psu.edu -i ~/.ssh/id_rsa -L 1234:localhost:3306
    conn = MySQLdb.connect(host = "127.0.0.1", 
                    user = "yang", 
                    port = 3306,
                    passwd = "05012014",
                    db = "swbd")
    cur = conn.cursor()

    # get all convIDs
    convIDs = range(1, 1127)

    # get train and test sentences
    # SENTS_NUM = 100
    # test_convIDs = random.sample(convIDs, 100)
    # train_convIDs = [cid for cid in convIDs if cid not in test_convIDs]
    # train_sents = read_firstN_sents(cur, train_convIDs, SENTS_NUM)
    # test_sents = read_firstN_sents(cur, test_convIDs, SENTS_NUM, include_loc = True)

    # train and compute
    # with open('results_swbd_nltk_100.txt', 'wb') as fw:
    #     for key in train_sents.iterkeys():
    #         # train the ngrams model
    #         lm = NgramModel(3, train_sents[key])
    #         # compute and write
    #         for s in test_sents[key]:
    #             if len(s[1]) > 0: # make sure it's not an empty list
    #                 e = lm.entropy(s[1])
    #                 fw.write(','.join((str(key), str(s[0]), str(e))) + '\n')
    #         # print progress
    #         print 'key = %d done' % key


    ###############################
    # experiment 1: train by all
    ###############################

    # randomly sample a test set, and use the rest as train set
    # train the model on the whole set - do not differentiate sentence numbers (global IDs)
    # test_convIDs = random.sample(convIDs, 100)
    # train_convIDs = [cid for cid in convIDs if cid not in test_convIDs]
    # train_sents = read_all(cur, train_convIDs)

    # # train the model
    # lm = NgramModel(3, train_sents) # wow, it takes 3 hrs to train the model!

    # # compute 
    # with open('results_swbd_nltk_trainWithAll.txt', 'wb') as fw:
    #     for i, cid in enumerate(test_convIDs):
    #         test_sents = read_all(cur, cid, include_loc = True)
    #         # compute and write
    #         for j, s in enumerate(test_sents):
    #             if len(s[1]) > 0:
    #                 e = lm.entropy(s[1])
    #                 fw.write(','.join((str(cid), str(j), str(s[0]), str(e))) + '\n')
    #         # print progress
    #         print 'conversation %d/%d is done' % (i+1, len(test_convIDs))


    #############################
    # experiment 2: train by bin
    #############################

    # # constants
    # TEST_CONV_NUM = 100 # number of conversations that are sampled as test set
    # BIN_SIZE = 10 # each conversation is segmented into bins (# of sentences)
    # BIN_NUM = 10 # number of bins to be extracted from each conversation
    
    # # get the convIDs for train and test
    # test_convIDs = random.sample(convIDs, TEST_CONV_NUM)
    # train_convIDs = [cid for cid in convIDs if cid not in test_convIDs]

    # # read the sentences for train and test, stored by bin
    # train_sents = read_sents_bin(cur, train_convIDs, BIN_SIZE, BIN_NUM)
    # test_sents = read_sents_bin(cur, test_convIDs, BIN_SIZE, BIN_NUM, include_loc = True)

    # # train, compute, and write
    # with open('results_swbd_nltk_trainByBin.txt', 'wb') as fw:
    #     count = 1
    #     for b in train_sents.iterkeys():
    #         # train
    #         lm = NgramModel(3, train_sents[b])
    #         # compute and write
    #         for s in test_sents[b]:
    #             e = lm.entropy(s[2])
    #             fw.write(','.join((str(s[0]), str(s[1]), str(e))) + '\n')
    #         # print progress
    #         print '%d/%d bin is done' % (count, len(train_sents))
    #         count += 1


    ################################
    # experiment 3: 10-fold cross-validation to
    # compute the entropy for each conversation
    # and for the first 100 sentences only
    # note: the training set for the n_th sentences are also from the n_th sentences
    ################################

    # put convIDs into folds
    FOLD_NUM = 10
    FOLD_LEN = len(convIDs) / FOLD_NUM
    random.shuffle(convIDs)
    folds = [convIDs[i:i+FOLD_LEN] for i in xrange(0, len(convIDs), FOLD_LEN)]

    tmp = folds[:9]
    tmp.append(folds[9] + folds[10])
    folds = tmp

    # remove the existing result file
    res_file_name = 'results_swbd_nltk_CV.txt'
    if os.path.isfile(res_file_name):
        os.system('rm ' + res_file_name)

    SAMPLE_SENTS_NUM = 100
    for fold_idx, fold in enumerate(folds): # takes 37 min
        # print progress
        print 'fold %d/%d started' % (fold_idx+1, len(folds))
        # read test sents
        test_sents = read_firstN_sents(cur, fold, SAMPLE_SENTS_NUM, include_loc = True)
        # read the train sents
        train_convIDs = reduce(lambda a,b: a+b, folds[:fold_idx] + folds[fold_idx+1:])
        train_sents = read_firstN_sents(cur, train_convIDs, SAMPLE_SENTS_NUM)
        # open the file to write the results
        fw = open(res_file_name, 'ab')
        # train and compute
        key_count = 1
        for key in test_sents.iterkeys():
            lm = NgramModel(3, train_sents[key])
            for s in test_sents[key]:
                e = lm.entropy(s[2])
                fw.write(','.join((str(s[0]), str(key), str(s[1]), str(e))) + '\n')
            # print progress
            sys.stdout.write('\rkey = %d/%d done' % (key_count, len(test_sents)))
            sys.stdout.flush()
            key_count += 1
        # print progress
        print '\nfold %d/%d done\n' % (fold_idx+1, len(folds))