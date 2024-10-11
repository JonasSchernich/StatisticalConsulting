#if (!require("BiocManager", quietly = TRUE))
#    install.packages("BiocManager")#

#BiocManager::install("Biobase")

library(Biobase)

#Load data
cohorts = readRDS("./Data/PCa_cohorts.Rds")

#Cohorts
names(cohorts)

#Select individual cohorts
cohorts[[1]]
cohorts[["Atlanta_2014_Long"]]

# Get patient data of a cohort
pData(cohorts[[1]])

# Get expression data of a cohort
exprs(cohorts[[1]])


# Standardize expression data for all cohorts
standardize = function(z) {
  rowmean = apply(z, 1, mean, na.rm=TRUE)
  rowsd = apply(z, 1, sd, na.rm=TRUE)
  rv = sweep(z, 1, rowmean,"-")
  rv = sweep(rv, 1, rowsd, "/")
  return(rv)
}
old_expr <- head(exprs(cohorts$Atlanta_2014_Long))
for (i in 1:length(cohorts)){
  exprs(cohorts[[i]]) = standardize(exprs(cohorts[[i]]))
}
expr <- head(exprs(cohorts$Atlanta_2014_Long))
for (i in 1:length(cohorts)){
  print(experimentData((cohorts[[i]])))
}




# Zweites dummy objekt erstellen
cohorts <- readRDS("./Data/PCa_cohorts.Rds")
cohorts_2 <- cohorts
names(cohorts_2) <- paste0(names(cohorts), "2")
saveRDS(cohorts_2, "PCa_cohorts_2.Rds")
names(cohorts_2)












