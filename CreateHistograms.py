#!/usr/bin/python

from ROOT import *

## varlist entries:
# 0: descriptive string used for caption and filename (what is plotted)
# 1: binning
# 2: variables to plot
# 3: physical cuts on GMT muons
# 4: physical cuts on reco (and GMT) muons
# (optional) 5: Range of y-axis
def generateGhostPercHist(varList, ntuple_file, dataset=""):
    generateEffOrPercHist(varList, dataset, ["Probability for Ghosts", "ghost"], ntuple_file)

## varlist entries:
# 0: descriptive string used for caption and filename (what is plotted)
# 1: binning
# 2: variables to plot
# 3: physical cuts on GMT muons
# 4: physical cuts on reco (and GMT) muons
# (optional) 5: Range of y-axis
def generateEfficiencyHist(varList, ntuple_file, dataset=""):
    generateEffOrPercHist(varList, ["Efficiency", "eff"], ntuple_file, dataset=dataset)

def generateEffOrPercHist(varList, typeStrings, ntuple_file, ntupleMC_file="", dataset="", datasetMC=""):
    if len(varList) < 6:
        minYAxis = 0
        maxYAxis = 1
    else:
        minYAxis = varList[5][0]
        maxYAxis = varList[5][1]

    gStyle.SetOptStat(0)

    # Get ntuple
    f = TFile.Open(ntuple_file)
    ntuple = f.Get("ntuple")

    # Create descriptive strings
    descrWspaces = " - " + varList[3][1] + ", "
    descrWOspaces = "_"+varList[3][1] + "_"
    canvasTitle = typeStrings[0] + " vs. " + varList[0] + descrWspaces + varList[4][1]
    histTitle = typeStrings[0] + " vs. " + varList[0] + descrWspaces + varList[4][1]

    # Create cut string
    cutString = [varList[3][1], varList[3][0] + " && " + varList[4][0]]

    c1 = TCanvas('c1', canvasTitle, 200, 10, 700, 500)
    tmpHist = TH1D("tmpHist", "", varList[1][0], varList[1][1], varList[1][2])
    passHist = TH1D("passHist", cutString[0], varList[1][0], varList[1][1], varList[1][2])
    tmpHist.Sumw2()
    ntuple.Project("tmpHist", varList[2], varList[4][0])
    ntuple.Project("passHist", varList[2], cutString[1])

    finGraph = TGraphAsymmErrors()
    finHist = TH1D("finHist", histTitle, varList[1][0], varList[1][1], varList[1][2])
    finHist.Divide(passHist, tmpHist, 1.0, 1.0)
    finHist.SetMinimum(minYAxis)
    finHist.SetMaximum(maxYAxis)
    finGraph.Divide(passHist, tmpHist)
    finHist.GetXaxis().SetTitle(varList[0])
    finHist.GetYaxis().SetTitle(typeStrings[0])
    finHist.Draw("hist")
    # passHist.Draw("E1,SAME")
    finGraph.SetLineColor(38)
    finGraph.SetMarkerColor(38)
    finGraph.Draw("p,SAME")
    finHist.Draw("hist,SAME")    # Drawn again to cover horizontal error bars.

    if ntupleMC_file != "":
        # Get ntuple
        f = TFile.Open(ntupleMC_file)
        ntuple = f.Get("ntuple")
        tmpHistMC = TH1D("tmpHistMC", "", varList[1][0], varList[1][1], varList[1][2])
        passHistMC = TH1D("passHistMC", cutString[0], varList[1][0], varList[1][1], varList[1][2])
        tmpHistMC.Sumw2()
        ntuple.Project("tmpHistMC", varList[2], varList[4][0])
        ntuple.Project("passHistMC", varList[2], cutString[1])

        finGraphMC = TGraphAsymmErrors()
        finHistMC = TH1D("finHistMC", histTitle, varList[1][0], varList[1][1], varList[1][2])
        finHistMC.Divide(passHistMC, tmpHistMC, 1.0, 1.0)
        finHistMC.SetMinimum(minYAxis)
        finHistMC.SetMaximum(maxYAxis)
        finGraphMC.Divide(passHistMC, tmpHistMC)
        finHistMC.SetLineColor(kRed)
        # finHistMC.Draw("HistMC, SAME")
        # passHistMC.Draw("E1,SAME")
        finGraphMC.SetLineColor(46)
        finGraphMC.SetMarkerColor(46)
        finGraphMC.Draw("p,SAME")
        finHistMC.Draw("hist,SAME")    # Drawn again to cover horizontal error bars.

        legend = TLegend(0.55,0.1,0.9,0.2)
        # legend.SetFillStyle(kWhite)
        legend.AddEntry(finHist, dataset, "L")
        legend.AddEntry(finHistMC, datasetMC, "L")
        legend.Draw()

        combString = "combined_"
    else:
        combString = ""

    c1.Update()

    if (dataset != "") and (dataset != "Data"):
        dataset += "_"

    if (datasetMC != "") and (datasetMC != "MC"):
        datasetMC += "_"
    filename = "plots/hist_" + combString + typeStrings[1] + "_" + dataset + datasetMC + varList[0] +\
        descrWOspaces + varList[4][1] + ".pdf"

    c1.Print(filename, "pdf")

