# Compute the statistics used in the paper
# Yang Xu
# 3/18/2016

library(data.table)
library(RMySQL)

# read data from db
# ssh yvx5085@brain.ist.psu.edu -i ~/.ssh/id_rsa -L 1234:localhost:3306

# Switchboard
conn = dbConnect(MySQL(), host = '127.0.0.1', user = 'yang', port = 1234, password = "05012014", dbname = 'swbd')
sql = 'SELECT convID, turnID, globalID, tileID, inTileID, globalID, ent, wordNum FROM entropy'
df.swbd = dbGetQuery(conn, sql)
dt.swbd = data.table(df.swbd)
setkey(dt.swbd, convID)

# BNC
conn = dbConnect(MySQL(), host = '127.0.0.1', user = 'yang', port = 1234, password = "05012014", dbname = 'bnc')
sql = 'SELECT xmlID, divIndex, turnID, globalID FROM DEM_2spkr'
df.bnc.full = dbGetQuery(conn, sql)
dt.bnc.full = data.table(df.bnc.full)
setkey(dt.bnc.full, xmlID, divIndex)

sql = 'SELECT xmlID, divIndex, convID, localID, turnID, topicID, inTopicID, ent, wordNum FROM entropy_DEM100'
df.bnc.short = dbGetQuery(conn, sql)
dt.bnc.short = data.table(df.bnc.short)
setkey(dt.bnc.short, xmlID, divIndex)

# join convID column from dt.bnc.short to dt.bnc.full
dt.bnc.full = dt.bnc.full[unique(dt.bnc.short[,.(xmlID, divIndex, convID)]),]
setkey(dt.bnc.full, convID)


## basic statistic of corpora
# Switchboard
stats.swbd = dt.swbd[, .(turnNum = max(turnID), sentNum = max(globalID)), by = convID]
mean(stats.swbd$turnNum) # 109.3
sd(stats.swbd$turnNum) # 50.7
mean(stats.swbd$sentNum) # 141.0
sd(stats.swbd$sentNum) # 61.4

# BNC
stats.bnc = dt.bnc.full[, .(turnNum = max(turnID), sentNum = max(globalID)), by = convID]
mean(stats.bnc$turnNum) # 51.7
sd(stats.bnc$turnNum) # 102.9
mean(stats.bnc$sentNum) # 70.3
sd(stats.bnc$sentNum) # 133.9


## correlation between sentence length and entropy
cor.test(dt.swbd$ent, dt.swbd$wordNum) # r = 0.258***
cor.test(dt.bnc.short$ent, dt.bnc.short$wordNum) # r = 0.088***


## proportion of within-turn and between-turn topic boundaries
# BNC
totalBoundaryNum = nrow(dt.bnc.short[inTopicID == 1 & topicID != 1,]) # 3722

boundaryIndex = dt.bnc.short[, .I[which(inTopicID == 1 & topicID != 1)], by = convID]
withinTurnNum = 0
betweenTurnNum = 0
for (i in 1:nrow(boundaryIndex)) {
    idx = boundaryIndex$V1[i]
    if (dt.bnc.short[idx, turnID] == dt.bnc.short[idx-1, turnID]) {
        withinTurnNum = withinTurnNum + 1
    } else {
        betweenTurnNum = betweenTurnNum + 1
    }
}
# withinTurnNum == 1534
# betweenTurnNum == 2188
1534/3722 # 41.2%
2188/3722 # 58.8%
