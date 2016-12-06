#!/usr/bin/python

import random
import string
import os
import CMS_lumi
import tdrstyle

from ROOT import *


def randomword(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))

# varlist entries:
# 0: descriptive string used for caption and filename (what is plotted)
# 1: binning
# 2: variables to plot
# 3: physical cuts on GMT muons in first ntuple
# 4: leave empty ("")
# 5: physical cuts on reco (and GMT) muons
# (optional) 6: Range of y-axis


def generateGhostPercHist(varList, ntuple_file, dataset=""):
    generateEffOrPercHist(varList, dataset,
                          ["Probability for Ghosts", "ghost"], ntuple_file)


# varlist entries:
# 0: descriptive string used for caption and filename (what is plotted)
# 1: binning
# 2: variables to plot
# 3: physical cuts on GMT muons in first ntuple
# 4: leave empty ("")
# 5: physical cuts on reco (and GMT) muons
# (optional) 6: Range of y-axis
def generateEfficiencyHist(varList, ntuple_file, dataset=""):
    generateEffOrPercHist(varList, ["Efficiency", "eff"], ntuple_file,
                          dataset=dataset)


def generateEffOrPercHist(varList, typeStrings, ntuple_files,
                          ntuple_names, labels, line_colours,
                          gmt_cuts, folder_name="", drawGenMus=True,
                          drawDistributions=False,
                          drawStackPlot=False, rootFolder="plots",
                          distLogy=False):
    #    gStyle.SetOptStat(0)
    tdrstyle.setTDRStyle()
    CMS_lumi.lumi_sqrtS = "13 TeV"
    iPeriod = 0

    if folder_name == "":
        folder = rootFolder + "/"
    else:
        folder = rootFolder + "/" + folder_name + "/"
    if not os.path.exists(folder + "pdf"):
        os.makedirs(folder + "pdf")
    if not os.path.exists(folder + "png"):
        os.makedirs(folder + "png")

    if len(varList) < 5:
        minYAxis = 0
        maxYAxis = 1
    else:
        minYAxis = varList[4][0]
        maxYAxis = varList[4][1]

    # Get ntuples
    ntuples = []
    unique_files = {}
    for ntuple_file, ntuple_name in zip(ntuple_files, ntuple_names):
        if ntuple_file in unique_files:
            ntuples.append(unique_files[ntuple_file].Get(ntuple_name))
        else:
            f = TFile.Open(ntuple_file)
            unique_files[ntuple_file] = f
            ntuples.append(f.Get(ntuple_name))

    # Create cut string and desciption
    cutStrings = []
    descStrings = set()
    for gmt_cut in gmt_cuts:
        cutStrings.append([gmt_cut[1], gmt_cut[0] + " && " + varList[3][0]])
        descStrings.add(gmt_cut[1])

    c = TCanvas("c", "", 525, 500)
    c.SetRightMargin(0.05)
    fin_legend = TLegend(0.17, 0.72, 0.9, 0.92)
    finHists = []
    finGraphs = []

    if drawStackPlot is True:
        hist_stack = THStack()
        hist_stack.SetMinimum(minYAxis)
        hist_stack.SetMaximum(maxYAxis)

    for ntuple, label, cutString, line_colour in zip(ntuples,
                                                     labels,
                                                     cutStrings,
                                                     line_colours):
        randomID = randomword(10)

        recoHist = TH1D("recoHist" + randomID, "", varList[1][0], varList[1][1],
                        varList[1][2])
        passHist = TH1D("passHist" + randomID, "", varList[1][0], varList[1][1],
                        varList[1][2])
        recoHist.Sumw2()
        passHist.Sumw2()
        ntuple.Project("recoHist" + randomID, varList[2], varList[3][0])
        ntuple.Project("passHist" + randomID, varList[2], cutString[1])
        # Make dist histogram
        c1 = TCanvas("c1", "", 525, 500)
        c1.SetRightMargin(0.05)
        if distLogy is True:
            recoHist.SetMinimum(0.00001)
            passHist.SetMinimum(0.00001)
            gPad.SetLogy()
        else:
            recoHist.SetMinimum(0)
            passHist.SetMinimum(0)
        recoHist.GetXaxis().SetTitle(varList[0][1])
        recoHist.GetYaxis().SetTitle("# of muons")
        passHist.GetXaxis().SetTitle(varList[0][1])
        passHist.GetYaxis().SetTitle("# of muons")

        legend = TLegend(0.17, 0.72, 0.9, 0.92)
        legend.SetBorderSize(0)
        legend.SetFillStyle(0)

        recoHist.SetLineColor(kRed)
        if drawGenMus is True:
            recoHist.Draw("E1HIST")
            legend.AddEntry(recoHist, label[0], "LP")
        passHist.SetLineColor(kBlue)
        passHist.Draw("E1HISTSAME")
        # legend.SetTextSize(0.0275)
        legend.AddEntry(passHist, label[1], "LP")

        legend.Draw("SAME")

        dist_filename_list = []
        dist_filename_list.append("dist")
        dist_filename_list.append(label[2])
        dist_filename_list.append(varList[0][0])
        dist_filename_list.append(cutString[0])
        dist_filename_list.append(varList[3][1])
        if len(label) > 3:
            dist_filename_list.append(label[3])
        dist_filename = '_'.join(dist_filename_list)
        if drawDistributions is True:
            c1.Print(folder + "png/" + dist_filename + ".png")
            c1.Print(folder + "pdf/" + dist_filename + ".pdf")

        c.cd()
        finGraph = TGraphAsymmErrors()
        finHist = TH1D("finHist" + randomID, "", varList[1][0], varList[1][1],
                       varList[1][2])
        finHist.Divide(passHist, recoHist, 1.0, 1.0)
        finGraph.Divide(passHist, recoHist)
        if (drawStackPlot is True) and (label[2] == "uGMT"):
            legend_marker = "F"
            finHist.SetFillColor(line_colour)
            finHist.SetLineColor(kBlack)
            hist_stack.Add(finHist)
        else:
            finHist.SetMinimum(minYAxis)
            finHist.SetMaximum(maxYAxis)
            finHist.GetXaxis().SetTitle(varList[0][1])
            finHist.GetYaxis().SetTitle(typeStrings[0])
            finHist.SetLineColor(line_colour)
            finHists.append(finHist)
            finGraph.SetLineColor(line_colour)
            finGraph.SetMarkerColor(line_colour)
            legend_marker = "LP"
            c.Update()
        finGraphs.append(finGraph)

        if len(ntuple_files) > 1:
            fin_legend.SetFillStyle(0)
            fin_legend.SetBorderSize(0)
            fin_legend.AddEntry(finHist, label[1], legend_marker)

    if drawStackPlot is True:
        hist_stack.Draw("hist")
        c.Update()
        hist_stack.GetXaxis().SetTitle(varList[0][1])
        hist_stack.GetYaxis().SetTitle(typeStrings[0])

    for finHist, finGraph in zip(finHists, finGraphs):
        finHist.Draw("hist,SAME")
        finGraph.Draw("p,SAME")
        # Drawn again to cover horizontal error bars
        finHist.Draw("hist,SAME")
        c.Update()

    if len(ntuple_files) > 1:
        fin_legend.Draw("SAME")
        c.Update()

    filename_list = []
    filename_list.append(typeStrings[1])
    filename_list.append(varList[0][0])
    filename_list.extend(descStrings)
    filename_list.append(varList[3][1])
    if len(ntuple_files) > 1:
        filename_list.append("comb")

    filename = '_'.join(filename_list)

    c.Print(folder + "pdf/" + filename + ".pdf")
    c.Print(folder + "png/" + filename + ".png")

    # Clean up.
    for name, f in unique_files.iteritems():
        f.Close()