## varlist entries:
# 0: descriptive string used for caption and filename (what is plotted)
# 1: binning
# 2: variables to plot
# 3: physical cuts on GMT muons
# 4: physical cuts on reco (and GMT) muons
# 5: list of 'cuts' for each component of stack
# (optional) 6: Range of y-axis
def generateEfficiencyStack(varList, ntuple_file, dataset=""):
    if len(varList) < 7:
        minYAxis = 0
        maxYAxis = 1
    else:
        minYAxis = varList[6][0]
        maxYAxis = varList[6][1]

    gStyle.SetOptStat(0)
    legend = TLegend(0.85,0.70,0.99,0.99)

    # Get ntuple
    f = TFile.Open(ntuple_file)
    ntuple = f.Get("ntuple")

    # Create descriptive strings
    descrWspaces = " - " + varList[3][1] + ", "
    descrWOspaces = "_"+varList[3][1] + "_"
    canvasTitle = "Efficiency vs. " + varList[0] + descrWspaces + varList[4][1]
    stackTitle = "Efficiency vs. " + varList[0] + descrWspaces + varList[4][1]

    c1 = TCanvas('c1', canvasTitle, 200, 10, 700, 500)
    histStack = THStack("histStack", stackTitle + ";" + varList[0] + ";Efficiency")
    tmpHist = TH1D("tmpHist", "", varList[1][0], varList[1][1], varList[1][2])
    ntuple.Project("tmpHist", varList[2], varList[4][0])

    # Create cut strings
    cutStrings = []
    for compCutDict in varList[5]:
        descr = compCutDict[1]
        cut = compCutDict[0] + " && " + varList[3][0] + " && " + varList[4][0]
        cutStrings.append([descr, cut, compCutDict[2]])

    if dataset != "":
        dataset += "_"
    filename = "plots/hist_eff_" + dataset + "stack_" + varList[0] + descrWOspaces + varList[4][1] + ".pdf"

    for cutString in cutStrings:
        efficiencyHist = TH1D("effHist", cutString[0], varList[1][0], varList[1][1], varList[1][2])
        ntuple.Project("effHist", varList[2], cutString[1])
        efficiencyHist.Divide(tmpHist)
        efficiencyHist.SetFillColor(cutString[2])
        histStack.Add(efficiencyHist)
        legend.AddEntry(efficiencyHist, cutString[0], "F")
    histStack.SetMinimum(minYAxis)
    histStack.SetMaximum(maxYAxis)
    histStack.Draw()
    legend.Draw("")
    c1.Update()
    c1.Print(filename, "pdf")

