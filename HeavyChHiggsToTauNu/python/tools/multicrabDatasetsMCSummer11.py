import multicrabDatasetsCommon as common

# For pattuples: ~15kev/job (~20 kB/event on average, depending trigger selection efficiency)
# For analysis: ~500kev/job

# Default signal cross section taken the same as ttbar

datasets = {
    # Signal WH
    "TTToHplusBWB_M80_Summer11": {
        "dataVersion": "42Xmc",
        "crossSection": 165,
        "data": {
            "AOD": {
                "datasetpath": "/TTToHplusBWB_M-80_7TeV-pythia6-tauola/Summer11-PU_S4_START42_V11-v1/AODSIM",
                "number_of_jobs": 20, # Adjusted for PATtuple file size
            },
            "pattuple_v13": {
                "dbs_url": common.pattuple_dbs,
                "datasetpath": "/TTToHplusBWB_M-80_7TeV-pythia6-tauola/local-Summer11_PU_S4_START42_V11_v1_AODSIM_pattuple_v13-f4fa5e38ef8e2164af1f351b44ad93c5/USER",
                "number_of_jobs": 1
            },
        }
    },
    "TTToHplusBWB_M90_Summer11": {
        "dataVersion": "42Xmc",
        "crossSection": 165,
        "data": {
            "AOD": {
                "datasetpath": "/TTToHplusBWB_M-90_7TeV-pythia6-tauola/Summer11-PU_S4_START42_V11-v1/AODSIM",
                "number_of_jobs": 20, # Adjusted for PATtuple file size
            },
            "pattuple_v13": {
                "dbs_url": common.pattuple_dbs,
                "datasetpath": "/TTToHplusBWB_M-90_7TeV-pythia6-tauola/local-Summer11_PU_S4_START42_V11_v1_AODSIM_pattuple_v13-f4fa5e38ef8e2164af1f351b44ad93c5/USER",
                "number_of_jobs": 1
            },
        }
    },
    "TTToHplusBWB_M100_Summer11": {
        "dataVersion": "42Xmc",
        "crossSection": 165,
        "data": {
            "AOD": {
                "datasetpath": "/TTToHplusBWB_M-100_7TeV-pythia6-tauola/Summer11-PU_S4_START42_V11-v1/AODSIM",
                "number_of_jobs": 20, # Adjusted for PATtuple file size
            },
            "pattuple_v13": {
                "dbs_url": common.pattuple_dbs,
                "datasetpath": "/TTToHplusBWB_M-100_7TeV-pythia6-tauola/local-Summer11_PU_S4_START42_V11_v1_AODSIM_pattuple_v13-f4fa5e38ef8e2164af1f351b44ad93c5/USER",
                "number_of_jobs": 1
            },
        }
    },
    "TTToHplusBWB_M120_Summer11": {
        "dataVersion": "42Xmc",
        "crossSection": 165,
        "data": {
            "AOD": {
                "datasetpath": "/TTToHplusBWB_M-120_7TeV-pythia6-tauola/Summer11-PU_S4_START42_V11-v1/AODSIM",
                "number_of_jobs": 20, # Adjusted for PATtuple file size
            },
            "pattuple_v13": {
                "dbs_url": common.pattuple_dbs,
                "datasetpath": "/TTToHplusBWB_M-120_7TeV-pythia6-tauola/local-Summer11_PU_S4_START42_V11_v1_AODSIM_pattuple_v13-f4fa5e38ef8e2164af1f351b44ad93c5/USER",
                "number_of_jobs": 1
            },
        }
    },
    "TTToHplusBWB_M140_Summer11": {
        "dataVersion": "42Xmc",
        "crossSection": 165,
        "data": {
            "AOD": {
                "datasetpath": "/TTToHplusBWB_M-140_7TeV-pythia6-tauola/Summer11-PU_S4_START42_V11-v1/AODSIM",
                "number_of_jobs": 20, # Adjusted for PATtuple file size
            },
            "pattuple_v13": {
                "dbs_url": common.pattuple_dbs,
                "datasetpath": "/TTToHplusBWB_M-140_7TeV-pythia6-tauola/local-Summer11_PU_S4_START42_V11_v1_AODSIM_pattuple_v13-f4fa5e38ef8e2164af1f351b44ad93c5/USER",
                "number_of_jobs": 1
            },
        }
    },
    "TTToHplusBWB_M150_Summer11": {
        "dataVersion": "42Xmc",
        "crossSection": 165,
        "data": {
            "AOD": {
                "datasetpath": "/TTToHplusBWB_M-150_7TeV-pythia6-tauola/Summer11-PU_S4_START42_V11-v1/AODSIM",
                "number_of_jobs": 20, # Adjusted for PATtuple file size
            },
            "pattuple_v13": {
                "dbs_url": common.pattuple_dbs,
                "datasetpath": "/TTToHplusBWB_M-150_7TeV-pythia6-tauola/local-Summer11_PU_S4_START42_V11_v1_AODSIM_pattuple_v13-f4fa5e38ef8e2164af1f351b44ad93c5/USER",
                "number_of_jobs": 1
            },
        }
    },
    "TTToHplusBWB_M155_Summer11": {
        "dataVersion": "42Xmc",
        "crossSection": 165,
        "data": {
            "AOD": {
                "datasetpath": "/TTToHplusBWB_M-155_7TeV-pythia6-tauola/Summer11-PU_S4_START42_V11-v1/AODSIM",
                "number_of_jobs": 20, # Adjusted for PATtuple file size
            },
            "pattuple_v13": {
                "dbs_url": common.pattuple_dbs,
                "datasetpath": "/TTToHplusBWB_M-155_7TeV-pythia6-tauola/local-Summer11_PU_S4_START42_V11_v1_AODSIM_pattuple_v13-f4fa5e38ef8e2164af1f351b44ad93c5/USER",
                "number_of_jobs": 1
            },
        }
    },
    "TTToHplusBWB_M160_Summer11": {
        "dataVersion": "42Xmc",
        "crossSection": 165,
        "data": {
            "AOD": {
                "datasetpath": "/TTToHplusBWB_M-160_7TeV-pythia6-tauola/Summer11-PU_S4_START42_V11-v1/AODSIM",
                "number_of_jobs": 20, # Adjusted for PATtuple file size
            },
            "pattuple_v13": {
                "dbs_url": common.pattuple_dbs,
                "datasetpath": "/TTToHplusBWB_M-160_7TeV-pythia6-tauola/local-Summer11_PU_S4_START42_V11_v1_AODSIM_pattuple_v13-f4fa5e38ef8e2164af1f351b44ad93c5/USER",
                "number_of_jobs": 1
            },
        }
    },
    # Signal HH
    "TTToHplusBHminusB_M80_Summer11": {
        "dataVersion": "42Xmc",
        "crossSection": 165,
        "data": {
            "AOD": {
                "datasetpath": "/TTToHplusBHminusB_M-80_7TeV-pythia6-tauola/Summer11-PU_S4_START42_V11-v1/AODSIM",
                "number_of_jobs": 20, # Adjusted for PATtuple file size
            },
            "pattuple_v13": {
                "dbs_url": common.pattuple_dbs,
                "datasetpath": "/TTToHplusBHminusB_M-80_7TeV-pythia6-tauola/local-Summer11_PU_S4_START42_V11_v1_AODSIM_pattuple_v13-f4fa5e38ef8e2164af1f351b44ad93c5/USER",
                "number_of_jobs": 1
            },
        }
    },
    "TTToHplusBHminusB_M100_Summer11": {
        "dataVersion": "42Xmc",
        "crossSection": 165,
        "data": {
            "AOD": {
                "datasetpath": "/TTToHplusBHminusB_M-100_7TeV-pythia6-tauola/Summer11-PU_S4_START42_V11-v1/AODSIM",
                "number_of_jobs": 20, # Adjusted for PATtuple file size
            },
            "pattuple_v13": {
                "dbs_url": common.pattuple_dbs,
                "datasetpath": "/TTToHplusBHminusB_M-100_7TeV-pythia6-tauola/local-Summer11_PU_S4_START42_V11_v1_AODSIM_pattuple_v13-f4fa5e38ef8e2164af1f351b44ad93c5/USER",
                "number_of_jobs": 1
            },
        }
    },
    "TTToHplusBHminusB_M120_Summer11": {
        "dataVersion": "42Xmc",
        "crossSection": 165,
        "data": {
            "AOD": {
                "datasetpath": "/TTToHplusBHminusB_M-120_7TeV-pythia6-tauola/Summer11-PU_S4_START42_V11-v1/AODSIM",
                "number_of_jobs": 20, # Adjusted for PATtuple file size
            },
            "pattuple_v13": {
                "dbs_url": common.pattuple_dbs,
                "datasetpath": "/TTToHplusBHminusB_M-120_7TeV-pythia6-tauola/local-Summer11_PU_S4_START42_V11_v1_AODSIM_pattuple_v13-f4fa5e38ef8e2164af1f351b44ad93c5/USER",
                "number_of_jobs": 1
            },
        }
    },
    "TTToHplusBHminusB_M140_Summer11": {
        "dataVersion": "42Xmc",
        "crossSection": 165,
        "data": {
            "AOD": {
                "datasetpath": "/TTToHplusBHminusB_M-140_7TeV-pythia6-tauola/Summer11-PU_S4_START42_V11-v1/AODSIM",
                "number_of_jobs": 20, # Adjusted for PATtuple file size
            },
            "pattuple_v13": {
                "dbs_url": common.pattuple_dbs,
                "datasetpath": "/TTToHplusBHminusB_M-140_7TeV-pythia6-tauola/local-Summer11_PU_S4_START42_V11_v1_AODSIM_pattuple_v13-f4fa5e38ef8e2164af1f351b44ad93c5/USER",
                "number_of_jobs": 1
            },
        }
    },
    "TTToHplusBHminusB_M150_Summer11": {
        "dataVersion": "42Xmc",
        "crossSection": 165,
        "data": {
            "AOD": {
                "datasetpath": "/TTToHplusBHminusB_M-150_7TeV-pythia6-tauola/Summer11-PU_S4_START42_V11-v1/AODSIM",
                "number_of_jobs": 20, # Adjusted for PATtuple file size
            },
            "pattuple_v13": {
                "dbs_url": common.pattuple_dbs,
                "datasetpath": "/TTToHplusBHminusB_M-150_7TeV-pythia6-tauola/local-Summer11_PU_S4_START42_V11_v1_AODSIM_pattuple_v13-f4fa5e38ef8e2164af1f351b44ad93c5/USER",
                "number_of_jobs": 1
            },
        }
    },
    "TTToHplusBHminusB_M155_Summer11": {
        "dataVersion": "42Xmc",
        "crossSection": 165,
        "data": {
            "AOD": {
                "datasetpath": "/TTToHplusBHminusB_M-155_7TeV-pythia6-tauola/Summer11-PU_S4_START42_V11-v1/AODSIM",
                "number_of_jobs": 20, # Adjusted for PATtuple file size
            },
            "pattuple_v13": {
                "dbs_url": common.pattuple_dbs,
                "datasetpath": "/TTToHplusBHminusB_M-155_7TeV-pythia6-tauola/local-Summer11_PU_S4_START42_V11_v1_AODSIM_pattuple_v13-f4fa5e38ef8e2164af1f351b44ad93c5/USER",
                "number_of_jobs": 1
            },
        }
    },
    "TTToHplusBHminusB_M160_Summer11": {
        "dataVersion": "42Xmc",
        "crossSection": 165,
        "data": {
            "AOD": {
                "datasetpath": "/TTToHplusBHminusB_M-160_7TeV-pythia6-tauola/Summer11-PU_S4_START42_V11-v1/AODSIM",
                "number_of_jobs": 20, # Adjusted for PATtuple file size
            },
            "pattuple_v13": {
                "dbs_url": common.pattuple_dbs,
                "datasetpath": "/TTToHplusBHminusB_M-160_7TeV-pythia6-tauola/local-Summer11_PU_S4_START42_V11_v1_AODSIM_pattuple_v13-f4fa5e38ef8e2164af1f351b44ad93c5/USER",
                "number_of_jobs": 1
            },
        }
    },

    # QCD backgrounds
    # Cross sections are from https://twiki.cern.ch/twiki/bin/view/CMS/ReProcessingSummer2011
    "QCD_Pt15to30_TuneZ2_Summer11": {
        "dataVersion": "42Xmc",
        "crossSection": 8.159e+08,
        "data": {
           "AOD": {
               "datasetpath": "/QCD_Pt-15to30_TuneZ2_7TeV_pythia6/Summer11-PU_S3_START42_V11-v2/AODSIM",
               "number_of_jobs": 490, # Adjusted for PATtuple file size
           },
        },
    },
    "QCD_Pt30to50_TuneZ2_Summer11": {
        "dataVersion": "42Xmc",
        "crossSection": 5.312e+07,
        "data": {
           "AOD": {
               "datasetpath": "/QCD_Pt-30to50_TuneZ2_7TeV_pythia6/Summer11-PU_S3_START42_V11-v2/AODSIM",
               "number_of_jobs": 200, # Adjusted for PATtuple file size
           },
           "pattuple_v13_test1": {
                "dbs_url": common.pattuple_dbs,
                "datasetpath": "/QCD_Pt-30to50_TuneZ2_7TeV_pythia6/local-Summer11_PU_S3_START42_V11_v2_AODSIM_pattuple_v13_test1-f4fa5e38ef8e2164af1f351b44ad93c5/USER",
                "number_of_jobs": 6
            },
        },
    },
    "QCD_Pt50to80_TuneZ2_Summer11": {
        "dataVersion":  "42Xmc",
        "crossSection": 6.359e+06,
        "data": {
           "AOD": {
               "datasetpath": "/QCD_Pt-50to80_TuneZ2_7TeV_pythia6/Summer11-PU_S3_START42_V11-v2/AODSIM",
               "number_of_jobs": 200, # Adjusted for PATtuple file size
           },
        },
    },
    "QCD_Pt80to120_TuneZ2_Summer11": {
        "dataVersion": "42Xmc",
        "crossSection": 7.843e+05,
        "data": {
           "AOD": {
               "datasetpath": "/QCD_Pt-80to120_TuneZ2_7TeV_pythia6/Summer11-PU_S3_START42_V11-v2/AODSIM",
               "number_of_jobs": 250, # Adjusted for PATtuple file size
           },
        },
    },
    "QCD_Pt120to170_TuneZ2_Summer11": {
        "dataVersion": "42Xmc",
        "crossSection": 1.151e+05,
        "data": {
            "AOD": {
                "datasetpath": "/QCD_Pt-120to170_TuneZ2_7TeV_pythia6/Summer11-PU_S3_START42_V11-v2/AODSIM",
                "number_of_jobs": 250, # Adjusted for PATtuple file size
            },
        },
    },
    "QCD_Pt170to300_TuneZ2_Summer11": {
        "dataVersion": "42Xmc",
        "crossSection": 2.426e+04,
        "data": {
            "AOD": {
                "datasetpath": "/QCD_Pt-170to300_TuneZ2_7TeV_pythia6/Summer11-PU_S3_START42_V11-v2/AODSIM",
                "number_of_jobs": 250, # Adjusted for PATtuple file size
            },
        },
    },
    "QCD_Pt300to470_TuneZ2_Summer11": {
        "dataVersion": "42Xredigi",
        "crossSection": 1.168e+03,
        "data": {
            "AOD": {
                "datasetpath": "/QCD_Pt-300to470_TuneZ2_7TeV_pythia6/Summer11-PU_S3_START42_V11-v2/AODSIM",
                "number_of_jobs": 250 # Adjusted for PATtuple file size
            },
        }
    },
    "QCD_Pt20_MuEnriched_TuneZ2_Summer11": {
        "dataVersion": "42Xredigi",
        "crossSection": 296600000.*0.0002855,
        "data": {
            "AOD": {
                "datasetpath": "/QCD_Pt-20_MuEnrichedPt-15_TuneZ2_7TeV-pythia6/Summer11-PU_S4_START42_V11-v1/AODSIM",
                "number_of_jobs": 200,  # Adjusted for PAT on the fly (NOT for PATtuple processing)
            }
        },
    },
    

    # EWK pythia
    # Cross sections (not yet) from https://twiki.cern.ch/twiki/bin/view/CMS/CrossSections_3XSeries
    "TT_TuneZ2_Summer11": {
        "dataVersion": "42Xmc",
        "crossSection": 165,
        "data": {
            "AOD": {
                "datasetpath": "/TT_TuneZ2_7TeV-pythia6-tauola/Summer11-PU_S3_START42_V11-v2/AODSIM",
                "number_of_jobs": 80, # Adjusted for PATtuple file size
            },
            "pattuple_v13_test1": {
                "dbs_url": common.pattuple_dbs,
                "datasetpath": "/TT_TuneZ2_7TeV-pythia6-tauola/local-Summer11_PU_S3_START42_V11_v2_AODSIM_pattuple_v13_test1-f4fa5e38ef8e2164af1f351b44ad93c5/USER",
                "number_of_jobs": 1
            },
        },
    },
    "WToTauNu_Z2_Summer11": {
        "dataVersion": "42Xmc",
        "crossSection": 7899,
        "data": {
            "AOD": {
                "datasetpath": "/WToTauNu_TuneZ2_7TeV-pythia6-tauola/Summer11-PU_S3_START42_V11-v2/AODSIM",
                "number_of_jobs": 370, # Adjusted for PATtuple file size
            },
        },
    },
    "WToMuNu_Z2_Summer11": {
        "dataVersion": "42Xmc",
        "crossSection": 7899,
        "data": {
            "AOD": {
                "datasetpath": "/WToMuNu_TuneZ2_7TeV-pythia6/Summer11-PU_S3_START42_V11-v2/AODSIM",
                "number_of_jobs": 370, # Adjusted for PATtuple file size
            },
        },
    },
}
