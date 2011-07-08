
files = {
    "Apr21ReReco": "Cert_136033-149442_7TeV_Apr21ReReco_Collisions10_JSON.txt",
    "May10ReReco": "Cert_160404-163869_7TeV_May10ReReco_Collisions11_JSON.txt",
    "PromptReco": "Cert_160404-167784_7TeV_PromptReco_Collisions11_JSON.txt",
    "May10ReRecoWedDiff": "Cert_160404-163869_7TeV_May10ReReco_Collisions11_JSON_diff_v2.txt",
    "PromptRecoWedDiff": "Cert_160404-167784_7TeV_PromptReco_Collisions11_JSON_diff_167913.txt",
}

def getFile(name):
    try:
        return files[name]
    except KeyError:
        raise Exception("No key '%s' for certified lumi file" % name)

if __name__ == "__main__":
    print "Lumi files"
    for name,fname in files.iteritems():
        print "%s: %s" % (name, fname)