## varlist entries:
# 0: descriptive string used for caption and filename (what is plotted)
# 1: binning
# 2: variables to plot
# 3: physical cuts
def generateCombinedRateHist(varList, ntuple_file, ntupleMC_file, dataset = "", datasetMC = ""):
    if ntupleMC_file == "":
        gStyle.SetOptStat(110011)
    else:
        gStyle.SetOptStat(0)

    # Get ntuple
    f = TFile.Open(ntuple_file)
    ntuple = f.Get("ntuple")

    c1 = TCanvas('c1', "Distribution of " + varList[0] + " - " + varList[3][1], 200, 10, 700, 500)
    rateHist = TH1D("rateHist", "Distribution of " + varList[0] + " - " + varList[3][1], varList[1][0], varList[1][1], varList[1][2])
    ntuple.Project("rateHist", varList[2], varList[3][0])
    rateHist.GetXaxis().SetTitle(varList[0])
    rateHist.Draw("hist")

    if ntupleMC_file != "":
        # Get ntuple
        fMC = TFile.Open(ntupleMC_file)
        ntuple = fMC.Get("ntuple")

        rateHistMC = TH1D("rateHistMC", "Distribution of " + varList[0] + " - " + varList[3][1], varList[1][0], varList[1][1], varList[1][2])
        ntuple.Project("rateHistMC", varList[2], varList[3][0])
        rateHistMC.GetXaxis().SetTitle(varList[0])
        rateHistMC.SetLineColor(kRed)
        rateHistMC.Draw("hist,SAME")

        legend = TLegend(0.55,0.8,0.9,0.9)
        legend.SetFillStyle(0)
        legend.AddEntry(rateHist, dataset, "L")
        legend.AddEntry(rateHistMC, datasetMC, "L")
        legend.Draw("")

        combString = "combined_"
    else:
        combString = ""

    c1.Update()
    if dataset != "":
        dataset += "_"
    if datasetMC != "":
        datasetMC += "_"
    filename = "plots/hist_dist_" + combString + dataset + datasetMC + varList[0] + "_" + varList[3][1] + ".pdf"
    c1.Print(filename, "pdf")

## varlist entries:
# 0: descriptive string used for caption and filename (what is plotted)
# 1: binning
# 2: variables to plot
# 3: physical cuts
# 4: list of 'cuts' for each component of stack (optional, used for subsystem separation)
def generateRateStack(varList, ntuple_file, dataset = ""):
    gStyle.SetOptStat(110011);
    legend = TLegend(0.85,0.70,0.99,0.99);

    # Get ntuple
    f = TFile.Open(ntuple_file)
    ntuple = f.Get("ntuple")

    # Create descriptive strings
    descrWspaces = " - " + varList[3][1]
    descrWOspaces = "_"+varList[3][1]
    title = "Distribution of " + varList[0] + descrWspaces

    c1 = TCanvas('c1', title, 200, 10, 700, 500)
    histStack = THStack("histStack", title + ";" + varList[0] + ";Events")

    # Create cut strings
    cutStrings = []
    for compCutDict in varList[4]:
        descr = compCutDict[1]
        cut = compCutDict[0] + " && " + varList[3][0]
        cutStrings.append([descr, cut, compCutDict[2]])

    if dataset != "":
        dataset += "_"
    filename = "plots/hist_dist_" + dataset + "stack_" + varList[0] + descrWOspaces + ".pdf"

    for cutString in cutStrings:
        rateHist = TH1D("rateHist", cutString[0], varList[1][0], varList[1][1], varList[1][2])
        ntuple.Project("rateHist", varList[2], cutString[1])
        rateHist.SetFillColor(cutString[2])
        histStack.Add(rateHist)
        legend.AddEntry(rateHist, cutString[0], "F")
    histStack.Draw()
    legend.Draw("")
    c1.Update()
    c1.Print(filename, "pdf")

## varlist entries:
# 0: descriptive string used for caption and filename (what is plotted)
# 1: Binning for first variable
# 2: Binning for second variable
# 3: Variables to plot (in the form x2:x1) (!)
# 4: physical cuts on GMT muons
# 5: physical cuts on reco (and GMT) muons
def generate2DEfficiencyHist(varList, ntuple_file, dataset = ""):
    gStyle.SetOptStat(0)

    # Get ntuple
    f = TFile.Open(ntuple_file)
    ntuple = f.Get("ntuple")

    descrWspaces = " - " + varList[4][1] + ", "
    descrWOspaces = "_"+varList[4][1] + "_"
    c1 = TCanvas('c1', "Efficiency vs. " + varList[0] + descrWspaces + varList[5][1], 200, 10, 700, 500)
    tmpHist = TH2D("tmpHist", "", varList[1][0], varList[1][1], varList[1][2], varList[2][0], varList[2][1], varList[2][2])
    efficiencyHist = TH2D("effHist", varList[0] + descrWspaces + varList[5][1], varList[1][0], varList[1][1], varList[1][2], varList[2][0], varList[2][1], varList[2][2])
    ntuple.Project("tmpHist", varList[3], varList[5][0])
    ntuple.Project("effHist", varList[3], varList[4][0] + " && " + varList[5][0])
    efficiencyHist.Divide(tmpHist)
    axLbl = varList[3].split(":")
    efficiencyHist.GetXaxis().SetTitle(axLbl[1])
    efficiencyHist.GetYaxis().SetTitle(axLbl[0])
    efficiencyHist.DrawCopy("COLZ")
    c1.Update()
    if dataset != "":
        dataset += "_"
    filename = "plots/hist2D_eff_" + dataset + varList[0] + descrWOspaces + varList[5][1] + ".pdf"
    c1.Print(filename, "pdf")

