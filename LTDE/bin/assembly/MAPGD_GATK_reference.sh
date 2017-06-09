#!/bin/bash
#PBS -k o
#PBS -l nodes=1:ppn=8,vmem=100gb,walltime=24:00:00
#PBS -M wrshoema@umail.iu.edu
#PBS -m abe
#PBS -j oe

module rm gcc
module load gcc/4.9.2
module load gsl/1.15
module load samtools/0.1.19
module load python
module load java


declare -a SoilGen=("ATCC13985" "ATCC43928" "KBS0702" "KBS0707" "KBS0712" "KBS0801")

# pass string and array and check if the array contains the string
containsElement () {
  local e
  for e in "${@:2}"; do [[ "$e" == "$1" ]] && return 1; done
  return 0
}

for d in /N/dc2/projects/muri2/Task2/LTDE/data/map_results/*/ ;
do
  dType="$(echo "$d" | cut -d "/" -f10-10)"
  containsElement "$dType" "${SoilGen[@]}"
  Result="$(echo $?)"
  # 1 == True
  if [ "$Result" -eq 1 ]; then
    # get and index the reference
    #mkdir -p "${d}${dType}_MAPGD"
    #samtools merge "${d}${dType}_MAPGD/${dType}_merged.bam" "${d}"*"_mapped_sort_NOdup_sort.bam" -f
    #samtools view -H "${d}${dType}_MAPGD/${dType}_merged.bam" > "${d}${dType}_MAPGD/${dType}_merged.header"
    #samtools mpileup -q 25 -Q 25 -B "${d}"*"_mapped_sort_NOdup_sort.bam" \
    #| /N/dc2/projects/muri2/Task2/LTDE/MAPGD-master/bin/mapgd proview -H "${d}${dType}_MAPGD/${dType}_merged.header" \
    #| /N/dc2/projects/muri2/Task2/LTDE/MAPGD-master/bin/mapgd pool -a 22 -o "${d}${dType}_MAPGD/${dType}_merged"
    REF="/N/dc2/projects/muri2/Task2/LTDE/data/2016_KBSGenomes_Annotate/${dType}/G-Chr1"
    d_No_Hypeh="$(echo "$d" | cut -d "/" -f1-10)"
    for file in $d_No_Hypeh/*;
    do
      if [[ $file == *_mapped_sort_NOdup_sort.bam ]]; then
        NoExt="$(echo "${file%.*}")"

        java -Xmx2g -classpath /N/soft/rhel6/picard/picard-tools-1.107/ -jar \
            /N/soft/rhel6/picard/picard-tools-1.107/AddOrReplaceReadGroups.jar \
            I="${NoExt}.bam" \
            O="${NoExt}_fixed.bam" \
            SORT_ORDER=coordinate RGID=Rpal RGLB=bar RGPL=illumina RGSM=test_line \
            RGPU=6 CREATE_INDEX=True VALIDATION_STRINGENCY=LENIENT

        java -Xmx2g -classpath /N/soft/rhel6/picard/picard-tools-1.107/ \
            -jar /N/soft/rhel6/picard/picard-tools-1.107/CreateSequenceDictionary.jar \
            R="${REF}.fna" \
            O="${REF}.dict"

        java -Xmx2g -classpath /N/soft/rhel6/picard/picard-tools-1.107/ -jar \
            /N/soft/rhel6/gatk/3.4-0/GenomeAnalysisTK.jar \
            -T RealignerTargetCreator \
            -R "${REF}.fna" \
            -I "${NoExt}_fixed.bam" \
            -o "${NoExt}_fixed.intervals"

        java -Xmx2g -classpath /N/soft/rhel6/picard/picard-tools-1.107/ \
            -jar /N/soft/rhel6/gatk/3.4-0/GenomeAnalysisTK.jar \
            -T IndelRealigner \
            -R "${REF}.fna" \
            -I "${NoExt}_fixed.bam" \
            -targetIntervals "${NoExt}_fixed.intervals" \
            --filter_bases_not_stored \
            -o "${NoExt}_fixed_realigned.bam"

        java -Xmx2g -classpath /N/soft/rhel6/picard/picard-tools-1.107/ \
            -jar /N/soft/rhel6/gatk/3.4-0/GenomeAnalysisTK.jar -nt 4 \
            -T UnifiedGenotyper \
            -R "${REF}.fna" \
            -I "${NoExt}_fixed_realigned.bam" \
            -glm BOTH -rf BadCigar \
            -o "${NoExt}_fixed_realigned.vcf"

        java -Xmx2g -classpath /N/soft/rhel6/picard/picard-tools-1.107/ \
            -jar /N/soft/rhel6/gatk/3.4-0/GenomeAnalysisTK.jar \
            -T BaseRecalibrator -I "${NoExt}_fixed_realigned.bam" \
            -R "${REF}.fna" \
            -rf BadCigar --filter_bases_not_stored -knownSites "${NoExt}_fixed_realigned.vcf" \
            -o "${NoExt}_fixed_realigned.recal_data.grp"

        java -Xmx2g -classpath /N/soft/rhel6/picard/picard-tools-1.107/ \
            -jar /N/soft/rhel6/gatk/3.4-0/GenomeAnalysisTK.jar \
            -T PrintReads -rf BadCigar \
            -R "${REF}.fna" \
            -I "${NoExt}_fixed_realigned.bam" \
            -o "${NoExt}_fixed_realigned_mapped.bam" \
            -BQSR "${NoExt}_fixed_realigned.recal_data.grp"

        java -Xmx2g -classpath /N/soft/rhel6/picard/picard-tools-1.107/ \
            -jar /N/soft/rhel6/gatk/3.4-0/GenomeAnalysisTK.jar -nt 4 \
            -T UnifiedGenotyper \
            -R "${REF}.fna" \
            -I "${NoExt}_fixed_realigned_mapped.bam"\
            -rf BadCigar \
            -o "${NoExt}_fixed_realigned_mapped.vcf"

        java -Xmx2g -classpath /N/soft/rhel6/picard/picard-tools-1.107/ \
          -jar /N/soft/rhel6/gatk/3.4-0/GenomeAnalysisTK.jar \
          -R "${REF}.fna" \
          -T VariantsToTable \
          -V "${NoExt}_fixed_realigned_mapped.vcf" \
          -F CHROM -F POS -F ID -F REF -F ALT -F QUAL -F AC \
          -o "${NoExt}_fixed_realigned_mapped.txt"

        subDir="$(echo "$file" | cut -d "_" -f1-2)"
        mkdir -p $subDir
        mv -v "${subDir}"* "${subDir}/"
      else
        continue
      fi
    done
  else
    continue
  fi
done