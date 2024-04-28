#!/bin/bash

INIT_GEOMETRY=$1
MOSS_UNIT=$2

X_coord=(8 2 -4 -10) # bot: (-11 -5 1 7) same for b4 & b5; top: (8 2 -4 -10) same for t6 & t7
roi_reg1='roi=[[80,1],[256,1],[256,165],[80,165]]' # top: [[80,1],[256,1],[256,165],[80,165]]  bot: [[100,1],[320,1],[320,200],[100,200]]
roi_reg2='roi=[[1,1],[220,1],[220,165],[1,165]]'   # top: [[1,1],[220,1],[220,165],[1,165]]    bot: [[1,1],[265,1],[265,200],[1,200]]

Mat_budget_incl_PCB=0.024
Mat_budget_Si=0.0005

fgeom_unit=geometry/$MOSS_UNIT

if [ -d "$fgeom_unit" ]
then
   sudo rm -rf $fgeom_unit
   mkdir -p $fgeom_unit
fi

fconfig_unit=config/$MOSS_UNIT

if [ -d "$fconfig_unit" ]
then
   sudo rm -rf $fconfig_unit
   mkdir -p $fconfig_unit
fi

for (( MOSS_REGION=0; MOSS_REGION<=3; MOSS_REGION++ ));
do

   fmoss_region=MOSS_reg$MOSS_REGION

   mkdir -p $fmoss_region
   cp -r $fmoss_region $fconfig_unit
   mv -u $fmoss_region $fgeom_unit

   fgeom_moss=$fgeom_unit/MOSS_reg$MOSS_REGION
   geom_conf=$fgeom_moss/2023-09_PS_3REF-MOSS_reg$MOSS_REGION-3REF_$MOSS_UNIT.conf

   if [ $MOSS_REGION == 0 ] || [ $MOSS_REGION == 3 ]
   then
      MAT_BUDGET=$Mat_budget_incl_PCB
   else
      MAT_BUDGET=$Mat_budget_Si
   fi

   sed -e "s/NUM/$MOSS_REGION/g" -e "s/X_COORDINATE/${X_coord[$MOSS_REGION]}/g" -e "s/MAT_BUDGET/$MAT_BUDGET/g" $INIT_GEOMETRY > $geom_conf
   
   if [ $MOSS_REGION == 1 ]
   then
      sed -i "54 i $roi_reg1" $geom_conf 
   elif [ $MOSS_REGION == 2 ]
   then
      sed -i "54 i $roi_reg2" $geom_conf 
   fi
done