## varlist entries:
# 0: descriptive string used for caption and filename (what is plotted)
# 1: Binning for first variable
# 2: Binning for second variable
# 3: Variables to plot (in the form x1:x2)
# 4: physical cuts
def generate2DRateHist(varList, ntuple_file, dataset = ""):
    gStyle.SetOptStat(110011);

    # Get ntuple
    f = TFile.Open(ntuple_file)
    ntuple = f.Get("ntuple")

    c1 = TCanvas('c1', "Distribution of " + varList[0] + " - " + varList[4][1], 200, 10, 700, 500)
    rateHist = TH2D("rateHist", varList[0] + " - " + varList[4][1], varList[1][0], varList[1][1], varList[1][2], varList[2][0], varList[2][1], varList[2][2])
    ntuple.Project("rateHist", varList[3], varList[4][0])
    axLbl = varList[3].split(":")
    rateHist.GetXaxis().SetTitle(axLbl[0])
    rateHist.GetYaxis().SetTitle(axLbl[1])
    rateHist.DrawCopy("COLZ")
    c1.Update()
    if dataset != "":
        dataset += "_"
    filename = "plots/hist2D_dist_" + dataset + varList[0] + "_" + varList[4][1] + ".pdf"
    c1.Print(filename, "pdf")

## varlist entries:
# 0: descriptive string used for caption and filename (what is plotted)
# 1: binning
# 2: variables to plot
# 3: physical cuts on GMT muons
# 4: physical cuts on reco (and GMT) muons
# (optional) 5: Range of y-axis
def generateCombinedGhostPercHist(varList, ntuple_file, ntupleMC_file, dataset=""):
    generateEffOrPercHist(varList, ["Probability for Ghosts vs. ", "ghost"], ntuple_file, ntupleMC_file, dataset, datasetMC)

## varlist entries:
# 0: descriptive string used for caption and filename (what is plotted)
# 1: binning
# 2: variables to plot
# 3: physical cuts on GMT muons
# 4: physical cuts on reco (and GMT) muons
# (optional) 5: Range of y-axis
def generateCombinedEfficiencyHist(varList, ntuple_file, ntupleMC_file, dataset="Data", datasetMC="MC"):
    generateEffOrPercHist(varList, ["Efficiency", "eff"], ntuple_file, ntupleMC_file, dataset, datasetMC)

## varlist entries:
# 0: descriptive string used for caption and filename (what is plotted)
# 1: binning
# 2: variables to plot
# 3: physical cuts
def generateRateHist(varList, ntuple_file, dataset = "Data", datasetMC = "MC"):
    generateCombinedRateHist(varList, ntuple_file, ntupleMC_file = "", dataset = "")

# etaScalePos= [0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.75,1.8,1.85,1.9,1.95,2.,2.05,2.1,2.15,2.2,2.25,2.3,2.35,2.4];
# etaScale= [None] * 63
# for i in range(31):
#     etaScale[i]    = -etaScalePos[31-i]
#     etaScale[32+i] = etaScalePos[i+1]
# etaScale[31]=0;

## Binning

binningDict                 = {}
binningDict["etaFine"]      = [100, -2.6, 2.6]
binningDict["phiFine"]      = [100, -3.2, 3.2]
binningDict["ptFine"]       = [100, 0, 200]
binningDict["pt50Fine"]     = [100, 0, 50]
binningDict["pt25Fine"]     = [100, 0, 25]
binningDict["invMassFine"]  = [80, 0, 20]
binningDict["distNarrow"]   = [50, 0, 0.4]
binningDict["distWide"]     = [50, 0, 2]
binningDict["distWideFine"] = [100, 0, 2]


