#!/usr/bin/python

from ROOT import *

def generateEfficiencyHist(varList):
    gStyle.SetOptStat(0);
    legend = TLegend(0.70,0.5,0.95,0.8);

    # Create descriptive strings
    descrWspaces = " - " + varList[5][1] + ", "
    descrWOspaces = "_"+varList[5][1] + "_"
    canvasTitle = "Efficiency vs. " + varList[0] + descrWspaces + varList[6][1]
    stackTitle = "Efficiency vs. " + varList[0] + descrWspaces + varList[6][1]

    c1 = TCanvas('c1', canvasTitle, 200, 10, 700, 500)
    histStack = THStack("histStack", stackTitle)
    tmpHist = TH1D("tmpHist", "", varList[1], varList[2], varList[3])
    ntuple.Project("tmpHist", varList[4], varList[6][0])

    # Create cut strings
    cutStrings = []
    for effCutDict in varList[7]:
        descr = effCutDict[1]
        cut = effCutDict[0] + " && " + varList[5][0] + " && " + varList[6][0]
        cutStrings.append([descr, cut, effCutDict[2]])
    if len(varList[7]) == 0:
        cutStrings.append([varList[5][1], varList[5][0] + " && " + varList[6][0], 0])
        filenameMod = ""
    else:
        filenameMod = "stack_"

    filename = "plots/hist_eff_"+ filenameMod +varList[0] + descrWOspaces + varList[6][1]+".pdf"

    for cutString in cutStrings:
        efficiencyHist = TH1D("effHist", cutString[0], varList[1], varList[2], varList[3])
        ntuple.Project("effHist", varList[4], cutString[1])
        efficiencyHist.Divide(tmpHist)
        efficiencyHist.SetFillColor(cutString[2])
        histStack.Add(efficiencyHist)
        legend.AddEntry(efficiencyHist, cutString[0], "F")
    histStack.Draw()
    if len(varList[7]) > 0:
        legend.Draw("")
    c1.Update()
    c1.Print(filename, "pdf")
    
def generate2DEfficiencyHist(varList):
    gStyle.SetOptStat(0)
    c1 = TCanvas('c1', "Efficiency vs. " + varList[0] + " - " + varList[8][1] + ", " + varList[9][1], 200, 10, 700, 500)
    tmpHist = TH2D("tmpHist", "", varList[1], varList[2], varList[3], varList[4], varList[5], varList[6])
    efficiencyHist = TH1D("effHist", "Efficiency vs. " + varList[0] + " - " + varList[8][1] + ", " + varList[9][1], varList[1], varList[2], varList[3], varList[4], varList[5], varList[6])
    ntuple.Project("tmpHist", varList[7], varList[9][0])
    ntuple.Project("effHist", varList[7], varList[9][0] + " && " + varList[8][0])
    efficiencyHist.Divide(tmpHist)
    efficiencyHist.DrawCopy()
    c1.Update()
    c1.Print("plots/hist2D_eff_"+varList[0]+"_"+varList[8][1] + "_" + varList[9][1]+".pdf", "pdf")

def generateRateHist(varList):
    gStyle.SetOptStat(110011);
    c1 = TCanvas('c1', "Rate of " + varList[0] + " - " + varList[5][1], 200, 10, 700, 500)
    rateHist = TH1D("rateHist", "Rate of " + varList[0] + " - " + varList[5][1], varList[1], varList[2], varList[3])
    ntuple.Project("rateHist", varList[4], varList[5][0])
    rateHist.DrawCopy()
    c1.Update()
    c1.Print("plots/hist_rate_"+varList[0]+"_"+varList[5][1]+".pdf", "pdf")

# etaScalePos= [0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.75,1.8,1.85,1.9,1.95,2.,2.05,2.1,2.15,2.2,2.25,2.3,2.35,2.4];
# etaScale= [None] * 63
# for i in range(31):
#     etaScale[i]    = -etaScalePos[31-i]
#     etaScale[32+i] = etaScalePos[i+1]
# etaScale[31]=0;

