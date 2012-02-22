#include "TF1.h"

void plotTxt(double lumi);
void readValuesFromLandsFile(char * temp, double &my_obs,double * my_exp);

int mkBrLimits_processBrPlots()
{
  gROOT->ProcessLine(".L mkBrLimits_processBrPlots_plotstyle.cxx");
  setTDRStyle();

  tdrStyle->SetTitleFillColor(0);
  tdrStyle->SetTitleFontSize(0.05);
  tdrStyle->SetTitleX(0.3); // Set the position of the title box

  char temp[200];

  // --- Data: mass points and efficiencies hard-coded --- 
   const int nData = 7; // 90 not yet ready
   double mH[nData]   = 
     {80,
      100,     
      120,     
      140,         
      150,    
      155, 
      160};

   // --- Read initial values from input files ---
   // Check that all datacards have the same luminosity
  double L;
  for (int index=0; index<nData; index++){
    sprintf(temp,"outputs/input_luminosity_%d",mH[index]);

    ifstream fileLumi(temp,ios::in); 
    double tmpL;
    fileLumi >> tmpL;
    if (index==0)
      L = tmpL;
    else if (tmpL != L){
      cout << "Different luminosity value in datacards, now exit!" << endl;
      exit(-1);
    }
  }

  // --- Read obs and exp values from LandS files ---
  char fileName[500];   
  double valueLandS_obs[nData];
  double valueLandS_exp[nData][5];
  //  cout << "----- give name of LandS files to be read -----" << endl;
  //  cout << "e.g. output_LandS_HPlusHadronic will read the files" << endl;
  //  cout << "     output_LandS_HPlusHadronic_M80/100/120/etc." << endl;
  //  cin >> fileName;

  sprintf(fileName,"outputs/output_lands_datacard_hplushadronic_m");
  cout << endl << "File name is " << fileName << endl;

  for (int i=0; i<nData; i++){
    //    sprintf(temp,"output_LandS_HPlusHadronic_%d",mH[i]);
    sprintf(temp,"%s%d",fileName,mH[i]);
    readValuesFromLandsFile(temp,valueLandS_obs[i],valueLandS_exp[i]);
  }

  // --- Plot #events vs. Br ---
  // for mH = 120
  const int plot_this = 1; // makes plots for illustration, 1 for mH=120 
  // --- Plot Br 95% CL limit plot ---
  double BR_95_obs[nData],BR_95_exp[nData], BR_95_exp_p1[nData], BR_95_exp_m1[nData], BR_95_exp_p2[nData], BR_95_exp_m2[nData];
  for (int i=0; i<nData; i++){ 
    BR_95_obs[i] = valueLandS_obs[i]    ;
    BR_95_exp[i] =  valueLandS_exp[i][2] ;
    BR_95_exp_p1[i] = valueLandS_exp[i][2+1] ;
    BR_95_exp_m1[i] = valueLandS_exp[i][2-1] ;
    BR_95_exp_p2[i] = valueLandS_exp[i][2+2] ;
    BR_95_exp_m2[i] = valueLandS_exp[i][2-2] ;
  }
  TCanvas * can_br = new TCanvas();
  can_br->SetTitle("95\% CL limit for BR");
  TGraph * tg_obs = new TGraph(nData, mH, BR_95_obs);
  tg_obs->SetTitle("95\% CL limit for BR");
  tg_obs->SetMarkerStyle(20);
  tg_obs->SetFillStyle(3005);
  tg_obs->SetMarkerSize(1.4);
  tg_obs->SetLineWidth(3);
  tg_obs->Draw("LPA");
  tg_obs->GetYaxis()->SetRangeUser(0,0.2);
  tg_obs->GetYaxis()->SetTitle("95\% CL limit for Br(t#rightarrow bH^{#pm})");
  tg_obs->GetXaxis()->SetTitle("m_{H^{+}} (GeV/c^{2})");
  tg_obs->  GetXaxis()->SetTitleFont(43);
  tg_obs->  GetYaxis()->SetTitleFont(43);
  tg_obs->  GetXaxis()->SetTitleSize(33);
  tg_obs->  GetYaxis()->SetTitleSize(33);
  tg_obs->  GetXaxis()->SetLabelFont(43);
  tg_obs->  GetYaxis()->SetLabelFont(43);
  tg_obs->  GetXaxis()->SetLabelSize(27);
  tg_obs->  GetYaxis()->SetLabelSize(27);
  TGraph * tg_exp = new TGraph(nData, mH, BR_95_exp);
  tg_exp->SetLineColor(2);
  tg_exp->SetMarkerColor(2);
  tg_exp->SetMarkerStyle(21);
  tg_exp->SetMarkerSize(1.4);
  tg_exp->SetLineWidth(3);
  tg_exp->SetLineStyle(2);
  tg_exp->Draw("LP");
  double BR_95_exp_contour1[2*nData], BR_95_exp_contour2[2*nData], myx[2*nData];
  for (int i=0; i<nData; i++){
    BR_95_exp_contour1[i]       = BR_95_exp_m1[i];
    BR_95_exp_contour1[nData+i] = BR_95_exp_p1[nData-1-i];
    BR_95_exp_contour2[i]       = BR_95_exp_m2[i];
    BR_95_exp_contour2[nData+i] = BR_95_exp_p2[nData-1-i];
    myx[i]       = mH[i];
    myx[nData+i] = mH[nData-1-i];
  }
  TGraph * tg_exp_cont1 = new TGraph(2*nData, myx, BR_95_exp_contour1);
  TGraph * tg_exp_cont2 = new TGraph(2*nData, myx, BR_95_exp_contour2);
  tg_exp_cont1->SetFillColor(5);
  tg_exp_cont2->SetFillColor(kOrange);
  tg_exp_cont2->Draw("F");
  tg_exp_cont1->Draw("F");

  TLegend *pl = new TLegend(0.5,0.60,0.82,0.82);
  pl->SetTextSize(0.03);
  pl->SetFillStyle(4000);
  pl->SetTextFont(62);
  pl->SetTextSize(0.03);
  pl->SetBorderSize(0);
  TLegendEntry *ple;
  ple = pl->AddEntry(tg_obs, "Observed", "lp");
  ple = pl->AddEntry(tg_exp, "Expected median", "lp");
  char temp[200];
  sprintf(temp,"Expected median #pm1 #sigma");
  ple = pl->AddEntry(tg_exp_cont1, temp, "f");
  sprintf(temp,"Expected median #pm2 #sigma");
  ple = pl->AddEntry(tg_exp_cont2, temp, "f");
  pl->Draw();
  // Redraw lines on top of filled area
  tg_obs->Draw("LP same");
  tg_exp->Draw("LP same");

  plotTxt(L);

  // --- Plot LIP and Tevatron observed results (in black) ---
  if (0) plotLipResults(pl);
  if (0) plotTevatronResults(pl);

  // Save TGraphs and plots
  TFile myfi("limits.root","recreate");
  tg_obs->SetName("tg_obs"); tg_obs->Write();
  tg_exp->SetName("tg_exp"); tg_exp->Write();
  tg_exp_cont1->SetName("tg_exp_cont1"); tg_exp_cont1->Write();
  tg_exp_cont2->SetName("tg_exp_cont2"); tg_exp_cont2->Write();
  can_br->Write();
  myfi.Close();
  can_br->SaveAs("limitsBr.eps");
  can_br->SaveAs("limitsBr.png");
  can_br->SaveAs("limitsBr.C");
  
  return 0;
}