## Cuts

mu1_recoPt1        = "(pT1_reco>1)"
mu1_gmtPt1         = "(pT1_GMT>1)"
mu1_recoPt5        = "(pT1_reco>5)"
mu1_gmtPt5         = "(pT1_GMT>5)"
jPsi_recoPt1       = "(pT_dimuon_reco>1)"
jPsi_gmtPt1        = "(pT_dimuon_GMT>1)"
jPsi_recoPt5       = "(pT_dimuon_reco>5)"
jPsi_gmtPt5        = "(pT_dimuon_GMT>5)"
diMu_recoPt1       = "((pT1_reco>1) && (pT2_reco>1))"
diMu_gmtPt1        = "((pT1_GMT>1) && (pT2_GMT>1))"
diMu_recoPt5       = "((pT1_reco>5) && (pT2_reco>5))"
diMu_gmtPt5        = "((pT1_GMT>5) && (pT2_GMT>5))"
bothDTRPC          = "(SubsysID_GMT == 0)"
bothDTRPC1         = "(SubsysID1_GMT == 0)"
bothDTRPC2         = "(SubsysID2_GMT == 0)"
bothCSCRPC         = "(SubsysID_GMT == 1)"
bothCSCRPC1        = "(SubsysID1_GMT == 1)"
bothCSCRPC2        = "(SubsysID2_GMT == 1)"
onlyDT             = "(SubsysID_GMT == 2)"
onlyDT1            = "(SubsysID1_GMT == 2)"
onlyDT2            = "(SubsysID2_GMT == 2)"
onlyCSC            = "(SubsysID_GMT == 3)"
onlyCSC1           = "(SubsysID1_GMT == 3)"
onlyCSC2           = "(SubsysID2_GMT == 3)"
onlyRPC            = "((SubsysID_GMT == 4) || (SubsysID_GMT == 5))"
onlyRPC1           = "((SubsysID1_GMT == 4) || (SubsysID1_GMT == 5))"
onlyRPC2           = "((SubsysID2_GMT == 4) || (SubsysID2_GMT == 5))"
correctCharges     = "(Ch1_GMT == Ch1_reco) && (Ch2_GMT == Ch2_reco)"
usableCharges      = "(((Ch1_GMT == Ch1_reco) && (Ch2_GMT == Ch2_reco)) || ((Ch1_GMT != Ch1_reco) && (Ch2_GMT != Ch2_reco)))"
diMu_barrelRegion  = "((abs(Eta1_reco) <= 0.8) && (abs(Eta2_reco) < 0.8))"
diMu_overlapRegion = "((abs(Eta1_reco) > 0.8) && (abs(Eta1_reco) < 1.3) && (abs(Eta2_reco) > 0.8) && (abs(Eta2_reco) < 1.3))"
diMu_forwardRegion = "((abs(Eta1_reco) => 1.3) && (abs(Eta2_reco) => 1.3))"

cutDict = {}
cutDict["recoPt1"]      = [mu1_recoPt1, "RecoMu1"]
cutDict["gmtPt1"]       = [mu1_gmtPt1, "GMTMu1"]
cutDict["recoPt5"]      = [mu1_recoPt5, "RecoMu5"]
cutDict["gmtPt5"]       = [mu1_gmtPt5, "GMTMu5"]
cutDict["jpsi-gmtPt1"]  = [jPsi_gmtPt1, "GMTJPsi1"]
cutDict["jpsi-gmtPt1_cs"]  = ["(" + jPsi_gmtPt1 + " && " + correctCharges + ")", "GMTJPsi1_CorrectSign"]
cutDict["jpsi-gmtPt1_us"]  = ["(" + jPsi_gmtPt1 + " && " + usableCharges + ")", "GMTJPsi1_UsableSign"]

cutDict["diMu-recoPt1"] = [diMu_recoPt1, "DiRecoMu1"]
cutDict["diMu-recoPt5"] = [diMu_recoPt5, "DiRecoMu5"]

