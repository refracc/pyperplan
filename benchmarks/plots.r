# Load necessary libraries
library(ggplot2)
library(dplyr)
library(reshape2)

# Load the data
setwd("/Users/refracc/Documents/PhD/pyperplan/benchmarks")
file_path <- "collected.csv"
data <- read.csv(file_path)

# Inspect the data
str(data)
sum(is.na(data))

# Remove rows with missing values
data <- na.omit(data)

# Create a directory for plots if it doesn't exist
if(!dir.exists("plots")) dir.create("plots")

# Function to save plots as PDF
save_plot <- function(plot, filename) {
  ggsave(paste0("plots/", filename, ".pdf"), plot, device = "pdf")
}

# 1. Relationship between CPU and wall time for datalog generation
p1 <- ggplot(data, aes(x=datalog_generation_cpu, y=datalog_generation_wall, colour=domain)) +
  geom_point(alpha=0.5) +
  facet_wrap(~heuristic) +
  labs(title="Datalog Generation: CPU vs Wall Time by Domain and Heuristic",
       x="Datalog Generation CPU Time",
       y="Datalog Generation Wall Time") +
  theme_minimal()
save_plot(p1, "datalog_cpu_vs_wall")

# 2. Boxplot of peak memory usage by domain
p2 <- ggplot(data, aes(x=domain, y=translator_peak_mem, fill=domain)) +
  geom_boxplot() +
  facet_wrap(~heuristic) +
  labs(title="Peak Memory Usage by Domain and Heuristic",
       x="Domain",
       y="Translator Peak Memory") +
  theme(axis.text.x = element_text(angle=45, hjust=1))
save_plot(p2, "peak_memory_by_domain")

# 3. Histogram of total translator time
p3 <- ggplot(data, aes(x=total_translator_time, fill=domain)) +
  geom_histogram(bins=30, colour="black") +
  facet_wrap(~heuristic) +
  labs(title="Total Translator Time Distribution by Domain and Heuristic",
       x="Total Translator Time",
       y="Frequency") +
  theme_minimal()
save_plot(p3, "translator_time_distribution")

# 4. Density plot of simplified effect conditions
p4 <- ggplot(data, aes(x=effect_conditions_simplified, fill=domain)) +
  geom_density(alpha=0.5) +
  facet_wrap(~heuristic) +
  labs(title="Effect Conditions Simplified Density by Domain and Heuristic",
       x="Effect Conditions Simplified",
       y="Density")
save_plot(p4, "effect_conditions_density")

# 5. Correlation heatmap of numeric variables remains unchanged
numeric_data <- data %>% select_if(is.numeric)
cor_matrix <- cor(numeric_data, use="complete.obs")
melted_cor <- melt(cor_matrix)

p5 <- ggplot(melted_cor, aes(Var1, Var2, fill=value)) +
  geom_tile() +
  scale_fill_gradient2(low="blue", high="red", mid="white",
                       midpoint=0, limit=c(-1,1), space="Lab",
                       name="Correlation") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle=45, vjust=1, hjust=1)) +
  labs(title="Correlation Heatmap of Numeric Variables")
save_plot(p5, "correlation_heatmap")

# Additional detailed plots

# 16. Scatterplot of final queue length vs total queue pushes by domain and heuristic
p16 <- ggplot(data, aes(x=final_queue_length, y=total_queue_pushes, colour=domain)) +
  geom_point(alpha=0.5) +
  facet_wrap(~heuristic) +
  labs(title="Final Queue Length vs Total Queue Pushes by Domain and Heuristic",
       x="Final Queue Length",
       y="Total Queue Pushes")
save_plot(p16, "queue_length_vs_pushes")

# 17. Boxplot of search exit code by domain and heuristic
p17 <- ggplot(data, aes(x=domain, y=search_exit_code, fill=domain)) +
  geom_boxplot() +
  facet_wrap(~heuristic) +
  labs(title="Search Exit Code by Domain and Heuristic",
       x="Domain",
       y="Search Exit Code")
save_plot(p17, "search_exit_code_by_domain")

# 18. Density plot of writing output wall time by domain and heuristic
p18 <- ggplot(data, aes(x=writing_output_wall, fill=domain)) +
  geom_density(alpha=0.5) +
  facet_wrap(~heuristic) +
  labs(title="Writing Output Wall Time Density by Domain and Heuristic",
       x="Writing Output Wall Time",
       y="Density")
save_plot(p18, "output_wall_time_density")

# 19. Scatterplot of model preparation CPU vs wall time by domain and heuristic
p19 <- ggplot(data, aes(x=model_preparation_cpu, y=model_preparation_wall, colour=domain)) +
  geom_point(alpha=0.5) +
  facet_wrap(~heuristic) +
  labs(title="Model Preparation: CPU vs Wall Time by Domain and Heuristic",
       x="Model Preparation CPU Time",
       y="Model Preparation Wall Time")
save_plot(p19, "model_prep_cpu_vs_wall")

# 20. Histogram of translator operators by domain and heuristic
p20 <- ggplot(data, aes(x=translator_operators, fill=domain)) +
  geom_histogram(bins=25, colour="black") +
  facet_wrap(~heuristic) +
  labs(title="Translator Operators Distribution by Domain and Heuristic",
       x="Translator Operators",
       y="Frequency")
save_plot(p20, "translator_operators_distribution")
