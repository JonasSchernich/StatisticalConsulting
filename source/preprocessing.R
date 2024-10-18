library(Biobase)
library(mice)
library(dplyr)
library(impute)
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







################# einzelne Kohorten pData
output_dir <- file.path("..", "Data", "cohort_data", "pData", "original")
for (i in seq_along(processed_cohorts)) {
  name <- names(processed_cohorts[i])
  data <- processed_cohorts[[i]]$pData
  csv_file <- file.path(output_dir, paste0("cohort_", name, ".csv"))
  write.csv(data, file = csv_file, row.names = TRUE)
}

################# einzelne Kohorten exprs
output_dir <- file.path("..", "Data", "cohort_data", "exprs")
for (i in seq_along(processed_cohorts)) {
  name <- names(processed_cohorts[i])
  data <- processed_cohorts[[i]]$exprs
  csv_file <- file.path(output_dir, paste0("exprs_", name, ".csv"))
  write.csv(data, file = csv_file, row.names = TRUE)
}

################## mice für einzlene Kohorten pData
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



output_dir <- file.path("..", "Data", "cohort_data", "pData", "imputed")

for (i in seq_along(imputed_cohorts)) {
  name <- names(imputed_cohorts[i])
  data <- imputed_cohorts[[i]]$completed
  csv_file <- file.path(output_dir, paste0("cohort_", name, "_imputed.csv"))
  write.csv(data, file = csv_file, row.names = TRUE)
}


################################### Mice für gemergtedn DF

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

# Führe mice Imputation durch
imputed_data <- mice(merged_pdata, m = 5, maxit = 50, method = 'pmm', seed = 500)

# Vervollständige die Daten
completed_pData <- complete(imputed_data) 

output_dir <- file.path("..", "Data", "merged_data", "pData", "imputed")
csv_file <- file.path(output_dir, paste0("merged_imputed_pData", "_imputed.csv"))
write.csv(data, file = csv_file, row.names = TRUE)



############################ Gen Intersection
############# exprs mergen und transponieren
create_merged_exprs <- function(cohorts_dict) {
  # Extract exprs dataframes from cohorts
  exprs_dfs <- lapply(cohorts_dict, function(cohort_data) {
    if ('exprs' %in% names(cohort_data)) {
      return(cohort_data$exprs)
    }
    return(NULL)
  })
  exprs_dfs <- exprs_dfs[!sapply(exprs_dfs, is.null)]
  
  # Find common genes (row names)
  common_genes <- Reduce(intersect, lapply(exprs_dfs, rownames))
  
  # Filter dataframes for common genes
  filtered_exprs_dfs <- lapply(exprs_dfs, function(df) {
    df[common_genes, , drop = FALSE]
  })
  
  # Merge dataframes
  merged_exprs <- do.call(cbind, filtered_exprs_dfs)
  
  return(merged_exprs)
}

merged_exprs <- create_merged_exprs(processed_cohorts)

merged_exprs_t <- t(merged_exprs)

output_dir <- file.path("..", "Data", "merged_data", "exprs", "intersection")
csv_file <- file.path(output_dir, paste0("exprs_intersect", ".csv"))
write.csv(merged_exprs_t, file = csv_file, row.names = TRUE)









####################################### Common Genes
create_merged_exprs_for_imputation <- function(cohorts_dict) {
  # Extrahiere und transponiere exprs Dataframes aus den Kohorten
  exprs_dfs <- lapply(cohorts_dict, function(cohort_data) {
    if ('exprs' %in% names(cohort_data)) {
      return(t(cohort_data$exprs))  # Transponieren hier
    }
    return(NULL)
  })
  exprs_dfs <- exprs_dfs[!sapply(exprs_dfs, is.null)]
  
  # Finde alle einzigartigen Gene
  all_genes <- Reduce(union, lapply(exprs_dfs, colnames))
  
  # Erstelle einen leeren Dataframe mit allen Genen als Spalten
  all_exprs_merged <- data.frame(matrix(ncol = length(all_genes), nrow = 0))
  colnames(all_exprs_merged) <- all_genes
  
  # Füge Daten aus jeder Kohorte hinzu
  for (df in exprs_dfs) {
    # Erstelle einen temporären Dataframe mit allen Genen
    temp_df <- data.frame(matrix(NA, nrow = nrow(df), ncol = length(all_genes)))
    colnames(temp_df) <- all_genes
    
    # Fülle die vorhandenen Daten ein
    common_genes <- intersect(colnames(df), all_genes)
    temp_df[, common_genes] <- df[, common_genes]
    
    # Füge Zeilennamen hinzu 
    rownames(temp_df) <- rownames(df)
    
    # Füge zum Dataframe hinzu
    all_exprs_merged <- rbind(all_exprs_merged, temp_df)
  }
  
  return(all_exprs_merged)
}

all_exprs_merged <- create_merged_exprs_for_imputation(processed_cohorts)


output_dir <- file.path("..", "Data", "merged_data", "exprs", "all_genes")
csv_file <- file.path(output_dir, paste0("common_genes_knn_imputed", ".csv"))
write.csv(all_exprs_merged, file = csv_file, row.names = TRUE)



# Spalten mit zu vielen NAs entfernen
missing_values <- colSums(is.na(all_exprs_merged))
total_rows <- nrow(all_exprs_merged)

valid_columns <- missing_values / total_rows < 0.2

filtered_exprs <- all_exprs_merged[, valid_columns]

output_dir <- file.path("..", "Data", "merged_data", "exprs", "common_genes")
csv_file <- file.path(output_dir, paste0("common_genes", ".csv"))
write.csv(filtered_exprs, file = csv_file, row.names = TRUE)


#KNN imputation
imputed_data <- impute.knn(as.matrix(filtered_exprs[, sapply(filtered_exprs, is.numeric)]))


# Das Ergebnis ist eine Liste. Die imputierte Matrix ist im 'data' Element
imputed_matrix <- imputed_data$data

# Konvertiere zurück zu einem Dataframe, wenn nötig
imputed_df <- as.data.frame(imputed_matrix)


output_dir <- file.path("..", "Data", "merged_data", "exprs", "common_genes")
csv_file <- file.path(output_dir, paste0("common_genes_knn_imputed", ".csv"))
write.csv(filtered_exprs, file = csv_file, row.names = TRUE)












