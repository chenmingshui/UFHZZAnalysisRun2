import FWCore.ParameterSet.Config as cms

process = cms.Process("UFHZZ4LAnalysis")

process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 1000
process.MessageLogger.categories.append('UFHZZ4LAna')

process.load("Configuration.StandardSequences.MagneticField_cff")
process.load("Configuration.Geometry.GeometryRecoDB_cff")
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
process.GlobalTag.globaltag='76X_mcRun2_asymptotic_v12'

process.Timing = cms.Service("Timing",
                             summaryOnly = cms.untracked.bool(True)
                             )


process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

myfilelist = cms.untracked.vstring()
myfilelist.extend( [
#'root://cmsxrootd.fnal.gov//store/mc/RunIIFall15MiniAODv1/VBF_HToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/00000/E2490ECF-CBA7-E511-9B19-001E67398458.root',
#'root://cmsxrootd.fnal.gov//store/mc/RunIIFall15MiniAODv1/WminusH_HToZZTo4L_M125_13TeV_powheg2-minlo-HWJ_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/50000/282C35FB-68A3-E511-A0C4-0CC47A4C8E5E.root',
#'root://cmsxrootd.fnal.gov//store/mc/RunIIFall15MiniAODv1/WplusH_HToZZTo4L_M125_13TeV_powheg2-minlo-HWJ_JHUgenV6_pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/20000/E2DA5AA7-C5AC-E511-97E0-0CC47A4C8E98.root'
'file:/scratch/osg/dsperka/sync_feb19/syncfile_VBF.root',
'file:/scratch/osg/dsperka/sync_feb19/syncfile_WplusH.root',
'file:/scratch/osg/dsperka/sync_feb19/syncfile_WminusH.root'
]
)

process.source = cms.Source("PoolSource",fileNames = myfilelist,
                            duplicateCheckMode = cms.untracked.string('noDuplicateCheck'),
#                            eventsToProcess = cms.untracked.VEventRange('1:15924-1:15971'),
                            inputCommands = cms.untracked.vstring('keep *',
                                                                  'drop LHEEventProduct_*_*_*',
                                                                  'drop LHERunInfoProduct_*_*_*')
                            )

process.TFileService = cms.Service("TFileService",
                                   fileName = cms.string("Sync_76X_v3.root")
#                                   fileName = cms.string("test.root")
)

# clean muons by segments 
process.boostedMuons = cms.EDProducer("PATMuonCleanerBySegments",
				     src = cms.InputTag("slimmedMuons"),
				     preselection = cms.string("track.isNonnull"),
				     passthrough = cms.string("isGlobalMuon && numberOfMatches >= 2"),
				     fractionOfSharedSegments = cms.double(0.499),
				     )

# Kalman Muon Calibrations
process.calibratedMuons = cms.EDProducer("KalmanMuonCalibrationsProducer",
				     muonsCollection = cms.InputTag("boostedMuons"),
				     isMC = cms.bool(True),
				     isSync = cms.bool(True)
				     )


process.selectedElectrons = cms.EDFilter("PATElectronSelector",
                                         src = cms.InputTag("slimmedElectrons"),
                                         cut = cms.string("pt > 5 && abs(eta)<2.5")
                                         )

process.RandomNumberGeneratorService = cms.Service("RandomNumberGeneratorService",
    calibratedPatElectrons = cms.PSet(
        initialSeed = cms.untracked.uint32(1),
        engineName = cms.untracked.string('TRandom3')
    )
)

# Electron Calibrations
process.load('EgammaAnalysis.ElectronTools.calibratedElectronsRun2_cfi')
process.calibratedPatElectrons = cms.EDProducer("CalibratedPatElectronProducerRun2",
                                        # input collections
                                        electrons = cms.InputTag('selectedElectrons'),
                                        gbrForestName = cms.string("gedelectron_p4combination_25ns"),
                                        isMC = cms.bool(True),
                                        isSynchronization = cms.bool(True),
                                        correctionFile = cms.string("EgammaAnalysis/ElectronTools/data/76X_16DecRereco_2015")
                                        )

# Electron MVA ID producers
#from PhysicsTools.SelectorUtils.tools.vid_id_tools import *
#dataFormat = DataFormat.MiniAOD
#switchOnVIDElectronIdProducer(process, dataFormat)
## define which IDs we want to produce
#my_id_modules = ['RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Spring15_25ns_nonTrig_V1_cff']
## add them to the VID producer
#for idmod in my_id_modules:
#    setupAllVIDIdsInModule(process,idmod,setupVIDElectronSelection)
#process.electronMVAValueMapProducer.srcMiniAOD = cms.InputTag("calibratedPatElectrons")

process.mvaSpring15NonTrig25nsV1 = cms.EDProducer("SlimmedElectronMvaIDProducer",
                                     mvaValuesMap = cms.InputTag("electronMVAValueMapProducer:ElectronMVAEstimatorRun2Spring15NonTrig25nsV1Values"),
                                     electronsCollection = cms.InputTag("calibratedPatElectrons"),
#                                     electronsCollection = cms.InputTag("slimmedElectrons","","PAT"),
                                     Trig = cms.bool(False),
                                     )

# FSR Photons
process.load('UFHZZAnalysisRun2.FSRPhotons.fsrPhotons_cff')

