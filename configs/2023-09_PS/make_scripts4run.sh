#!/bin/bash
MOSS_UNIT=$1

file_path=../data/vcasb_scan_$MOSS_UNIT
# file_path=../data/$MOSS_UNIT

### Files for used for alignment
b4: run394145838_230928224026.raw
#b5: run393175726_230928034051.raw

#t6: run396111621_230930171133.raw
#t7: run395103419_230929211504.raw
#t6 high stat: run396111627_230930235306.raw

#t6 strobe:    run402161517_231004005851.raw
#t6 ibias_124: run401121214_231002161148.raw

#file_name=run401121214_231002161148.raw

for (( MOSS_REGION=0; MOSS_REGION<=3; MOSS_REGION++ ));
do
   script4run=config/$MOSS_UNIT/MOSS_reg$MOSS_REGION/script4alignment.sh
   geometry_path=../geometry/$MOSS_UNIT/MOSS_reg$MOSS_REGION

   detectors4tracking="ALPIDE_0,ALPIDE_1,ALPIDE_2,ALPIDE_4,ALPIDE_5,ALPIDE_6,MOSS_reg${MOSS_REGION}_3"

   if [ -f "$script4run" ]; then rm $script4run; fi

   echo "#!/bin/bash" >> $script4run
   echo "corry -c ../../createmask.conf -o detectors_file=$geometry_path/2023-09_PS_3REF-MOSS_reg$MOSS_REGION-3REF_$MOSS_UNIT.conf -o detectors_file_updated=$geometry_path/masked_$MOSS_UNIT.conf     -o histogram_file=masking_$MOSS_UNIT.root      -o output_directory=$MOSS_UNIT/MOSS_reg$MOSS_REGION -o EventLoaderEUDAQ2.file_name=$file_path/$file_name" >> $script4run
   echo "corry -c ../../prealign.conf   -o detectors_file=$geometry_path/masked_$MOSS_UNIT.conf                                    -o detectors_file_updated=$geometry_path/prealigned_$MOSS_UNIT.conf -o histogram_file=prealignment_$MOSS_UNIT.root -o output_directory=$MOSS_UNIT/MOSS_reg$MOSS_REGION -o EventLoaderEUDAQ2.file_name=$file_path/$file_name" >> $script4run
   echo "corry -c ../../align.conf      -o detectors_file=$geometry_path/prealigned_$MOSS_UNIT.conf                                -o detectors_file_updated=$geometry_path/aligned_$MOSS_UNIT.conf    -o histogram_file=alignment_$MOSS_UNIT.root    -o output_directory=$MOSS_UNIT/MOSS_reg$MOSS_REGION -o EventLoaderEUDAQ2.file_name=$file_path/$file_name" -o Tracking4D.require_detectors=$detectors4tracking >> $script4run

   counter=0
   file1=config/$MOSS_UNIT/MOSS_reg$MOSS_REGION/script4analysis1.sh
   if [ -f "$file1" ]; then rm $file1; fi

   file2=config/$MOSS_UNIT/MOSS_reg$MOSS_REGION/script4analysis2.sh
   if [ -f "$file2" ]; then rm $file2; fi

   cut_name=$(echo $file_path| cut -c 4-1000)

   for FILE in $cut_name/*;
   do
      prefix=$(echo $FILE| cut -d'_' -f 4)   # 6 for ibias;  5 for strobe; 4 for common scan
      prefix=$(echo $prefix| cut -d'.' -f 1)
      FILE=$(echo $FILE| cut -c 20-1000)     # 30 for ibias; 27 for strobe; 20 for common scan

      if [ $counter -lt 5 ]
      then
         echo "corry -c ../../analyse.conf -o detectors_file=$geometry_path/aligned_$MOSS_UNIT.conf -o histogram_file=analysis_${prefix}_$MOSS_UNIT.root -o output_directory=$MOSS_UNIT/MOSS_reg$MOSS_REGION -o EventLoaderEUDAQ2.file_name=$file_path/$FILE" >> $file1
      else
         echo "corry -c ../../analyse.conf -o detectors_file=$geometry_path/aligned_$MOSS_UNIT.conf -o histogram_file=analysis_${prefix}_$MOSS_UNIT.root -o output_directory=$MOSS_UNIT/MOSS_reg$MOSS_REGION -o EventLoaderEUDAQ2.file_name=$file_path/$FILE" >> $file2
      fi

      let counter++
   done
done