# varlist entries:
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
    legend = TLegend(0.85, 0.70, 0.99, 0.99)

    # Get ntuple
    f = TFile.Open(ntuple_file)
    ntuple = f.Get("ntuple")

    # Create descriptive strings
    descrWspaces = " - " + varList[3][1] + ", "
    descrWOspaces = "_" + varList[3][1] + "_"
    canvasTitle = ""
    stackTitle = ""

    c1 = TCanvas('c1', canvasTitle, 200, 10, 700, 500)
    histStack = THStack("histStack", "")
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

    filename_pdf = "plots/eff_" + dataset + "stack_" + varList[0][0] +\
        descrWOspaces + varList[4][1] + ".pdf"
    filename_png = "plots/eff_" + dataset + "stack_" + varList[0][0] +\
        descrWOspaces + varList[4][1] + ".png"

    for cutString in cutStrings:
        efficiencyHist = TH1D("effHist", "", varList[1][0],
                              varList[1][1], varList[1][2])
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
    c1.Print(filename_pdf)
    # c1.Print(filename_png)


def simplePlotter(varList, ntuple_files, ntuple_names, labels,
                  cutStrings, line_colours, folder_name="",
                  rootFolder="plots", drawLogY=False):
    gStyle.SetOptStat(0)

    if folder_name == "":
        folder = rootFolder + "/"
    else:
        folder = rootFolder + "/" + folder_name + "/"
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Get ntuples
    ntuples = []
    unique_files = {}
    for ntuple_file, ntuple_name in zip(ntuple_files, ntuple_names):
        if ntuple_file in unique_files:
            ntuples.append(unique_files[ntuple_file].Get(ntuple_name))
        else:
            f = TFile.Open(ntuple_file)
            unique_files[ntuple_file] = f
            ntuples.append(f.Get(ntuple_name))

    c = TCanvas('c', '', 200, 10, 700, 500)
    if drawLogY is True:
        c.SetLogy()
    legend = TLegend(0.55, 0.7, 0.9, 0.9)
    histList = []
    for ntuple, label, cutString, line_colour in zip(ntuples,
                                                     labels,
                                                     cutStrings,
                                                     line_colours):
        randomID = randomword(10)

        recoHist = TH1D("recoHist" + randomID, "", varList[1][0], varList[1][1],
                        varList[1][2])
        recoHist.Sumw2()
        ntuple.Project("recoHist" + randomID, varList[2], cutString[0])
        # Make dist histogram
        recoHist.SetMinimum(0)
        recoHist.GetXaxis().SetTitle(varList[0][1])
        recoHist.GetYaxis().SetTitle("# of muons")
        recoHist.SetMinimum(0.0001)

        legend.SetFillStyle(0)

        recoHist.SetLineColor(line_colour)
        histList.append(recoHist)
        legend.AddEntry(recoHist, label, "L")

    for hist in histList:
        hist.Draw("hist,SAME")
        c.Update()

    legend.Draw("SAME")
    c.Update()

    dist_filename_list = []
    dist_filename_list.append("dist")
    dist_filename_list.append(varList[0][0])
    dist_filename_list.append(cutString[1])
    dist_filename = '_'.join(dist_filename_list)
    distCompTitle = folder + dist_filename
    c.Print(distCompTitle + ".png")


