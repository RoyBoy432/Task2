#!/bin/bash
#PBS -k o
#PBS -l nodes=1:ppn=8,vmem=100gb,walltime=10:00:00
#PBS -M wrshoema@indiana.edu
#PBS -m abe
#PBS -j oe
module load java
module load fastqc
module load bioperl
module load python
module load gcc
module load cutadapt
module load khmer
module load spades



###### THis was merged with KBS0711_contig_assembly.sh
#### We're not using this file now

cd /N/dc2/projects/muri2/Task2/GSF966/KBS0711

# 6 kb

cutadapt -q 30 -b AGATCGGAAGAGCACACGTCTGAACTCCAGTCACGTCCGCACATCTCGTA \
    -b GATCGGAAGAGCACACGTCTGAACTCCAGTCACGTCCGCACATCTCGTAT \
    --minimum-length 20 \
    -u 15 \
    -u -10 \
    -o tmp.1.fastq \
    -p tmp.2.fastq \
    GSF966-5-Jonslin-6k_S5_R1_001.fastq.gz GSF966-5-Jonslin-6k_S5_R2_001.fastq.gz

cutadapt -q 30 -b AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGTAGATCTCGGTGGTCGCC \
    --minimum-length 20 \
    -u 15 \
    -u -10 \
    -o GSF966-5-Jonslin-6k_S5_R2_001_Q30_U15_UN10.fastq.gz \
    -p GSF966-5-Jonslin-6k_S5_R1_001_Q30_U15_UN10.fastq.gz \
    tmp.2.fastq tmp.1.fastq

rm tmp.1.fastq tmp.2.fastq

# 11 kb

cutadapt -q 20 -b AGATCGGAAGAGCACACGTCTGAACTCCAGTCACGTGAAACGATCTCGTA \
    --minimum-length 20 \
    -u 15 \
    -u -10 \
    -o tmp.1.fastq \
    -p tmp.2.fastq \
    GSF966-6-Jonslin-11k_S6_R1_001.fastq.gz GSF966-6-Jonslin-11k_S6_R2_001.fastq.gz

cutadapt -q 20 -b AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGTAGATCTCGGTGGTCGCC \
    --minimum-length 20 \
    -u 15 \
    -u -10 \
    -o GSF966-6-Jonslin-11k_S6_R2_001_Q30_U15_UN10.fastq.gz \
    -p GSF966-6-Jonslin-11k_S6_R1_001_Q30_U15_UN10.fastq.gz \
    tmp.2.fastq tmp.1.fastq

rm tmp.1.fastq tmp.2.fastq

cd /N/dc2/projects/muri2/Task2/GSF-911/KBS0711

cutadapt -q 20 \
    --minimum-length 20 \
    -u 15 \
    -u -20 \
    -o tmp.1.fastq \
    -p tmp.2.fastq \
    GSF911-711_S1_L001_R1_001.fastq.gz GSF911-711_S1_L001_R2_001.fastq.gz

cutadapt -q 20 \
    --minimum-length 20 \
    -u 15 \
    -u -20 \
    -o GSF911-711_S1_L001_R2_001_Q30_U15_UN20.fastq.gz \
    -p GSF911-711_S1_L001_R1_001_Q30_U15_UN20.fastq.gz \
    tmp.2.fastq tmp.1.fastq

rm tmp.1.fastq tmp.2.fastq
