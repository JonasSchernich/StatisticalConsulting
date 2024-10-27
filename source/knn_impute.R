library(Biobase)
library(impute)
library(caret)

# Helper functions from original preprocessing
load_cohorts <- function(rds_file_paths) {
  all_cohorts <- list()
  for (rds_file_path in rds_file_paths) {
    cohorts <- readRDS(file.path("..", "data", rds_file_path))
    cohorts_list <- lapply(cohorts, function(eset) {
      list(
        exprs = as.data.frame(exprs(eset))
      )
    })
    all_cohorts <- c(all_cohorts, cohorts_list)
  }
  return(all_cohorts)
}

standardize <- function(z) {
  rowmean <- apply(z, 1, mean, na.rm = TRUE)
  rowsd <- apply(z, 1, sd, na.rm = TRUE)
  rv <- sweep(z, 1, rowmean, "-")
  rv <- sweep(rv, 1, rowsd, "/")
  return(rv)
}

create_merged_exprs_for_imputation <- function(cohorts_dict) {
  exprs_dfs <- lapply(names(cohorts_dict), function(cohort_name) {
    cohort_data <- cohorts_dict[[cohort_name]]
    if ('exprs' %in% names(cohort_data)) {
      df <- t(cohort_data$exprs)
      rownames(df) <- paste(cohort_name, rownames(df), sep=".")
      return(df)
    }
    return(NULL)
  })
  exprs_dfs <- exprs_dfs[!sapply(exprs_dfs, is.null)]
  
  all_genes <- Reduce(union, lapply(exprs_dfs, colnames))
  all_exprs_merged <- data.frame(matrix(ncol = length(all_genes), nrow = 0))
  colnames(all_exprs_merged) <- all_genes
  
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

# Function to evaluate KNN imputation
evaluate_knn_imputation <- function(data, k, prop_missing = 0.05) {
  # Convert data to matrix
  data_matrix <- as.matrix(data)
  
  # Create mask of non-NA values
  non_na_mask <- !is.na(data_matrix)
  
  # Create vector of all non-NA values with their positions
  non_na_positions <- which(non_na_mask, arr.ind = TRUE)
  
  # Randomly select positions to remove
  set.seed(42)
  n_to_remove <- floor(nrow(non_na_positions) * prop_missing)
  remove_indices <- sample(1:nrow(non_na_positions), n_to_remove)
  positions_to_remove <- non_na_positions[remove_indices, ]
  
  # Store true values before removing them
  true_values <- data_matrix[positions_to_remove]
  
  # Create test dataset with artificially introduced NAs
  test_data <- data_matrix
  test_data[positions_to_remove] <- NA
  
  # Perform KNN imputation
  imputed_data <- impute.knn(test_data, k = k)$data
  
  # Get predicted values
  predicted_values <- imputed_data[positions_to_remove]
  
  # Calculate error metrics
  rmse <- sqrt(mean((true_values - predicted_values)^2))
  mae <- mean(abs(true_values - predicted_values))
  r_squared <- cor(true_values, predicted_values)^2
  
  return(list(
    rmse = rmse,
    mae = mae,
    r_squared = r_squared,
    true_values = true_values,
    predicted_values = predicted_values
  ))
}

# Main analysis function
analyze_knn_imputation <- function(rds_file_names) {
  # Load and process data
  cohorts <- load_cohorts(rds_file_names)
  
  # Standardize expression data
  processed_cohorts <- lapply(cohorts, function(cohort) {
    cohort$exprs <- standardize(as.matrix(cohort$exprs))
    return(cohort)
  })
  
  # Create merged expression data
  all_exprs_merged <- create_merged_exprs_for_imputation(processed_cohorts)
  
  # Filter for genes with < 20% missing values
  missing_values <- colSums(is.na(all_exprs_merged))
  total_rows <- nrow(all_exprs_merged)
  valid_columns <- missing_values / total_rows < 0.2
  filtered_exprs <- all_exprs_merged[, valid_columns]
  
  # Define k values to test
  k_values <- c(5, 10,11, 12, 13, 14, 15, 20, 25)
  
  # Evaluate each k value
  results <- lapply(k_values, function(k) {
    cat(sprintf("\nEvaluating k=%d...\n", k))
    evaluate_knn_imputation(filtered_exprs, k)
  })
  
  # Create results directory if it doesn't exist
  dir.create("../results", showWarnings = FALSE)
  
  # Compile results
  performance_df <- data.frame(
    k = k_values,
    rmse = sapply(results, function(x) x$rmse),
    mae = sapply(results, function(x) x$mae),
    r_squared = sapply(results, function(x) x$r_squared)
  )
  
  # Plot results
  pdf(file = "../results/knn_imputation_analysis.pdf")
  par(mfrow = c(2, 2))
  
  # RMSE plot
  plot(performance_df$k, performance_df$rmse, 
       type = "b", 
       main = "RMSE vs k",
       xlab = "k",
       ylab = "RMSE")
  
  # MAE plot
  plot(performance_df$k, performance_df$mae, 
       type = "b", 
       main = "MAE vs k",
       xlab = "k",
       ylab = "MAE")
  
  # R-squared plot
  plot(performance_df$k, performance_df$r_squared, 
       type = "b", 
       main = "R-squared vs k",
       xlab = "k",
       ylab = "R-squared")
  
  dev.off()
  
  # Find optimal k
  optimal_k <- k_values[which.min(performance_df$rmse)]
  
  # Print summary
  cat("\nImputation Performance Summary:\n")
  print(performance_df)
  cat(sprintf("\nOptimal k value (based on RMSE): %d\n", optimal_k))
  
  # Save results to CSV
  write.csv(performance_df, "../results/knn_imputation_performance.csv", row.names = FALSE)
  
  return(list(
    performance_df = performance_df,
    optimal_k = optimal_k,
    detailed_results = results
  ))
}

# Run the analysis
rds_file_names <- c("PCa_cohorts.Rds")
results <- analyze_knn_imputation(rds_file_names)