void plotTevatronResults(TLegend * pl){
    TGraph * tevaGraph;

    // Results fom arxiv:0908.1811v2, table II, tauonic observed values
    // FERMILAB-PUB-09/393-E
    Double_t tevax[] =    {  80, 100, 120, 140, 150, 155};
    Double_t tevayObs[] = { .16, .15, .17, .18, .19, .18}; 

    tgObsTeva = new TGraph(6,tevax,tevayObs);
    tgObsTeva->SetLineColor(kBlue);
    tgObsTeva->SetLineStyle(2);
    tgObsTeva->SetLineWidth(1);
    tgObsTeva->SetMarkerColor(kBlue);
    tgObsTeva->SetMarkerSize(1.0);
    tgObsTeva->Draw("LP");
    pl->AddEntry(tgObsTeva, "D0 1.0 fb^{-1} observed, approximate", "lp");
  return;
}


void plotLipResults(TLegend * pl){
  // from approval of 10.3.2011
  double xLip[] = {80,100,120,140,  150,  155,160};
  double yLipObs[] = {.25 , .23 , .24 , .27, .327, .385, .53};
  double yLipExp[] = {.255, .235, .245, .28, .34 , .405, .58};
  TGraph * tgLIPObs = new TGraph(7,xLip,yLipObs);
  TGraph * tgLIPExp = new TGraph(7,xLip,yLipExp);
  tgLIPObs->SetLineWidth(1);
  tgLIPObs->SetLineStyle(3);
  tgLIPObs->SetMarkerStyle(22);
  tgLIPObs->SetMarkerSize(1.1);
  tgLIPExp->SetLineWidth(1);
  tgLIPExp->SetLineColor(2);
  tgLIPExp->SetLineStyle(3);
  tgLIPExp->SetMarkerColor(2);
  tgLIPExp->SetMarkerStyle(23);
  tgLIPExp->SetMarkerSize(1.1);
  tgLIPObs->Draw("LP");
  tgLIPExp->Draw("LP");
  pl->AddEntry(tgLIPObs, "hadr.#tau+e/#mu channel, observed", "lp");
  pl->AddEntry(tgLIPExp, "hadr.#tau+e/#mu channel, expected", "lp");
  return;
}