# Jet Energy Corrections
from CondCore.DBCommon.CondDBSetup_cfi import *
import os
era = "Fall15_25nsV1_MC"
dBFile = os.environ.get('CMSSW_BASE')+"/src/UFHZZAnalysisRun2/UFHZZ4LAna/data/"+era+".db"
process.jec = cms.ESSource("PoolDBESSource",
                           CondDBSetup,
                           connect = cms.string("sqlite_file:"+dBFile),
                           toGet =  cms.VPSet(
        cms.PSet(
            record = cms.string("JetCorrectionsRecord"),
            tag = cms.string("JetCorrectorParametersCollection_"+era+"_AK4PF"),
            label= cms.untracked.string("AK4PF")
            ),
        cms.PSet(
            record = cms.string("JetCorrectionsRecord"),
            tag = cms.string("JetCorrectorParametersCollection_"+era+"_AK4PFchs"),
            label= cms.untracked.string("AK4PFchs")
            ),
        )
)

process.es_prefer_jec = cms.ESPrefer("PoolDBESSource",'jec')

process.load("PhysicsTools.PatAlgos.producersLayer1.jetUpdater_cff")

process.jetCorrFactors = process.patJetCorrFactorsUpdated.clone(
    src = cms.InputTag("slimmedJets"),
    levels = ['L1FastJet', 
              'L2Relative', 
              'L3Absolute'],
    payload = 'AK4PFchs' ) 

process.slimmedJetsJEC = process.patJetsUpdated.clone(
    jetSource = cms.InputTag("slimmedJets"),
    jetCorrFactorsSource = cms.VInputTag(cms.InputTag("jetCorrFactors"))
    )

# Analyzer
process.Ana = cms.EDAnalyzer('UFHZZ4LAna',
                              photonSrc    = cms.untracked.InputTag("slimmedPhotons"),
                              electronSrc  = cms.untracked.InputTag("mvaSpring15NonTrig25nsV1","NonTrig"),
                              muonSrc      = cms.untracked.InputTag("calibratedMuons"),
                              jetSrc       = cms.untracked.InputTag("slimmedJets"),
#                              jetSrc       = cms.untracked.InputTag("slimmedJetsJEC"),
                              metSrc       = cms.untracked.InputTag("slimmedMETs"),   
                              vertexSrc    = cms.untracked.InputTag("offlineSlimmedPrimaryVertices"),
                              beamSpotSrc  = cms.untracked.InputTag("offlineBeamSpot"),
                              conversionSrc  = cms.untracked.InputTag("reducedEgamma","reducedConversions"),
                              isMC         = cms.untracked.bool(True),
                              isSignal     = cms.untracked.bool(True),
                              mH           = cms.untracked.double(125.0),
                              CrossSection = cms.untracked.double(1.0),
                              FilterEff    = cms.untracked.double(1),
                              weightEvents = cms.untracked.bool(True),
                              elRhoSrc     = cms.untracked.InputTag("fixedGridRhoFastjetAll"),
                              muRhoSrc     = cms.untracked.InputTag("fixedGridRhoFastjetAll"),
                              rhoSrcSUS    = cms.untracked.InputTag("fixedGridRhoFastjetCentralNeutral"),
                              pileupSrc    = cms.untracked.InputTag("slimmedAddPileupInfo"),
                              pfCandsSrc   = cms.untracked.InputTag("packedPFCandidates"),
                              fsrPhotonsSrc = cms.untracked.InputTag("boostedFsrPhotons"),
                              prunedgenParticlesSrc = cms.untracked.InputTag("prunedGenParticles"),
                              packedgenParticlesSrc = cms.untracked.InputTag("packedGenParticles"),
                              genJetsSrc = cms.untracked.InputTag("slimmedGenJets"),
                              generatorSrc = cms.untracked.InputTag("generator"),
                              lheInfoSrc = cms.untracked.InputTag("externalLHEProducer"),
                              reweightForPU = cms.untracked.bool(True),
                              triggerSrc = cms.InputTag("TriggerResults","","HLT"),
                              triggerObjects = cms.InputTag("selectedPatTrigger"),
                              triggerList = cms.untracked.vstring(
                                            'HLT_Ele17_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v',
                                            'HLT_Ele16_Ele12_Ele8_CaloIdL_TrackIdL_v',
                                            'HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v',
                                            'HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v',
                                            'HLT_TripleMu_12_10_5_v',
                                            'HLT_Mu8_TrkIsoVVL_Ele17_CaloIdL_TrackIdL_IsoVL_v',
                                            'HLT_Mu17_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v',
                                            'HLT_Mu8_DiEle12_CaloIdL_TrackIdL_v',
                                            'HLT_DiMu9_Ele9_CaloIdL_TrackIdL_v',
                                            'HLT_Ele23_WPLoose_Gsf_v',
                              ),
                              verbose = cms.untracked.bool(False)              
#                              verbose = cms.untracked.bool(True)              
                             )

process.p = cms.Path(process.fsrPhotonSequence*
                     process.boostedMuons*
                     process.calibratedMuons*
                     process.selectedElectrons*
                     process.calibratedPatElectrons*
#                     process.electronMVAValueMapProducer*
                     process.mvaSpring15NonTrig25nsV1*
#                     process.jetCorrFactors*
#                     process.slimmedJetsJEC*
                     process.Ana
                     )