#!/bin/sh
git clone https://github.com/VBF-HZZ/KinZfitter.git

#these corrections/calibrations will be updated later
#git cms-merge-topic rafaellopesdesa:EgammaAnalysis80_EGMSmearer_Moriond17_23Jan
#cd EgammaAnalysis/ElectronTools/data
#git clone https://github.com/ECALELFS/ScalesSmearings.git
#cd -
#git cms-merge-topic cms-met:METRecipe_8020 -u
#git cms-merge-topic cms-met:METRecipe_80X_part2 -u


# this is still 2016 calibration from backtis, may change later
git clone https://github.com/bachtis/Analysis.git -b KaMuCa_V4 KaMuCa
git clone https://github.com/cms-analysis/HiggsAnalysis-ZZMatrixElement.git ZZMatrixElement

#the following patch has been manually handled
#cp UFHZZAnalysisRun2/Utilities/fixcrab.patch ZZMatrixElement


#git cms-merge-topic -u perrozzi:HTXS_clean
 git remote add perrozzi_HTXS_clean  https://github.com/perrozzi/cmssw.git
 git fetch perrozzi_HTXS_clean
 git branch HTXS_clean perrozzi_HTXS_clean/HTXS_clean
 git checkout HTXS_clean SimDataFormats/HTXS
 git checkout HTXS_clean GeneratorInterface/RivetInterface

(cd ZZMatrixElement ; git checkout -b from-v211 v2.1.1 ; ./setup.sh -j 12)

scram b -j 8
