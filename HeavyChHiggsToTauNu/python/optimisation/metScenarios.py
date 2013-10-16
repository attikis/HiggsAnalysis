from HiggsAnalysis.HeavyChHiggsToTauNu.OptimisationScheme import HPlusOptimisationScheme, Scenario

# There must be 'optimisation' object
optimisation = HPlusOptimisationScheme()

_pt = [50,60,70,80,90]

for pt in _pt:
    optimisation.addMETSelectionVariation(pt)