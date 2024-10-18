'''
- wd sollte "~/Code/source" sein
- code ist noch nicht final (imputationsmethoden etc) aber struktur sollte passen
'''
library(Biobase)
library(mice)
library(dplyr)
library(impute)

# Function to load and convert ExpressionSet objects
load_cohorts <- function(rds_file_paths) {
  all_cohorts <- list()
  for (rds_file_path in rds_file_paths) {
    cohorts <- readRDS(file.path("..", "data", rds_file_path))
    cohorts_list <- lapply(cohorts, function(eset) {
      list(
        pData = as.data.frame(pData(eset)),
        fData = as.data.frame(fData(eset)),
        exprs = as.data.frame(exprs(eset))
      )
    })
    all_cohorts <- c(all_cohorts, cohorts_list)
  }
  return(all_cohorts)
}

# Function to standardize expression data
standardize <- function(z) {
  rowmean <- apply(z, 1, mean, na.rm = TRUE)
  rowsd <- apply(z, 1, sd, na.rm = TRUE)
  rv <- sweep(z, 1, rowmean, "-")
  rv <- sweep(rv, 1, rowsd, "/")
  return(rv)
}

# Function to create CSV files for individual cohorts
create_cohort_csvs <- function(processed_cohorts) {
  # pData
  pdata_dir <- file.path("..", "data", "cohort_data", "pData", "original")
  dir.create(pdata_dir, recursive = TRUE, showWarnings = FALSE)
  for (i in seq_along(processed_cohorts)) {
    name <- names(processed_cohorts)[i]
    write.csv(processed_cohorts[[i]]$pData, file.path(pdata_dir, paste0("cohort_", name, ".csv")), row.names = TRUE)
  }
  
  # exprs
  exprs_dir <- file.path("..", "data", "cohort_data", "exprs")
  dir.create(exprs_dir, recursive = TRUE, showWarnings = FALSE)
  for (i in seq_along(processed_cohorts)) {
    name <- names(processed_cohorts)[i]
    write.csv(processed_cohorts[[i]]$exprs, file.path(exprs_dir, paste0("exprs_", name, ".csv")), row.names = TRUE)
  }
}

create_merged_csvs <- function(processed_cohorts) {
  # Define relevant columns
  rel_cols <- c('AGE', 'TISSUE', 'PATH_T_STAGE', 'GLEASON_SCORE', 'GLEASON_SCORE_1', 'GLEASON_SCORE_2', 
                'CEP_STATUS', 'MONTH_TO_CEP', 'PRE_OPERATIVE_PSA', 'MONTH_TO_BCR', 'CLIN_T_STAGE', 'BCR_STATUS')
  
  # Merged pData
  pdata_list <- lapply(processed_cohorts, function(x) x$pData)
  
  # Find common columns across all pData dataframes and intersect with rel_cols
  common_columns <- Reduce(intersect, c(list(rel_cols), lapply(pdata_list, colnames)))
  
  # Merge pData, keeping only common relevant columns
  merged_pdata <- do.call(rbind, lapply(pdata_list, function(x) x[, common_columns, drop = FALSE]))
  
  merged_pdata_dir <- file.path("..", "data", "merged_data", "pData", "original")
  dir.create(merged_pdata_dir, recursive = TRUE, showWarnings = FALSE)
  write.csv(merged_pdata, file.path(merged_pdata_dir, "merged_original_pData.csv"), row.names = TRUE)
  
  # Merged exprs (intersection)
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
  
  merged_exprs_dir <- file.path("..", "data", "merged_data", "exprs", "intersection")
  dir.create(merged_exprs_dir, recursive = TRUE, showWarnings = FALSE)
  write.csv(merged_exprs, file.path(merged_exprs_dir, "exprs_intersect.csv"), row.names = TRUE)
  
  return(list(merged_pdata = merged_pdata, merged_exprs = merged_exprs))
}

