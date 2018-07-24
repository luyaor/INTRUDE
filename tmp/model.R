library(xtable)
library(interplot)
library(caret)
library(car)
library(pscl)
library(pROC)
library(dplyr)
library(stargazer)

# Read in merged csv file
df.match <- read.csv2(file="matched_data.csv", quote="\"", sep=";")

# vs Mean Contrasts
cs = contr.sum(14)
cs
colnames(cs) = sort(unique(df.match$lang))[1:length(unique(df.match$lang))-1]
colnames(cs) = paste(colnames(cs), "vs Mean")
cs
contrasts(df.match$lang) = cs

combined_logit <- glm(abandoned_and_alive  ~
                        log(project_age) +
                        log(last_build_duration) +
                        log(commits) +
                        log(contribs) +
                        log(job_count) +
                        log(PRs+0.5) +
                        log(yml_commits) +
                        log(yml_contribs) + 
                        lang,
                      data = df.match, 
                      family = "binomial"
                      )
summary(combined_logit)
Anova(combined_logit, type=2)


library("car")
vif(combined_logit)

plot(combined_logit)

summary(combined_logit)
Anova(combined_logit, type=2)
library(pscl)
pR2(combined_logit)

library(pROC)
auc(roc(df.match$abandoned_and_alive ~ predict(combined_logit, type=c("response"))))
plot(roc(df.match$abandoned_and_alive ~ predict(combined_logit, type=c("response"))))