# varlist entries:
# 0: descriptive string used for caption and filename (what is plotted)
# 1: binning
# 2: variables to plot
# 3: physical cuts
def generateCombinedRateHist(varList, ntuple_file, ntupleMC_file, dataset="",
                             datasetMC=""):
    if ntupleMC_file == "":
        gStyle.SetOptStat(110011)
    else:
        gStyle.SetOptStat(0)

    # Get ntuple
    f = TFile.Open(ntuple_file)
    ntuple = f.Get("ntuple")

    c1 = TCanvas('c1', "", 200, 10, 700, 500)
    rateHist = TH1D("rateHist", "",
                    varList[1][0], varList[1][1], varList[1][2])
    ntuple.Project("rateHist", varList[2], varList[3][0])
    rateHist.GetXaxis().SetTitle(varList[0][1])
    rateHist.Draw("hist")

    if ntupleMC_file != "":
        # Get ntuple
        fMC = TFile.Open(ntupleMC_file)
        ntuple = fMC.Get("ntuple")

        rateHistMC = TH1D("rateHistMC", "",
                          varList[1][0], varList[1][1], varList[1][2])
        ntuple.Project("rateHistMC", varList[2], varList[3][0])
        rateHistMC.GetXaxis().SetTitle(varList[0][1])
        rateHistMC.SetLineColor(kRed)
        rateHistMC.Draw("hist,SAME")

        legend = TLegend(0.55, 0.8, 0.9, 0.9)
        legend.SetFillStyle(0)
        legend.AddEntry(rateHist, dataset, "L")
        legend.AddEntry(rateHistMC, datasetMC, "L")
        legend.Draw("")

        combString = "_comb"
    else:
        combString = ""

    c1.Update()
    if dataset != "":
        dataset += "_"
    if datasetMC != "":
        datasetMC += "_"
    filename_pdf = "plots/dist_" + dataset + datasetMC +\
        varList[0][0] + "_" + varList[3][1] + combString + ".pdf"
    filename_png = "plots/dist_" + dataset + datasetMC +\
        varList[0][0] + "_" + varList[3][1] + combString + ".png"
    c1.Print(filename_pdf)
    # c1.Print(filename_png)