cutDict["diMu-gmtPt1"]    = [diMu_gmtPt1, "DiGMTMu1"]
cutDict["diMu-gmtPt1_cs"] = ["(" + diMu_gmtPt1 + " && " + correctCharges + ")", "DiGMTMu1_CorrectSign"]
cutDict["diMu-gmtPt1_us"] = ["(" + diMu_gmtPt1 + " && " + usableCharges + ")", "DiGMTMu1_UsableSign"]

cutDict["diMu-gmtPt5"]    = [diMu_gmtPt5, "DiGMTMu5"]
cutDict["diMu-gmtPt5_cs"] = ["(" + diMu_gmtPt5 + " && " + correctCharges + ")", "DiGMTMu5_CorrectSign"]
cutDict["diMu-gmtPt5_us"] = ["(" + diMu_gmtPt5 + " && " + usableCharges + ")", "DiGMTMu5_UsableSign"]

cutDict["diMu-recoPt5-brl"] = ["(" + diMu_recoPt5 + " && " + diMu_barrelRegion + ")", "DiGMTMu5_BarrelRegion"]
cutDict["diMu-recoPt5-ovl"] = ["(" + diMu_recoPt5 + " && " + diMu_overlapRegion + ")", "DiGMTMu5_OverlapRegion"]
cutDict["diMu-recoPt5-fwd"] = ["(" + diMu_recoPt5 + " && " + diMu_forwardRegion + ")", "DiGMTMu5_ForwardRegion"]
cutDict["diMu-recoPt5-brl"] = ["(" + diMu_recoPt5 + " && " + diMu_barrelRegion + ")", "DiGMTMu5_BarrelRegion"]
cutDict["diMu-recoPt5-ovl"] = ["(" + diMu_recoPt5 + " && " + diMu_overlapRegion + ")", "DiGMTMu5_OverlapRegion"]
cutDict["diMu-recoPt5-fwd"] = ["(" + diMu_recoPt5 + " && " + diMu_forwardRegion + ")", "DiGMTMu5_ForwardRegion"]

# #TODO:0 Find better colours.
DTconfirmed  = kGreen + 3
DTonly       = kGreen - 10
CSCconfirmed = kBlue
CSConly      = kBlue - 10
RPC          = kOrange + 1

cutDict["DTRPC"]   = [bothDTRPC1, "DT+RPC", DTconfirmed]
cutDict["DTRPC1"]  = [bothDTRPC1, "DT+RPC", DTconfirmed]
cutDict["DTRPC2"]  = [bothDTRPC2, "DT+RPC", DTconfirmed]
cutDict["CSCRPC"]  = [bothCSCRPC1, "CSC+RPC", CSCconfirmed]
cutDict["CSCRPC1"] = [bothCSCRPC1, "CSC+RPC", CSCconfirmed]
cutDict["CSCRPC2"] = [bothCSCRPC2, "CSC+RPC", CSCconfirmed]
cutDict["DT"]      = [onlyDT1, "DT", DTonly]
cutDict["DT1"]     = [onlyDT1, "DT", DTonly]
cutDict["DT2"]     = [onlyDT2, "DT", DTonly]
cutDict["CSC"]     = [onlyCSC1, "CSC", CSConly]
cutDict["CSC1"]    = [onlyCSC1, "CSC", CSConly]
cutDict["CSC2"]    = [onlyCSC2, "CSC", CSConly]
cutDict["RPC"]     = [onlyRPC1, "RPC", RPC]
cutDict["RPC1"]    = [onlyRPC1, "RPC", RPC]
cutDict["RPC2"]    = [onlyRPC2, "RPC", RPC]

stackCutDict                   = {}
stackCutDict["subsystems_mu"]  = [cutDict["DTRPC"], cutDict["CSCRPC"], cutDict["DT"], cutDict["CSC"], cutDict["RPC"]]
stackCutDict["subsystems_mu1"] = [cutDict["DTRPC1"], cutDict["CSCRPC1"], cutDict["DT1"], cutDict["CSC1"], cutDict["RPC1"]]
stackCutDict["subsystems_mu2"] = [cutDict["DTRPC2"], cutDict["CSCRPC2"], cutDict["DT2"], cutDict["CSC2"], cutDict["RPC2"]]
