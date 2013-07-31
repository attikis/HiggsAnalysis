#! /usr/bin/env python

import ROOT
from HiggsAnalysis.HeavyChHiggsToTauNu.tools.codeValidator import *

#import HiggsAnalysis.HeavyChHiggsToTauNu.datacardtools.QCDfactorised as QCDfactorised

from HiggsAnalysis.HeavyChHiggsToTauNu.tools.ShellStyles import *

if __name__ == "__main__":
    ROOT.gROOT.SetBatch() # no flashing canvases
    print HighlightStyle()+"Validating code  ...\n"+NormalStyle()
    cv = CodeValidator()

    # Include here packages to validate
    from HiggsAnalysis.HeavyChHiggsToTauNu.tools.extendedCount import *
    validateExtendedCount(cv)
   
 #   from HiggsAnalysis.HeavyChHiggsToTauNu.datacardtools.UnfoldedHistogramReader import validateUnfoldedHistogramReader
 #   validateUnfoldedHistogramReader(cv)
    cv.finish()