# varlist entries:
# 0: descriptive string used for caption and filename (what is plotted)
# 1: binning
# 2: variables to plot
# 3: physical cuts
# 4: list of 'cuts' for each component of stack
#    (optional, used for subsystem separation)
def generateRateStack(varList, ntuple_file, dataset=""):
    gStyle.SetOptStat(110011)
    legend = TLegend(0.85, 0.70, 0.99, 0.99)

    # Get ntuple
    f = TFile.Open(ntuple_file)
    ntuple = f.Get("ntuple")

    # Create descriptive strings
    descrWspaces = " - " + varList[3][1]
    descrWOspaces = "_" + varList[3][1]
    title = ""

    c1 = TCanvas('c1', title, 200, 10, 700, 500)
    histStack = THStack("histStack", "")

    # Create cut strings
    cutStrings = []
    for compCutDict in varList[4]:
        descr = compCutDict[1]
        cut = compCutDict[0] + " && " + varList[3][0]
        cutStrings.append([descr, cut, compCutDict[2]])

    if dataset != "":
        dataset += "_"
    filename_pdf = "plots/dist_" + dataset + "stack_" + varList[0][0] +\
        descrWOspaces + ".pdf"
    filename_png = "plots/dist_" + dataset + "stack_" + varList[0][0] +\
        descrWOspaces + ".png"

    for cutString in cutStrings:
        rateHist = TH1D("rateHist", cutString[0], varList[1][0], varList[1][1],
                        varList[1][2])
        ntuple.Project("rateHist", varList[2], cutString[1])
        rateHist.SetFillColor(cutString[2])
        histStack.Add(rateHist)
        legend.AddEntry(rateHist, cutString[0], "F")
    histStack.Draw()
    legend.Draw("")
    c1.Update()
    c1.Print(filename_pdf)
    # c1.Print(filename_png)


# varlist entries:
# 0: descriptive string used for caption and filename (what is plotted)
# 1: Binning for first variable
# 2: Binning for second variable
# 3: Variables to plot (in the form x2:x1) (!)
# 4: physical cuts on GMT muons
# 5: physical cuts on reco (and GMT) muons
# 6: axis labels
def generate2DEfficiencyHist(varList, ntuple_file, dataset=""):
    gStyle.SetOptStat(0)

    # Get ntuple
    f = TFile.Open(ntuple_file)
    ntuple = f.Get("ntuple")

    descrWspaces = " - " + varList[4][1] + ", "
    descrWOspaces = "_" + varList[4][1] + "_"
    c1 = TCanvas()
    tmpHist = TH2D("tmpHist", "", varList[1][0], varList[1][1], varList[1][2],
                   varList[2][0], varList[2][1], varList[2][2])
    efficiencyHist = TH2D("effHist", "",
                          varList[1][0], varList[1][1], varList[1][2],
                          varList[2][0], varList[2][1], varList[2][2])
    ntuple.Project("tmpHist", varList[3], varList[5][0])
    ntuple.Project("effHist", varList[3],
                   varList[4][0] + " && " + varList[5][0])
    efficiencyHist.Divide(tmpHist)
    axLbl = varList[3].split(":")
    efficiencyHist.GetXaxis().SetTitle(varList[6][0])
    efficiencyHist.GetYaxis().SetTitle(varList[6][1])
    efficiencyHist.DrawCopy("COLZ")
    c1.Update()
    if dataset != "":
        dataset += "_"
    filename_pdf = "plots/hist2D_eff_" + dataset + \
        varList[0][0] + descrWOspaces + varList[5][1] + ".pdf"
    filename_png = "plots/hist2D_eff_" + dataset + \
        varList[0][0] + descrWOspaces + varList[5][1] + ".png"
    c1.Print(filename_pdf)
    # c1.Print(filename_png)


