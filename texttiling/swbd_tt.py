## Texttiling for swbd
## Yang Xu
## 8/17/2015

from nltk.tokenize.texttiling import TextTilingTokenizer
from nltk.corpus import brown
import MySQLdb
import re


# main
if __name__ == '__main__':

    # db connect: ssh yvx5085@brain.ist.psu.edu -i ~/.ssh/id_rsa -L 1234:localhost:3306
    conn = MySQLdb.connect(host = "127.0.0.1", 
                    user = "yang", 
                    port = 1234,
                    passwd = "05012014",
                    db = "swbd")
    cur = conn.cursor()

    # create the table
    sql = 'DROP TABLE IF EXISTS textTiling'
    cur.execute(sql)
    sql = 'CREATE TABLE textTiling (convID INT, globalID INT, tileID INT, inTileID INT, entropy FLOAT, \
        PRIMARY KEY (convID, globalID));'
    cur.execute(sql)


    # initialize
    tt = TextTilingTokenizer()
    # tt_demo = TextTilingTokenizer(demo_mode = True)

    # get all conversation IDs
    sql = 'SELECT DISTINCT(convID) FROM entropy'
    cur.execute(sql)
    convIDs = [tup[0] for tup in cur.fetchall()]

    # get text for each cid and do text tiling
    for cid in convIDs:
        sql = 'SELECT tagged FROM entropy WHERE convID = %d' % cid
        cur.execute(sql)
        text = '\n\n\n\t'.join([tup[0] for tup in cur.fetchall()])
        # tiling
        try:
            segmented_text = tt.tokenize(text)
        except Exception, e:
            pass
        else:
            global_id = 0
            for i, seg in enumerate(segmented_text):
                tile_id = i + 1
                sents = [s for s in seg.split('\n\n\n\t') if s != '']
                for j, s in enumerate(sents):
                    in_tile_id = j + 1
                    global_id += 1
                    # obtain the entropy
                    sql = 'SELECT ent FROM entropy WHERE convID = %d AND globalID = %d' % (cid, global_id)
                    cur.execute(sql)
                    ent = cur.fetchone()[0]
                    # insert to textTiling table
                    ent = 'NULL' if ent is None else ent
                    sql = 'INSERT INTO textTiling VALUES(%d, %d, %d, %d, %s)' % \
                        (cid, global_id, tile_id, in_tile_id, ent)
                    cur.execute(sql)
            print 'convID %d/%d done.' % (cid, len(convIDs))
    conn.commit()