void readValuesFromLandsFile(char * fileName, double &my_obs,double * my_exp)
{
  // First line : obs
  // Second line: exp, exp+-1sigma, exp+-2sigma
  cout << fileName << endl;
  ifstream logFile(fileName,ios::in);    
  if (!logFile) {
    cout << "No LandS input file " << fileName << endl;
    exit (-1) ;
  }
  logFile >> my_obs;
  cout << "Observed: " << my_obs << endl;
  for (int j=0; j<5; j++) logFile >> my_exp[j];
  cout << "Expected ";
  for (int j=0; j<5; j++) {
    cout << my_exp[j] << "  ";
  }
  cout << endl;
  return;
}


void plotTxt(double lumi) {
  // Text describing 
  //  1) decay channel
  //  2) final state
  //  3) assumption that Br(H->tau nu) = 1 
  Double_t linePos       = 0.9;
  Double_t lineSpace = 0.038;
  Double_t left      = 0.185;
  TLatex text;
  text.SetTextAlign(12);
  text.SetNDC();
  text.SetTextFont(63);
  text.SetTextSize(20);
  text.DrawLatex(left,linePos,"t#rightarrowH^{#pm}b, H^{#pm}#rightarrow#tau#nu");
  text.DrawLatex(left,linePos -= lineSpace,"#tau_{h}+jets final state");
  // --- Other possible final states --
  //  text.DrawLatex(left,linePos -= lineSpace,"hadr. + ltau final states");
  //text.DrawLatex(left,linePos -= lineSpace,"#tau_{h}+jets, e#tau_{h}, #mu#tau_{h}, and e#mu final states");
  text.DrawLatex(left,linePos -= lineSpace,"Br(H^{#pm}#rightarrow#tau^{#pm} #nu) = 1");


  // "CMS Preliminary" / "CMS" text
  TLatex *tex = new TLatex(0.62,0.96,"CMS Preliminary");
  //  TLatex *tex = new TLatex(0.62,0.96,"CMS");
  tex->SetNDC();
  tex->SetTextFont(43);
  tex->SetTextSize(27);
  tex->SetLineWidth(2);
  tex->Draw();

  // "Sqrt(s) = 7 TeV" text
  tex = new TLatex(0.2,0.96,"#sqrt{s} = 7 TeV");
  tex->SetNDC();
  tex->SetTextFont(43);
  tex->SetTextSize(27);
  tex->SetLineWidth(2);
  tex->Draw();

  // Integrated luminosity text
  char temp[300];
  sprintf(temp,"%.1f fb^{-1}",lumi);
  tex = new TLatex(0.43,0.96,temp);
  tex->SetNDC();
  tex->SetTextFont(43);
  tex->SetTextSize(27);
  tex->SetLineWidth(2);
  tex->Draw();

  return;
}