# varlist entries:
# 0: descriptive string used for caption and filename (what is plotted)
# 1: Binning for first variable
# 2: Binning for second variable
# 3: Variables to plot (in the form x1:x2)
# 4: physical cuts
# 5: axis labels
def generate2DRateHist(varList, ntuple_file, ntuple_name, dataset=""):
    gStyle.SetOptStat(0)
    tdrstyle.setTDRStyle()
    CMS_lumi.lumi_sqrtS = "13 TeV"
    iPeriod = 0
    gStyle.SetPalette(53)

    # Get ntuple
    f = TFile.Open(ntuple_file)
    ntuple = f.Get(ntuple_name)

    c1 = TCanvas("c1", "", 700, 500)
    c1.SetRightMargin(0.175)

    rateHist = TH2D("rateHist", "",
                    varList[1][0], varList[1][1], varList[1][2], varList[2][0],
                    varList[2][1], varList[2][2])
    ntuple.Project("rateHist", varList[3], varList[4][0])
    rateHist.GetYaxis().SetTitle(varList[5][0])
    rateHist.GetXaxis().SetTitle(varList[5][1])
    rateHist.DrawCopy("COLZ")
    c1.Update()
    if dataset != "":
        dataset += "_"
    filename_pdf = "plots/hist2D_dist_" + dataset + varList[0] + "_" +\
        varList[4][1] + ".pdf"
    # filename_png = "plots/hist2D_dist_" + dataset + varList[0] + "_" +\
    #     varList[4][1] + ".png"
    c1.Print(filename_pdf)
    # c1.Print(filename_png)


# varlist entries:
# 0: descriptive string used for caption and filename (what is plotted)
# 1: binning
# 2: variables to plot
# 3: physical cuts on GMT muons in first ntuple
# 4: physical cuts on GMT muons in second ntuple
# 5: physical cuts on reco (and GMT) muons
# (optional) 6: Range of y-axis
def generateCombinedGhostPercHist(varList, ntuple_files,
                                  ntuple_names, distribution_labels,
                                  line_colours, gmt_cuts, folder_name="",
                                  drawGenMus=True, drawDistributions=False,
                                  drawStackPlot=False, rootFolder="plots",
                                  distLogy=False):
    generateEffOrPercHist(varList, ["Probability for Ghosts", "ghost"],
                          ntuple_files, ntuple_names, distribution_labels,
                          line_colours, gmt_cuts, folder_name, drawGenMus,
                          drawDistributions, drawStackPlot, rootFolder,
                          distLogy)


# varlist entries:
# 0: descriptive string used for caption and filename (what is plotted)
# 1: binning
# 2: variables to plot
# 3: physical cuts on reco (and GMT) muons
# (optional) 4: Range of y-axis
def generateCombinedEfficiencyHist(varList, ntuple_files,
                                   ntuple_names, distribution_labels,
                                   line_colours, gmt_cuts, folder_name="",
                                   drawGenMus=True, drawDistributions=False,
                                   drawStackPlot=False, rootFolder="plots",
                                   distLogy=False):
    generateEffOrPercHist(varList, ["Efficiency", "eff"], ntuple_files,
                          ntuple_names, distribution_labels, line_colours,
                          gmt_cuts, folder_name, drawGenMus, drawDistributions,
                          drawStackPlot, rootFolder, distLogy)


# varlist entries:
# 0: descriptive string used for caption and filename (what is plotted)
# 1: binning
# 2: variables to plot
# 3: physical cuts
def generateRateHist(varList, ntuple_file, dataset="Data", datasetMC="MC"):
    generateCombinedRateHist(
        varList, ntuple_file, ntupleMC_file="", dataset="")

# Binning

binningDict = {}
binningDict["charge"] = [5, -2, 2]
binningDict["etaFine"] = [100, -2.6, 2.6]
binningDict["etaFineRestr"] = [25, -1, 2.6]
binningDict["etaFine_centralRegion"] = [80, -1.6, 1.6]
binningDict["phiFine"] = [100, -3.2, 3.2]
binningDict["phiFineRestr"] = [25, -0.2, 2]
binningDict["ptFine"] = [100, 0, 200]
binningDict["pt140Fine"] = [50, 0, 140]
binningDict["pt50Fine"] = [100, 0, 50]
binningDict["pt25Fine"] = [100, 0, 25]
binningDict["invMassFine"] = [40, 3, 3.2]
binningDict["distNarrow"] = [50, 0, 0.4]
binningDict["distWide"] = [25, 0, 1]
binningDict["distSym"] = [80, -1, 1]
binningDict["distVeryWide"] = [15, 0, 15]
binningDict["distWideFine"] = [100, 0, 1]


