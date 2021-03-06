#!/bin/bash
#PBS -k o
#PBS -l nodes=1:ppn=8,vmem=100gb,walltime=4:00:00
#PBS -M wrshoema@umail.iu.edu
#PBS -m abe
#PBS -j oe

module rm gcc
module load gcc/4.9.2
module load gsl/1.15
module load samtools/0.1.19

cd /N/dc2/projects/muri2/Task2/LTDE/data/map_results

for d in */ ;
do
    dType="$(echo "$d" | cut -d "/" -f1-1)"
    mkdir -p "${dType}/${dType}_MAPGD"
    samtools merge "./${dType}/${dType}_MAPGD/${dType}_merged.bam" "./${dType}/"*"_mapped_sort_NOdup_sort.bam"
    samtools view -H "${dType}/${dType}_MAPGD/${dType}_merged.bam" > "${dType}/${dType}_MAPGD/${dType}_merged.header"
    samtools mpileup -q 25 -Q 25 -B "${dType}/"*"_mapped_sort_NOdup_sort.bam" \
    | /N/dc2/projects/muri2/Task2/LTDE/MAPGD-master/bin/mapgd proview -H "${dType}/${dType}_MAPGD/${dType}_merged.header" \
    | /N/dc2/projects/muri2/Task2/LTDE/MAPGD-master/bin/mapgd pool -a 22 -o "${dType}/${dType}_MAPGD/${dType}_merged"
done
