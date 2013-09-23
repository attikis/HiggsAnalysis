#! /usr/bin/env python

import sys
import os

from HiggsAnalysis.HeavyChHiggsToTauNu.tools.aux import sort

# data structures for the config file information

class ObservationInput:
    def __init__(self, datasetDefinition, shapeHisto):
        self.datasetDefinition = datasetDefinition
        self.shapeHisto = shapeHisto

    def getShapeHisto(self):
        return self.shapeHisto

    def Print(self):
	print "ObservationInput :"
	print "    shapeHisto  ",self.shapeHisto

class DataGroup:
    def __init__(self, 
                 landsProcess = -999,
                 validMassPoints = [],
                 label = "", 
                 nuisances = [], 
                 shapeHisto = "", 
                 datasetType = "",
                 datasetDefinition = None,
                 QCDfactorisedInfo = None,
                 additionalNormalisation = 1.0):
	self.landsProcess  = landsProcess
	self.validMassPoints = validMassPoints
	self.label         = label
	self.nuisances     = nuisances
	self.shapeHisto    = shapeHisto
        self.datasetType   = datasetType
        self.datasetDefinition = datasetDefinition
        self.QCDfactorisedInfo = QCDfactorisedInfo
        self.additionalNormalisation = additionalNormalisation

    def getId(self):
	return self.label

    def clone(self):
	return DataGroup(landsProcess = self.landsProcess,
                         validMassPoints = self.validMassPoints,
                         label        = self.label,
                         nuisances    = self.nuisances,
                         shapeHisto   = self.shapeHisto,
                         datasetType  = self.datasetType,
                         datasetDefinition = self.datasetDefinition,
                         QCDfactorisedInfo = self.QCDfactorisedInfo,
                         additionalNormalisation= self.additionalNormalisation)

    def setLandSProcess(self,landsProcess):
	self.landsProcess = landsProcess

    def setValidMassPoints(self,validMassPoints):
	self.validMassPoints = list(validMassPoints)

    def setLabel(self, label):
	self.label = label

    def setNuisances(self,nuisances):
	self.nuisances = nuisances[:]

    def setShapeHisto(self,histo):
	self.shapeHisto = histo

    def setDatasetType(self,datasetType):
        self.datasetType = datasetType

    def setDatasetDefinition(self,datasetDefinition):
        self.datasetDefinition = datasetDefinition

    def setQCDfactorisedInfo(self,QCDfactorisedInfo):
        self.QCDfactorisedInfo = QCDfactorisedInfo

    def setAdditionalNormalisation(self,value):
	self.additionaNormalisation = value

    def Print(self):
	print "    Label        ",self.label
	print "    LandS process",self.landsProcess
	print "    Valid mass points",self.validMassPoints
	print "    datasetType  ",self.datasetType
	print "    datasetDefinition",self.datasetDefinition
	print "    Additional normalisation",self.additionalNormalisation
	print "    Nuisances    ",self.nuisances
        print

#class DataGroupInput:
#    def __init__(self):
#	self.datagroups = {}
#
#    def add(self,datagroup):
#	if datagroup.exists():
#	    self.datagroups[datagroup.getId()] = datagroup
#
#    def get(self,key):
#	return self.datagroups[key]
#
#    def Print(self):
#	print "DataGroups"
#        print "NuisanceTable"
#        for key in sorted(self.datagroups.keys()):
#            self.datagroups[key].Print()
#        print


class Nuisance:
    def __init__(self,
		id="",
		label="",
		distr="",
		function = "",
		**kwargs):
	self.setId(id)
	self.setLabel(label)
	self.setDistribution(distr)
	self.setFunction(function)
	self.kwargs = kwargs

    def setId(self,id):
	self.id = id

    def setLabel(self,label):
	self.label = label

    def setDistribution(self,distr):
	self.distr = distr

    def setFunction(self, function):
	self.function = function

    def getArg(self, keyword):
        if keyword in self.kwargs.keys():
            return self.kwargs[keyword]
        return None
	
    def getId(self):
	return self.id

    def Print(self):
	print "    ID            =",self.id
	print "    Label         =",self.label
        print "    Distribution  =",self.distr
        print "    Function      =",self.function
        #if self.value > 0:
            #print "    Value         =",self.value
        #if len(self.counter) > 0:
            #print "    Counter       =",self.counter
        #if len(self.paths) > 0:
            #print "    Paths         =",self.paths
        #if len(self.histo) > 0:
            #print "    Histograms    =",self.histo
        #if len(self.norm) > 0:
            #print "    Normalisation =",self.norm
	print

#class NuisanceTable:
    #def __init__(self):
	#self.nuisances = {}

    #def add(self,n):
	#if not self.exists(n):
	    #self.nuisances[n.getId()] = n
	#else:
	    #print "\nWarning, key",n.getId(),"already reserved to Nuisance"
	    #self.nuisances[n.getId()].Print()
	    #print "Exiting.."
	    #sys.exit()

    #def get(self,key):
        #return self.nuisances[key]

    #def merge(self,n1,n2):
	#print "merging nuisances is not yet implemented"

    #def reserve(self, ids, comment):
	#for id in ids:
	    #self.add(Nuisance(id=id,label=comment,distr= "lnN",function="Constant",value=0,reserved=True))

    #def exists(self, n):
	#if n.getId() in self.nuisances:
	    #return True
	#return False

    #def Print(self):
	#print "NuisanceTable"
	#for key in sort(self.nuisances.keys()):
	    #self.nuisances[key].Print()
	#print

class ControlPlotInput:
    def __init__(self,
                 title,
                 signalHHid,
                 signalHWid,
                 QCDid,
                 embeddingId,
                 EWKfakeId,
                 signalHistoPath,
                 signalHistoName,
                 EWKfakeHistoPath,
                 EWKfakeHistoName,
                 QCDFactNormalisation,
                 QCDFactHistoName,
                 details,
                 blindedRange,
                 evaluationRange,
                 flowPlotCaption):
        self.title = title
        self.signalHHid = signalHHid
        self.signalHWid = signalHWid
        self.QCDid = QCDid
        self.embeddingId = embeddingId
        self.EWKfakeId = EWKfakeId
        self.signalHistoPath = signalHistoPath
        self.signalHistoName = signalHistoName
        self.EWKfakeHistoPath = EWKfakeHistoPath
        self.EWKfakeHistoName = EWKfakeHistoName
        self.QCDFactNormalisation = QCDFactNormalisation
        self.QCDFactHistoName = QCDFactHistoName
        self.details = details
        self.blindedRange = blindedRange
        self.evaluationRange = evaluationRange
        self.flowPlotCaption = flowPlotCaption
