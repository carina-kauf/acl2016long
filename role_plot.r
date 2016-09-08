# plot ent vs inTopicID grouped by roles
# Yang Xu
# 3/17/2016

library(data.table)
library(lme4)
library(lmerTest)
library(ggplot2)

# read
df.swbd = readRDS('swbd.leader.new.rds')
df.bnc = readRDS('bnc.leader.tdbf.rds')

# change byLeader column to character
df.swbd$byLeader = as.character(df.swbd$byLeader)
df.swbd[df.swbd$byLeader == 'TRUE',]$byLeader = 'initiator'
df.swbd[df.swbd$byLeader == 'FALSE',]$byLeader = 'responder'
setnames(df.swbd, 'byLeader', 'role')

df.bnc$byLeader = as.character(df.bnc$byLeader)
df.bnc[df.bnc$byLeader == 'TRUE',]$byLeader = 'initiator'
df.bnc[df.bnc$byLeader == 'FALSE',]$byLeader = 'responder'
setnames(df.bnc, 'byLeader', 'role')


## plot
df.swbd.tmp = df.swbd[, .(ent, entc, inTopicID, role)][, corpus := 'Switchboard'][, group := '']
df.bnc.tmp = df.bnc[, .(ent, entc, inTopicID, role)][, corpus := 'BNC'][, group := '']
df.all = rbindlist(list(df.swbd.tmp, df.bnc.tmp))

df.all[corpus == 'Switchboard' & role == 'initiator', group := 'Switchboard: initiator']
df.all[corpus == 'Switchboard' & role == 'responder', group := 'Switchboard: responder']
df.all[corpus == 'BNC' & role == 'initiator', group := 'BNC: initiator']
df.all[corpus == 'BNC' & role == 'responder', group := 'BNC: responder']

# get ggplot default colors
gg_color_hue <- function(n) {
  hues = seq(15, 375, length=n+1)
  hcl(h=hues, l=65, c=100)[1:n]
}
my_colors = gg_color_hue(2)


p1 = ggplot(df.all[inTopicID <= 10,], aes(x = inTopicID, y = ent)) +
    stat_summary(fun.data = mean_cl_boot, geom = 'ribbon', alpha = .5, aes(fill = group)) +
    stat_summary(fun.y = mean, geom = 'line', aes(lty = group)) +
    stat_summary(fun.y = mean, geom = 'point', aes(shape = group)) +
    scale_x_continuous(breaks = 1:10) +
    theme(legend.position = c(.75, .2)) +
    xlab('within-episode position') + ylab('entropy') +
    scale_fill_manual(values = c('BNC: initiator' = my_colors[1], 'BNC: responder' = my_colors[1],
        'Switchboard: initiator' = my_colors[2], 'Switchboard: responder' = my_colors[2])) +
    scale_linetype_manual(values = c('BNC: initiator' = 1, 'BNC: responder' = 3, 'Switchboard: initiator' = 1, 'Switchboard: responder' = 3)) +
    scale_shape_manual(values = c('BNC: initiator' = 1, 'BNC: responder' = 1, 'Switchboard: initiator' = 4, 'Switchboard: responder' = 4))
pdf('e_vs_inPos_role_new.pdf', 4, 4)
plot(p1)
dev.off()

p2 = ggplot(df.all[inTopicID <= 10,], aes(x = inTopicID, y = entc)) +
    stat_summary(fun.data = mean_cl_boot, geom = 'ribbon', alpha = .5, aes(fill = group)) +
    stat_summary(fun.y = mean, geom = 'line', aes(lty = group)) +
    stat_summary(fun.y = mean, geom = 'point', aes(shape = group)) +
    scale_x_continuous(breaks = 1:10) +
    theme(legend.position = c(.75, .2)) +
    xlab('within-episode position') + ylab('normalized entropy') +
    scale_fill_manual(values = c('BNC: initiator' = my_colors[1], 'BNC: responder' = my_colors[1],
        'Switchboard: initiator' = my_colors[2], 'Switchboard: responder' = my_colors[2])) +
    scale_linetype_manual(values = c('BNC: initiator' = 1, 'BNC: responder' = 3, 'Switchboard: initiator' = 1, 'Switchboard: responder' = 3)) +
    scale_shape_manual(values = c('BNC: initiator' = 1, 'BNC: responder' = 1, 'Switchboard: initiator' = 4, 'Switchboard: responder' = 4))
pdf('ne_vs_inPos_role_new.pdf', 4, 4)
plot(p2)
dev.off()


## models
# Switchboard initiator
m1 = lmer(ent ~ inTopicID + (1|topicID) + (1|convID), df.swbd[role == 'initiator' & inTopicID <= 10,])
summary(m1) # beta = -3.642e-02, t = -10.74***

m2 = lmer(entc ~ inTopicID + (1|topicID) + (1|convID), df.swbd[role == 'initiator' & inTopicID <= 10,])
summary(m2) # beta = -2.452e-04, t = -0.252 ins

# BNC initiator
m3 = lmer(ent ~ inTopicID + (1|topicID) + (1|convID), df.bnc[role == 'initiator' & inTopicID <= 10,])
summary(m3) # beta = -2.901e-02, t = -2.293*

m4 = lmer(entc ~ inTopicID + (1|topicID) + (1|convID), df.bnc[role == 'initiator' & inTopicID <= 10,])
summary(m4) # beta = -4.307e-04, t = -0.345 ins


# Switchboard responder
m5 = lmer(ent ~ inTopicID + (1|topicID) + (1|convID), df.swbd[role == 'responder' & inTopicID <= 10,])
summary(m5) # beta = 3.286e-01, t = 36.77***

m6 = lmer(entc ~ inTopicID + (1|topicID) + (1|convID), df.swbd[role == 'responder' & inTopicID <= 10,])
summary(m6) # beta = 1.353e-02, t = 11.23***

# BNC responder
m7 = lmer(ent ~ inTopicID + (1|topicID) + (1|convID), df.bnc[role == 'responder' & inTopicID <= 10,])
summary(m7) # beta = 1.410e-01, t = 7.768***

m8 = lmer(entc ~ inTopicID + (1|topicID) + (1|convID), df.bnc[role == 'responder' & inTopicID <= 10,])
summary(m8) # beta = 1.171e-02, t = 6.478***
