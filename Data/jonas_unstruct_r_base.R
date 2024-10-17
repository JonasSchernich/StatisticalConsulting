# load_and_preprocess.R

library(Biobase)

# Function to load and convert ExpressionSet objects
load_cohorts <- function(rds_file_path) {
  # Load the RDS file
  cohorts <- readRDS(rds_file_path)
  
  # Function to convert ExpressionSet to list of data frames
  convertExpressionSet <- function(eset) {
    list(
      pData = as.data.frame(pData(eset)),
      fData = as.data.frame(fData(eset)),
      exprs = as.data.frame(exprs(eset))
    )
  }
  
  # Convert all cohorts to list of data frames
  cohorts_list <- lapply(cohorts, convertExpressionSet)
  
  return(cohorts_list)
}

# Function to standardize expression data
standardize <- function(z) {
  rowmean <- apply(z, 1, mean, na.rm = TRUE)
  rowsd <- apply(z, 1, sd, na.rm = TRUE)
  rv <- sweep(z, 1, rowmean, "-")
  rv <- sweep(rv, 1, rowsd, "/")
  return(rv)
}

# Main process
main <- function() {
  # Load the data
  rds_file_path <- file.path("Data", "PCa_cohorts.Rds")
  cohorts <- load_cohorts(rds_file_path)
  
  # Standardize expression data for all cohorts
  for (i in seq_along(cohorts)) {
    cohorts[[i]]$exprs <- standardize(as.matrix(cohorts[[i]]$exprs))
  }
  
  # Return the processed cohorts
  return(cohorts)
}

# Run the main process
processed_cohorts <- main()



## Na Imputation for single columns
na_list <- data.frame()
na_list[1, 2] = 1
for (i in 1:9) {
  for (j in 1:ncol(processed_cohorts[[i]]$pData)) {
    if (any(is.na(processed_cohorts[[i]]$pData[, j])) && !all(is.na(processed_cohorts[[i]]$pData[, j]))) {
      na_list[nrow(na_list) + 1, 1] <- names(processed_cohorts)[i]
      na_list[nrow(na_list) + 1, 2] <-colnames(processed_cohorts[[i]]$pData)[j]
    }
  }
}


################## mice für einzlene Kohorten
library(mice)
# Generelle zu klären: Was machen wir mit NA Spalten in einigen Kohorten?
# Aktuell: Ich imputiere innerhalb einzelner kohorten und entferne dafür NA columns, füge sie aber zum schluss wieder hinzu. Im nächsten schritt könnten dann ganze NA columns imputed werden
# Problem damit: Wir nutzen relativ wenig Beobachtungen für die imputation + die imputation basiert nicht in allen DFs auf den gleichen Daten (weil bei manchen eben NA spalten entfernt werden)
# Alternative: Spalten die in einigen DFs NA sind in allen entfernen, dann die DFs mergen und über alle imputieren. So würden für alle die gleichen Spalten + deutlich mehr Patienten genutzt
# Nachteil: Bei steigender Kohortenzahl ggf immer weniger nutzbare columns und ggf sind in einegen DFs einlzelne NA Werte in columns, die bei anderen komplett NA sind und dadurch hier nicht imputet werden
# ggf ebste Alternative: DFs mergen und NA spalten als einzelne leere NA values betrachten. So werden sowohl NA Spalten, als auch einzlene NA values in einem Schritt gelöst
impute_cohort_data <- function(cohort_data, rel_cols) {
  # Subset für relevante Spalten
  subset_data <- cohort_data[, intersect(names(cohort_data), rel_cols), drop = FALSE]
  
  # Identifiziere Spalten, die komplett NA sind
  na_cols <- names(subset_data)[colSums(is.na(subset_data)) == nrow(subset_data)]
  
  # Entferne diese Spalten temporär
  subset_data_clean <- subset_data[, !names(subset_data) %in% na_cols, drop = FALSE]
  
  # Umwandlung von Character-Spalten in Faktoren
  subset_data_clean[] <- lapply(subset_data_clean, function(x) if (is.character(x)) as.factor(x) else x)
  
  # Entferne Spalten mit nur einem einzigartigen Wert
  subset_data_clean <- subset_data_clean[, sapply(subset_data_clean, function(x) length(unique(na.omit(x))) > 1), drop = FALSE]
  
  # Führe mice durch
  ## Was hier gute parameter für m und matix sind muss ich noch researchen
  imputed_data <- mice(subset_data_clean, m=5, maxit=50, method='pmm', seed=500)
  
  # Vervollständige die Daten
  completed_data <- complete(imputed_data)
  
  # Füge die entfernten NA-Spalten wieder hinzu
  for (col in na_cols) {
    completed_data[[col]] <- NA
  }
  
  return(list(imputed = imputed_data, completed = completed_data))
}

# Relevante Spalten definieren
rel_cols <- c('AGE', 'TISSUE', 'PATH_T_STAGE', 'GLEASON_SCORE', 'GLEASON_SCORE_1', 'GLEASON_SCORE_2', 'CEP_STATUS', 'MONTH_TO_CEP', 'PRE_OPERATIVE_PSA', 'MONTH_TO_BCR', 'CLIN_T_STAGE', 'BCR_STATUS')