# Cuts

mu1_recoPt1 = "(pT1_reco>1)"
mu1_gmtPt1 = "(pT1_GMT>1)"
mu1_recoPt5 = "(pT1_reco>5)"
mu1_gmtPt5 = "(pT1_GMT>5)"
jPsiPt1 = "(pT_dimuon>1)"
jPsiPt5 = "(pT_dimuon>5)"
diMu_recoPt1 = "((pT1_reco>1) && (pT2_reco>1))"
diMu_gmtPt1 = "((pT1_GMT>1) && (pT2_GMT>1))"
diMu_recoPt5 = "((pT1_reco>5) && (pT2_reco>5))"
diMu_gmtPt5 = "((pT1_GMT>5) && (pT2_GMT>5))"
DTRPC1 = "(SubsysID1_GMT == 0)"
DTRPC2 = "(SubsysID2_GMT == 0)"
CSCRPC1 = "(SubsysID1_GMT == 1)"
CSCRPC2 = "(SubsysID2_GMT == 1)"
DT1 = "(SubsysID1_GMT == 2)"
DT2 = "(SubsysID2_GMT == 2)"
CSC1 = "(SubsysID1_GMT == 3)"
CSC2 = "(SubsysID2_GMT == 3)"
RPC1 = "((SubsysID1_GMT == 4) || (SubsysID1_GMT == 5))"
RPC2 = "((SubsysID2_GMT == 4) || (SubsysID2_GMT == 5))"

correctCharges = "(Ch1_GMT == Ch1_reco) && (Ch2_GMT == Ch2_reco)"
usableCharges = "(((Ch1_GMT == Ch1_reco) && (Ch2_GMT == Ch2_reco)) ||\
    ((Ch1_GMT != Ch1_reco) && (Ch2_GMT != Ch2_reco)))"

mass3to32 = "(InvMass_dimuon >= 3) && (InvMass_dimuon <= 3.2)"

diMu_barrelRegion = "((abs(Eta1_reco) <= 0.8) && (abs(Eta2_reco) <= 0.8))"
diMu_overlapRegion = "((abs(Eta1_reco) > 0.8) && (abs(Eta1_reco) < 1.3) &&\
    (abs(Eta2_reco) > 0.8) && (abs(Eta2_reco) < 1.3))"
diMu_forwardRegion = "((abs(Eta1_reco) => 1.3) && (abs(Eta2_reco) => 1.3))"
diMu_centralRegion = "((abs(Eta1_reco) < 1.6) && (abs(Eta2_reco) < 1.6))"
diMu_forwardRegion = "((abs(Eta1_reco) => 1.6) && (abs(Eta2_reco) => 1.6))"
diMu_centralRegion_gmt = "((abs(Eta1_GMT) < 1.6) && (abs(Eta2_GMT) < 1.6))"
diMu_forwardRegion_gmt = "((abs(Eta1_GMT) => 1.6) && (abs(Eta2_GMT) => 1.6))"

cutDict = {}
cutDict["recoPt1"] = [mu1_recoPt1, "RecoMu1"]
cutDict["gmtPt1"] = [mu1_gmtPt1, "GMTMu1"]
cutDict["recoPt5"] = [mu1_recoPt5, "RecoMu5"]
cutDict["gmtPt5"] = [mu1_gmtPt5, "GMTMu5"]
cutDict["jpsi-Pt1"] = [jPsiPt1, "JPsi1"]
cutDict["jpsi-Pt1_cs"] = ["(" + jPsiPt1 + " && " + correctCharges + ")",
                          "JPsi1_CorrectSign"]
cutDict["jpsi-Pt1_us"] = ["(" + jPsiPt1 + " && " + usableCharges + ")",
                          "JPsi1_UsableSign"]

cutDict["diMu-recoPt1"] = [diMu_recoPt1, "DiRecoMu1"]
cutDict["diMu-recoPt5"] = [diMu_recoPt5, "DiRecoMu5"]