# Function to impute cohort data
impute_cohort_data <- function(cohort_data, rel_cols) {
  # Subset for relevant columns
  subset_data <- cohort_data[, intersect(names(cohort_data), rel_cols), drop = FALSE]
  
  # Identify columns that are completely NA
  na_cols <- names(subset_data)[colSums(is.na(subset_data)) == nrow(subset_data)]
  
  # Remove these columns temporarily
  subset_data_clean <- subset_data[, !names(subset_data) %in% na_cols, drop = FALSE]
  
  # Convert character columns to factors
  subset_data_clean[] <- lapply(subset_data_clean, function(x) if (is.character(x)) as.factor(x) else x)
  
  # Remove columns with only one unique value
  subset_data_clean <- subset_data_clean[, sapply(subset_data_clean, function(x) length(unique(na.omit(x))) > 1), drop = FALSE]
  
  # Perform mice imputation
  imputed_data <- mice(subset_data_clean, m=5, maxit=50, method='pmm', seed=500)
  
  # Complete the data
  completed_data <- complete(imputed_data)
  
  # Add back the removed NA columns
  for (col in na_cols) {
    completed_data[[col]] <- NA
  }
  
  return(list(imputed = imputed_data, completed = completed_data))
}

# Function to merge pData dataframes with type conversion
merge_pdata <- function(processed_cohorts, rel_cols) {
  pdata_list <- lapply(processed_cohorts, function(x) x$pData)
  
  # Find common columns across all pData dataframes
  common_columns <- Reduce(intersect, lapply(pdata_list, colnames))
  
  # Intersect common columns with rel_cols
  common_rel_cols <- intersect(common_columns, rel_cols)
  
  merged_df <- do.call(rbind, lapply(pdata_list, function(x) x[, common_rel_cols, drop = FALSE]))
  
  # Convert columns to appropriate data types
  merged_df <- merged_df %>%
    mutate(across(everything(), as.character)) %>%
    mutate(
      AGE = as.numeric(AGE),
      GLEASON_SCORE = as.numeric(GLEASON_SCORE),
      GLEASON_SCORE_1 = as.numeric(GLEASON_SCORE_1),
      GLEASON_SCORE_2 = as.numeric(GLEASON_SCORE_2),
      MONTH_TO_CEP = as.numeric(MONTH_TO_CEP),
      PRE_OPERATIVE_PSA = as.numeric(PRE_OPERATIVE_PSA),
      MONTH_TO_BCR = as.numeric(MONTH_TO_BCR),
      BCR_STATUS = as.numeric(BCR_STATUS),
      across(where(is.character), as.factor)
    )
  
  return(merged_df)
}

# Function to create merged expression data for imputation
create_merged_exprs_for_imputation <- function(cohorts_dict) {
  # Extract and transpose exprs dataframes from cohorts
  exprs_dfs <- lapply(cohorts_dict, function(cohort_data) {
    if ('exprs' %in% names(cohort_data)) {
      return(t(cohort_data$exprs))
    }
    return(NULL)
  })
  exprs_dfs <- exprs_dfs[!sapply(exprs_dfs, is.null)]
  
  # Find all unique genes
  all_genes <- Reduce(union, lapply(exprs_dfs, colnames))
  
  # Create an empty dataframe with all genes as columns
  all_exprs_merged <- data.frame(matrix(ncol = length(all_genes), nrow = 0))
  colnames(all_exprs_merged) <- all_genes
  
  # Add data from each cohort
  for (df in exprs_dfs) {
    temp_df <- data.frame(matrix(NA, nrow = nrow(df), ncol = length(all_genes)))
    colnames(temp_df) <- all_genes
    
    common_genes <- intersect(colnames(df), all_genes)
    temp_df[, common_genes] <- df[, common_genes]
    
    rownames(temp_df) <- rownames(df)
    
    all_exprs_merged <- rbind(all_exprs_merged, temp_df)
  }
  
  return(all_exprs_merged)
}