recoPt1 = "((pT1_reco>1) && (pT2_reco>1))"
gmtPt1 = "((pT1_GMT>1) && (pT2_GMT>1))"
recoPt5 = "((pT1_reco>5) && (pT2_reco>5))"
gmtPt5 = "((pT1_GMT>5) && (pT2_GMT>5))"
bothDTRPC = "(SubsysID_GMT == 0)"
bothDTRPC1 = "(SubsysID1_GMT == 0)"
bothDTRPC2 = "(SubsysID2_GMT == 0)"
bothCSCRPC = "(SubsysID_GMT == 1)"
bothCSCRPC1 = "(SubsysID1_GMT == 1)"
bothCSCRPC2 = "(SubsysID2_GMT == 1)"
onlyDT = "(SubsysID_GMT == 2)"
onlyDT1 = "(SubsysID1_GMT == 2)"
onlyDT2 = "(SubsysID2_GMT == 2)"
onlyCSC = "(SubsysID_GMT == 3)"
onlyCSC1 = "(SubsysID1_GMT == 3)"
onlyCSC2 = "(SubsysID2_GMT == 3)"
onlyRPC = "((SubsysID_GMT == 4) || (SubsysID_GMT == 5))"
onlyRPC1 = "((SubsysID1_GMT == 4) || (SubsysID1_GMT == 5))"
onlyRPC2 = "((SubsysID2_GMT == 4) || (SubsysID2_GMT == 5))"
correctCharges = "(Ch1_GMT == Ch1_reco) && (Ch2_GMT == Ch2_reco)"
usableCharges = "(((Ch1_GMT == Ch1_reco) && (Ch2_GMT == Ch2_reco)) || ((Ch1_GMT != Ch1_reco) && (Ch2_GMT != Ch2_reco)))"

cutDict = {}
cutDict["recoPt1"] = [recoPt1, "DiRecoMu1"]
cutDict["gmtPt1"] = [gmtPt1, "DiGMTMu1"]
cutDict["recoPt5"] = [recoPt5, "DiRecoMu5"]
cutDict["gmtPt5"] = [gmtPt5, "DiGMTMu5"]
cutDict["gmtPt1_cs"] = ["(" + gmtPt1 + " && " + correctCharges + ")", "DiGMTMu1_CorrectSign"]
cutDict["gmtPt1_us"] = ["(" + gmtPt1 + " && " + usableCharges + ")", "DiGMTMu1_UsableSign"]
cutDict["gmtPt5_cs"] = ["(" + gmtPt5 + " && " + correctCharges + ")", "DiGMTMu5_CorrectSign"]
cutDict["gmtPt5_us"] = ["(" + gmtPt5 + " && " + usableCharges + ")", "DiGMTMu5_UsableSign"]

cutDict["DTRPC"] = [bothDTRPC1, "DT+RPC", 8]
cutDict["DTRPC1"] = [bothDTRPC1, "DT+RPC", 8]
cutDict["DTRPC2"] = [bothDTRPC2, "DT+RPC", 8]
cutDict["CSCRPC"] = [bothCSCRPC1, "CSC+RPC", 9]
cutDict["CSCRPC1"] = [bothCSCRPC1, "CSC+RPC", 9]
cutDict["CSCRPC2"] = [bothCSCRPC2, "CSC+RPC", 9]
cutDict["DT"] = [onlyDT1, "DT", 30]
cutDict["DT1"] = [onlyDT1, "DT", 30]
cutDict["DT2"] = [onlyDT2, "DT", 30]
cutDict["CSC"] = [onlyCSC1, "CSC", 40]
cutDict["CSC1"] = [onlyCSC1, "CSC", 40]
cutDict["CSC2"] = [onlyCSC2, "CSC", 40]
cutDict["RPC"] = [onlyRPC1, "RPC", 46]
cutDict["RPC1"] = [onlyRPC1, "RPC", 46]
cutDict["RPC2"] = [onlyRPC2, "RPC", 46]

stackCutDict = {}
stackCutDict["subsystems_mu"] = [cutDict["DTRPC"], cutDict["CSCRPC"], cutDict["DT"], cutDict["CSC"], cutDict["RPC"]]
stackCutDict["subsystems_mu1"] = [cutDict["DTRPC1"], cutDict["CSCRPC1"], cutDict["DT1"], cutDict["CSC1"], cutDict["RPC1"]]
stackCutDict["subsystems_mu2"] = [cutDict["DTRPC2"], cutDict["CSCRPC2"], cutDict["DT2"], cutDict["CSC2"], cutDict["RPC2"]]