cutDict["diMu-gmtPt1"] = [diMu_gmtPt1, "DiGMTMu1"]
cutDict["diMu-gmtPt1_cs"] = ["(" + diMu_gmtPt1 + " && " + correctCharges + ")",
                             "DiGMTMu1_CorrectSign"]
cutDict["diMu-gmtPt1_us"] = ["(" + diMu_gmtPt1 + " && " + usableCharges + ")",
                             "DiGMTMu1_UsableSign"]
cutDict["diMu-gmtPt1-mass3to32"] = ["(" + diMu_gmtPt1 + " && " +
                                    mass3to32 + ")",
                                    "DiGMTMu1_Mass3to32"]
cutDict["diMu-gmtPt1-mass3to32_cs"] = ["(" + diMu_gmtPt1 + " && " +
                                       mass3to32 + " && " +
                                       correctCharges + ")",
                                       "DiGMTMu1_Mass3to32_CorrectSign"]
cutDict["diMu-gmtPt1-mass3to32_us"] = ["(" + diMu_gmtPt1 + " && " +
                                       mass3to32 + " && " +
                                       usableCharges + ")",
                                       "DiGMTMu1_Mass3to32_UsableSign"]

cutDict["diMu-gmtPt5"] = [diMu_gmtPt5, "DiGMTMu5"]
cutDict["diMu-gmtPt5_cs"] = ["(" + diMu_gmtPt5 + " && " + correctCharges + ")",
                             "DiGMTMu5_CorrectSign"]
cutDict["diMu-gmtPt5_us"] = ["(" + diMu_gmtPt5 + " && " + usableCharges + ")",
                             "DiGMTMu5_UsableSign"]

cutDict["diMu-recoPt1-brl"] = ["(" + diMu_recoPt1 +
                               " && " + diMu_barrelRegion + ")",
                               "DiGMTMu1_BarrelRegion"]
cutDict["diMu-recoPt1-ovl"] = ["(" + diMu_recoPt1 +
                               " && " + diMu_overlapRegion + ")",
                               "DiGMTMu1_OverlapRegion"]
cutDict["diMu-recoPt1-fwd"] = ["(" + diMu_recoPt1 +
                               " && " + diMu_forwardRegion + ")",
                               "DiGMTMu1_ForwardRegion"]
cutDict["diMu-recoPt1-central"] = [
    "(" + diMu_recoPt1 + " && " + diMu_centralRegion + ")",
    "DiGMTMu1_CentralRegion"]
cutDict["diMu-recoPt1-forward"] = [
    "(" + diMu_recoPt1 + " && " + diMu_forwardRegion + ")",
    "DiGMTMu1_ForwardRegion"]
cutDict["diMu-recoPt5-brl"] = ["(" + diMu_recoPt5 +
                               " && " + diMu_barrelRegion + ")",
                               "DiGMTMu5_BarrelRegion"]
cutDict["diMu-recoPt5-ovl"] = ["(" + diMu_recoPt5 +
                               " && " + diMu_overlapRegion + ")",
                               "DiGMTMu5_OverlapRegion"]
cutDict["diMu-recoPt5-fwd"] = ["(" + diMu_recoPt5 +
                               " && " + diMu_forwardRegion + ")",
                               "DiGMTMu5_ForwardRegion"]
cutDict["diMu-recoPt5-forward"] = [
    "(" + diMu_recoPt5 + " && " + diMu_forwardRegion + ")",
    "DiGMTMu5_ForwardRegion"]
cutDict["diMu-gmtPt1-forward_etagmt"] = [
    "(" + diMu_gmtPt1 + " && " + diMu_forwardRegion_gmt + ")",
    "DiGMTMu5_ForwardRegion"]
cutDict["diMu-recoPt5-central"] = [
    "(" + diMu_recoPt5 + " && " + diMu_centralRegion + ")",
    "DiGMTMu5_CentralRegion"]
cutDict["diMu-gmtPt1-central_etagmt"] = [
    "(" + diMu_gmtPt1 + " && " + diMu_centralRegion_gmt + ")",
    "DiGMTMu5_CentralRegion"]