# Anwenden der Funktion auf alle Kohorten
imputed_cohorts <- lapply(processed_cohorts, function(cohort) {
  impute_cohort_data(cohort$pData, rel_cols)
})



################################### Mice für gemergtedn DF
library(mice)
library(dplyr)

# Funktion zum Mergen der pData Dataframes mit Typkonvertierung
clean_numeric <- function(x) {
  x <- gsub(",", ".", x)  # Replace comma with dot
  x <- gsub("[^0-9.]", "", x)  # Remove any non-numeric characters except dot
  as.numeric(x)
}
merge_pdata <- function(processed_cohorts, rel_cols) {
  merged_df <- data.frame()
  
  for (cohort_name in names(processed_cohorts)) {
    pdata <- processed_cohorts[[cohort_name]]$pData
    pdata <- pdata[, intersect(names(pdata), rel_cols), drop = FALSE]
    
    # Konvertiere Datentypen
    pdata <- pdata %>%
      mutate(across(everything(), as.character))  
    
    if (nrow(merged_df) == 0) {
      merged_df <- pdata
    } else {
      merged_df <- bind_rows(merged_df, pdata)
    }
  }
  
  # Konvertiere Spalten zu angemessenen Datentypen
  merged_df <- merged_df %>%
    mutate(
      AGE = clean_numeric(AGE),
      GLEASON_SCORE = clean_numeric(GLEASON_SCORE),
      GLEASON_SCORE_1 = clean_numeric(GLEASON_SCORE_1),
      GLEASON_SCORE_2 = clean_numeric(GLEASON_SCORE_2),
      MONTH_TO_CEP = clean_numeric(MONTH_TO_CEP),
      PRE_OPERATIVE_PSA = clean_numeric(PRE_OPERATIVE_PSA),
      MONTH_TO_BCR = clean_numeric(MONTH_TO_BCR),
      BCR_STATUS = clean_numeric(BCR_STATUS),
      across(where(is.character), as.factor)
    )
  
  return(merged_df)
}

# Relevante Spalten definieren
rel_cols <- c('AGE', 'TISSUE', 'PATH_T_STAGE', 'GLEASON_SCORE', 'GLEASON_SCORE_1', 'GLEASON_SCORE_2', 'CEP_STATUS', 'MONTH_TO_CEP', 'PRE_OPERATIVE_PSA', 'MONTH_TO_BCR', 'CLIN_T_STAGE', 'BCR_STATUS')

# Merge alle pData Dataframes
merged_pdata <- merge_pdata(processed_cohorts, rel_cols)

# Überprüfung der Datentypen
str(merged_pdata)

# Führe mice Imputation durch
imputed_data <- mice(merged_pdata, m = 5, maxit = 50, method = 'pmm', seed = 500)

# Vervollständige die Daten
completed_pData <- complete(imputed_data) 




# Funktion zum Mergen der exprs Dataframes
merge_exprs <- function(processed_cohorts) {
  merged_exprs <- data.frame()
  
  for (cohort_name in names(processed_cohorts)) {
    exprs_data <- processed_cohorts[[cohort_name]]$exprs
    
    # Füge eine Spalte hinzu, um die Kohorte zu identifizieren
    exprs_data$cohort <- cohort_name
    
    # Transponiere das DataFrame, um Gene als Spalten zu haben
    exprs_data_t <- t(exprs_data)
    exprs_data_t <- as.data.frame(exprs_data_t)
    
    # Füge die Probe-IDs als Spalte hinzu
    exprs_data_t$probe_id <- rownames(exprs_data_t)
    
    if (nrow(merged_exprs) == 0) {
      merged_exprs <- exprs_data_t
    } else {
      # Finde gemeinsame Gene
      common_genes <- intersect(colnames(merged_exprs), colnames(exprs_data_t))
      
      # Merge basierend auf gemeinsamen Genen
      merged_exprs <- merge(merged_exprs[, c("probe_id", "cohort", common_genes)], 
                            exprs_data_t[, c("probe_id", "cohort", common_genes)], 
                            all = TRUE)
    }
  }
  
  # Setze probe_id als Zeilenname und entferne die Spalte
  rownames(merged_exprs) <- merged_exprs$probe_id
  merged_exprs$probe_id <- NULL
  
  return(merged_exprs)
}

# Merge alle exprs Dataframes
merged_exprs <- merge_exprs(processed_cohorts)

# Überprüfe die Dimensionen des gemergten Dataframes
print(dim(merged_exprs))

# Zeige die ersten paar Zeilen und Spalten
print(merged_exprs[1:5, 1:10])

# Überprüfe, wie viele Gene (Spalten) wir haben
print(ncol(merged_exprs) - 1)  # -1 wegen der 'cohort' Spalte

# Überprüfe, wie viele Proben (Zeilen) wir für jede Kohorte haben
print(table(merged_exprs$cohort))




