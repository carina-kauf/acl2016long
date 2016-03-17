# plot entropy and normalized entropy against sentence global position
# Yang Xu
# 3/14/2016

library(ggplot2)
library(gridExtra)

library(data.table)
library(lme4)
library(lmerTest)

# the function that gets the legend of a plot (for multiple plotting that shares one legend)
g_legend = function(p) {
    tmp = ggplotGrob(p)
    leg = which(sapply(tmp$grobs, function(x) x$name) == "guide-box")
    legend = tmp$grobs[[leg]]
    legend
}

# read data
df.swbd = readRDS('swbd_df_c.rds')
df.bnc = readRDS('bnc_df_c.rds')

# make dt
dt.s = data.table(df.swbd)
setkey(dt.s, globalID)
dt.b = data.table(df.bnc)
setkey(dt.b, globalID)

# combine the two datasets
dt.s.tmp = dt.s[, .(globalID, ent, entc)]
dt.s.tmp[, corpus := 'Switchboard']
dt.b.tmp = dt.b[, .(globalID, ent, entc)]
dt.b.tmp[, corpus := 'BNC']
dt.all = rbindlist(list(dt.s.tmp, dt.b.tmp))


# The palette with grey:
cbPalette <- c("#999999", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7")

# plot ent vs globalID
p1 = ggplot(dt.all, aes(x = globalID, y = ent)) +
    stat_summary(fun.data = mean_cl_boot, geom = 'ribbon', alpha = .5, aes(fill = corpus)) +
    stat_summary(fun.y = mean, geom = 'line', aes(lty = corpus)) +
    xlab('global position') + ylab('entropy') + ggtitle('(a)') +
    scale_x_continuous(breaks = 1:100) +
    theme(legend.position = 'bottom', plot.title = element_text(size = 12))

p2 = ggplot(dt.all, aes(x = globalID, y = entc)) +
    stat_summary(fun.data = mean_cl_boot, geom = 'ribbon', alpha = .5, aes(fill = corpus)) +
    stat_summary(fun.y = mean, geom = 'line', aes(lty = corpus)) +
    xlab('global position') + ylab('normalized entropy') + ggtitle('(b)')

lgd = g_legend(p1)
pdf('ent_vs_global.pdf', 10, 5)
grid.arrange(arrangeGrob(p1 + theme(legend.position = "none"),
                        p2 + theme(legend.position = "none"), ncol = 2),
            lgd, nrow = 2, heights = c(9, 1))
dev.off()




## linear mixed models

# Switchboard
m1 = lmer(ent ~ globalID + (1|convID), dt.s)
summary(m1) # beta = 4.225e-03, t = 8.643***

m1_1 = lmer(ent ~ globalID + (1|convID), dt.s[globalID > 10,])
summary(m1_1) # beta = 3.431e-03, t = 5.974***

m2 = lmer(entc ~ globalID + (1|convID), dt.s)
summary(m2) # beta = 5.897e-04, t = 9.17***

m2_1 = lmer(entc ~ globalID + (1|convID), dt.s[globalID > 10,])
summary(m2_1) # beta = 5.093e-04, t = 6.799***

# BNC
m3 = lmer(ent ~ globalID + (1|convID), dt.b)
summary(m3) # beta = 1.537e-02, t = 17.15***

m4 = lmer(entc ~ globalID + (1|convID), dt.b)
summary(m4) # beta = 1.416e-03, t = 15.92***