# Main function
main <- function(rds_file_names) {
  # Load and preprocess cohorts
  cohorts <- load_cohorts(rds_file_names)
  
  # Standardize expression data
  processed_cohorts <- lapply(cohorts, function(cohort) {
    cohort$exprs <- standardize(as.matrix(cohort$exprs))
    return(cohort)
  })
  
  # Create CSV files for individual cohorts
  create_cohort_csvs(processed_cohorts)
  
  # Create CSV files for merged data
  merged_data <- create_merged_csvs(processed_cohorts)
  merged_pdata <- merged_data$merged_pdata
  
  # Define relevant columns for imputation
  rel_cols <- c('AGE', 'TISSUE', 'PATH_T_STAGE', 'GLEASON_SCORE', 'GLEASON_SCORE_1', 'GLEASON_SCORE_2', 
                'CEP_STATUS', 'MONTH_TO_CEP', 'PRE_OPERATIVE_PSA', 'MONTH_TO_BCR', 'CLIN_T_STAGE', 'BCR_STATUS')
  
  # Impute individual cohorts
  imputed_cohorts <- lapply(processed_cohorts, function(cohort) {
    impute_cohort_data(cohort$pData, rel_cols)
  })
  
  # Save imputed individual cohorts
  imputed_dir <- file.path("..", "data", "cohort_data", "pData", "imputed")
  dir.create(imputed_dir, recursive = TRUE, showWarnings = FALSE)
  for (i in seq_along(imputed_cohorts)) {
    name <- names(imputed_cohorts)[i]
    write.csv(imputed_cohorts[[i]]$completed, file.path(imputed_dir, paste0("cohort_", name, "_imputed.csv")), row.names = TRUE)
  }
  
  # Merge pData
  merged_pdata <- merge_pdata(processed_cohorts, rel_cols)
  
  # Impute merged pData
  imputed_merged_data <- mice(merged_pdata, m = 5, maxit = 50, method = 'pmm', seed = 500)
  completed_merged_pData <- complete(imputed_merged_data)
  
  # Save imputed merged pData
  merged_imputed_dir <- file.path("..", "data", "merged_data", "pData", "imputed")
  dir.create(merged_imputed_dir, recursive = TRUE, showWarnings = FALSE)
  write.csv(completed_merged_pData, file.path(merged_imputed_dir, "merged_imputed_pData.csv"), row.names = TRUE)
  
  # Create merged expression data for imputation
  all_exprs_merged <- create_merged_exprs_for_imputation(processed_cohorts)
  
  # Save all genes expression data
  all_genes_dir <- file.path("..", "data", "merged_data", "exprs", "all_genes")
  dir.create(all_genes_dir, recursive = TRUE, showWarnings = FALSE)
  write.csv(all_exprs_merged, file.path(all_genes_dir, "all_genes.csv"), row.names = TRUE)
  
  # Filter expression data
  missing_values <- colSums(is.na(all_exprs_merged))
  total_rows <- nrow(all_exprs_merged)
  valid_columns <- missing_values / total_rows < 0.2
  filtered_exprs <- all_exprs_merged[, valid_columns]
  
  # Save common genes expression data
  common_genes_dir <- file.path("..", "data", "merged_data", "exprs", "common_genes")
  dir.create(common_genes_dir, recursive = TRUE, showWarnings = FALSE)
  write.csv(filtered_exprs, file.path(common_genes_dir, "common_genes.csv"), row.names = TRUE)
  
  
  # KNN imputation for expression data
  imputed_expr_data <- impute.knn(as.matrix(filtered_exprs[, sapply(filtered_exprs, is.numeric)]))
  imputed_expr_df <- as.data.frame(imputed_expr_data$data)
  
  # Save KNN imputed expression data
  write.csv(imputed_expr_df, file.path(common_genes_dir, "common_genes_knn_imputed.csv"), row.names = TRUE)
  
  return(list(processed_cohorts = processed_cohorts, 
              imputed_cohorts = imputed_cohorts, 
              merged_pdata = merged_pdata,
              completed_merged_pData = completed_merged_pData,
              filtered_exprs = filtered_exprs,
              imputed_expr_df = imputed_expr_df))
}

# Run the main function
rds_file_names <- c("PCa_cohorts.Rds") # more can be added for example c("PCa_cohorts.Rds", "PCa_cohorts_2.Rds")
result <- main(rds_file_names)






