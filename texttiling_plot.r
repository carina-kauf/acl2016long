# plot the texttiling results
# Yang Xu
# 3/17/2016

library(ggplot2)
library(gridExtra)

library(data.table)
library(lme4)
library(lmerTest)

# read data
df.swbd = readRDS('swbd_df_c.rds')
df.bnc = readRDS('bnc_df_c.rds')

# make dt
dt.s = data.table(df.swbd)
setkey(dt.s, topicID, inTopicID)
dt.b = data.table(df.bnc)
setkey(dt.b, topicID, inTopicID)

# combine dt.s and dt.b
dt.s.tmp = dt.s[, .(ent, entc, topicID, inTopicID)]
# add label column, which is the label text of facet_wrap
dt.s.tmp[, label := '']
for (i in 1:max(dt.s.tmp$topicID)) {
    dt.s.tmp[topicID == i, label := paste('episode', i)]
}
dt.s.tmp$label = as.factor(dt.s.tmp$label)

dt.b.tmp = dt.b[, .(ent, entc, topicID, inTopicID)]
dt.b.tmp[, label := '']
for (i in 1:max(dt.b.tmp$topicID)) {
    dt.b.tmp[topicID == i, label := paste('episode', i)]
}
dt.b.tmp$label = as.factor(dt.b.tmp$label)

dt.s.tmp[, corpus := 'Switchboard']
dt.b.tmp[, corpus := 'BNC']
dt.all = rbindlist(list(dt.s.tmp, dt.b.tmp))


# ent vs within-episode position, grouped by episode index
ps1 = ggplot(dt.all[topicID <= 6 & inTopicID <= 10,], aes(x = inTopicID, y = ent)) +
    stat_summary(fun.data = mean_cl_boot, geom = 'ribbon', alpha = .5, aes(fill = corpus)) +
    stat_summary(fun.y = mean, geom = 'line', aes(lty = corpus)) +
    facet_wrap(~label, nrow = 1) +
    scale_x_continuous(breaks = 1:10) +
    xlab('within-episode position') + ylab('entropy') +
    theme(legend.position = c(.85, .1), legend.direction = 'horizontal')
pdf('e_vs_inPos_g.pdf', 9, 2.5)
plot(ps1)
dev.off()

ps2 = ggplot(dt.all[topicID <= 6 & inTopicID <= 10,], aes(x = inTopicID, y = entc)) +
    stat_summary(fun.data = mean_cl_boot, geom = 'ribbon', alpha = .5, aes(fill = corpus)) +
    stat_summary(fun.y = mean, geom = 'line', aes(lty = corpus)) +
    facet_wrap(~label, nrow = 1) +
    scale_x_continuous(breaks = 1:10) +
    xlab('within-episode position') + ylab('normalized entropy') +
    theme(legend.position = c(.85, .1), legend.direction = 'horizontal')
pdf('ne_vs_inPos_g.pdf', 9, 2.5)
plot(ps2)
dev.off()


## linear mixed effect models
# Switchboard
m1 = lmer(ent ~ inTopicID + (1|topicID) + (1|convID), dt.s)
summary(m1) # beta = 3.801e-02，t = 15.06***

m1_1 = lmer(entc ~ inTopicID + (1|topicID) + (1|convID), dt.s)
summary(m1_1) # beta = 4.526e-03, t = 13.65***

m2 = lmer(ent ~ inTopicID + (1|topicID) + (1|convID), dt.b)
summary(m2) # beta = 2.533e-02，t = 6.973***

m2_1 = lmer(entc ~ inTopicID + (1|topicID) + (1|convID), dt.b)
summary(m2_1) # beta = 2.991e-03, t = 8.257***
