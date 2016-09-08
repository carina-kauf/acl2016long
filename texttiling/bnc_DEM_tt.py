#!/usr/local/bin/python
# Accomplish the TextTiling task on the entropy_DEM100 table (for BNC-DEM)
# Yang Xu
# 10/1/2015

from nltk.tokenize.texttiling import TextTilingTokenizer
import MySQLdb


# main
if __name__ == '__main__':
    # db init: ssh yvx5085@brain.ist.psu.edu -i ~/.ssh/id_rsa -L 1234:localhost:3306
    conn = MySQLdb.connect(host = "127.0.0.1", 
                    user = "yang", 
                    port = 3306,
                    passwd = "05012014",
                    db = "bnc")
    cur = conn.cursor()

    # all convIDs
    sql = 'SELECT DISTINCT(convID) FROM entropy_DEM100'
    cur.execute(sql)
    convIDs = [tup[0] for tup in cur.fetchall()]
    convIDs.sort()

    # tokenizer
    tt = TextTilingTokenizer()

    # get the text of each convID, and do the TextTiling
    failed_convIDs = []
    for cid in convIDs:
        sql = 'SELECT rawWord FROM entropy_DEM100 WHERE convID = %s'
        cur.execute(sql, [cid])
        text = '\n\n\n\t'.join([tup[0] for tup in cur.fetchall()])

        try:
            segmented_text = tt.tokenize(text)
        except Exception, e:
            print 'convID %d failed' % cid
            failed_convIDs.append(cid)
        else:
            global_idx = 1
            for i, seg in enumerate(segmented_text):
                topic_idx = i + 1
                sents = [s for s in seg.split('\n\n\n\t') if s != '']
                for j, s in enumerate(sents):
                    in_topic_idx = j + 1
                    # update columns in table
                    sql = 'UPDATE entropy_DEM100 SET topicID = %s, inTopicID = %s WHERE convID = %s AND globalID = %s'
                    cur.execute(sql, (topic_idx, in_topic_idx, cid, global_idx))
                    # increase global index
                    global_idx += 1
            # print progress
            print 'convID %d/%d done.' % (cid, len(convIDs))

    # commit update
    conn.commit()

    # log failed convIDs
    with open('failed_convIDs.txt', 'wb') as fw:
        for item in failed_convIDs:
            fw.write(str(item) + '\n')