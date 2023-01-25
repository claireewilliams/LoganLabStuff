#!/bin/bash -l
#SBATCH --job-name=rc-g16		# The job name
#SBATCH --ntasks=1			# One task will be run
#SBATCH --cpus-per-task=16		# The task requires 16 CPUs
#SBATCH --hint=compute_bound		# Hyperthreading is enabled, run only on cores 
					#   - 32 total CPUs will be allocated for this job.
#SBATCH --mem-per-cpu=3500M		# Allocate 3.5GB of memory per CPU
					#   - 112GB = 32*3.5GB of memory will be allocated 
#SBATCH --time=0-3:00:00		# Max run time is 3 days, this test is 10min
					#   - Use --time as command line argument to override					
#SBATCH --partition=cpu-core-0	# Submit job to the cpu test partition
#SBATCH --account=cpu-s5-lizard_project-0		# and cpu test account
#SBATCH --mail-type=FAIL		# Send mail on all state changes
#SBATCH --output=/data/gpfs/assoc/lizard_project/slurm_out/%x.%j.out		# The output file name: <job_name>.<job_id>.out
#SBATCH --error=/data/gpfs/assoc/lizard_project/slurm_err/%x.%j.err		# The error file name: <job_name>.<job_id>.err

#--------------------------------------------------------------------------------------------------
#
# Name: sm-importsumm
#
# Purpose: Run snakemake script for 16S importing
#
# Output: Output files will be written to the working directory from which the batch script was
#         submitted. The stdout file name ends in *.out. The stderr file name ends in *.err.
#         Both contain the job number.
#
# Notes: This submission script is optimized for 16 core, 112GB memory jobs. 
#
# Example submission:
#
# $ sbatch Slurm_example.sh input.yaml
#
# Example submission that sets a notification email address:
#
# $ sbatch --mail-user=williams.claire.e@gmail.com Slurm_import_summarize.sh config_A.yaml
#
#--------------------------------------------------------------------------------------------------

# Load conda environment

conda activate qiime2-2022.8 


# Error if the  input file does not exist or was not specified. Check stderr file for 
# error.
[[ -f ${1} ]] || { echo "input file does not exist" >&2; exit 1; }

# Run snakemake script
srun snakemake -s snakefile_importsummarize` ${1}