cutDict["diMu-gmtPt1-central_etagmt_us"] = [
    "(" + diMu_gmtPt1 + " && " + usableCharges + " && " +
    diMu_centralRegion_gmt + ")",
    "DiGMTMu5_CentralRegion_UsableSign"]
cutDict["diMu-gmtPt1-mass3to32-central_etagmt"] = [
    "(" + diMu_gmtPt1 + " && " + diMu_centralRegion_gmt +
    " && " + mass3to32 + ")",
    "DiGMTMu5_Mass3to32_CentralRegion"]
cutDict["diMu-gmtPt1-mass3to32-central_etagmt_cs"] = [
    "(" + diMu_gmtPt1 + " && " + correctCharges + " && " +
    mass3to32 + " && " + diMu_centralRegion_gmt + ")",
    "DiGMTMu5_Mass3to32_CentralRegion_CorrectSign"]
cutDict["diMu-gmtPt1-mass3to32-central_etagmt_us"] = [
    "(" + diMu_gmtPt1 + " && " + usableCharges + " && " +
    mass3to32 + " && " + diMu_centralRegion_gmt + ")",
    "DiGMTMu5_Mass3to32_CentralRegion_UsableSign"]

cutDict["jpsi-Pt1-central"] = ["(" + jPsiPt1 + " && " +
                               diMu_centralRegion_gmt + ")",
                               "JPsi1_CentralRegion"]
cutDict["jpsi-Pt1-central_cs"] = ["(" + jPsiPt1 + " && " +
                                  diMu_centralRegion_gmt +
                                  " && " + correctCharges + ")",
                                  "JPsi1_CentralRegion_CorrectSign"]
cutDict["jpsi-Pt1-central_us"] = ["(" + jPsiPt1 + " && " +
                                  diMu_centralRegion_gmt +
                                  " && " + usableCharges + ")",
                                  "JPsi1_CentralRegion_UsableSign"]
cutDict["jpsi-Pt1-mass3to32-central"] = ["(" + jPsiPt1 + " && " + mass3to32 +
                                         " && " + diMu_centralRegion_gmt + ")",
                                         "JPsi1_Mass3to32_CentralRegion"]
cutDict["jpsi-Pt1-mass3to32-central_cs"] = ["(" + jPsiPt1 + " && " +
                                            mass3to32 + " && " +
                                            diMu_centralRegion_gmt +
                                            " && " + correctCharges + ")",
                                            "JPsi1_Mass3to32_CentralRegion_CorrectSign"]
cutDict["jpsi-Pt1-mass3to32-central_us"] = ["(" + jPsiPt1 + " && " +
                                            mass3to32 + " && " +
                                            diMu_centralRegion_gmt +
                                            " && " + usableCharges + ")",
                                            "JPsi1_Mass3to32_CentralRegion_UsableSign"]


# #TODO:0 Find better colours.
DTconfirmed = kGreen - 2
DTonly = kGreen - 9
CSCconfirmed = kBlue - 3
CSConly = kBlue - 10
RPC = kRed - 3

cutDict["DTRPC1"] = [DTRPC1, "DT+RPC", DTconfirmed]
cutDict["DTRPC2"] = [DTRPC2, "DT+RPC", DTconfirmed]
cutDict["CSCRPC1"] = [CSCRPC1, "CSC+RPC", CSCconfirmed]
cutDict["CSCRPC2"] = [CSCRPC2, "CSC+RPC", CSCconfirmed]
cutDict["DT1"] = [DT1, "DT", DTonly]
cutDict["DT2"] = [DT2, "DT", DTonly]
cutDict["CSC1"] = [CSC1, "CSC", CSConly]
cutDict["CSC2"] = [CSC2, "CSC", CSConly]
cutDict["RPC1"] = [RPC1, "RPC", RPC]
cutDict["RPC2"] = [RPC2, "RPC", RPC]

stackCutDict = {}
stackCutDict["subsystems_mu1"] = [cutDict["DTRPC1"], cutDict["CSCRPC1"],
                                  cutDict["DT1"], cutDict["CSC1"],
                                  cutDict["RPC1"]]
stackCutDict["subsystems_mu2"] = [cutDict["DTRPC2"], cutDict["CSCRPC2"],
                                  cutDict["DT2"], cutDict["CSC2"],
                                  cutDict["RPC2"]]
