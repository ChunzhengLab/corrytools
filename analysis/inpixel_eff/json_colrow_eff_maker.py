import array
import ROOT
import os

def custom_rebin_by_bin_number(tefficiency, bin_groups, output_filename):
    passed_histogram = tefficiency.GetPassedHistogram()
    total_histogram = tefficiency.GetTotalHistogram()

    new_bins = len(bin_groups)
    
    new_bin_edges = [0]
    for group in bin_groups:
        new_bin_edges.append(new_bin_edges[-1] + len(group))
    
    if new_bin_edges[-1] > passed_histogram.GetNbinsX():
        new_bin_edges[-1] = passed_histogram.GetNbinsX()

    new_bin_edges = array.array('d', new_bin_edges)
    print(f"New bin edges: {new_bin_edges}")

    new_passed_histogram = ROOT.TH1F("new_passed", "Rebinned Passed", new_bins, new_bin_edges)
    new_total_histogram = ROOT.TH1F("new_total", "Rebinned Total", new_bins, new_bin_edges)

    for i, group in enumerate(bin_groups):
        content_passed = sum(passed_histogram.GetBinContent(bin_num) for bin_num in group)
        content_total = sum(total_histogram.GetBinContent(bin_num) for bin_num in group)

        print(f"Group {i+1}, Bin Numbers: {group}, Passed Content: {content_passed}, Total Content: {content_total}")

        new_passed_histogram.SetBinContent(i + 1, content_passed)
        new_total_histogram.SetBinContent(i + 1, content_total)

    new_tefficiency = ROOT.TEfficiency(new_passed_histogram, new_total_histogram)

    # Save the new passed histogram to a ROOT file
    output_root_file = ROOT.TFile(output_filename, "RECREATE")
    passed_histogram.Write()
    total_histogram.Write()
    output_root_file.Close()
    print(f"Saved new passed histogram to {output_filename}")

    return new_tefficiency

def generate_bin_groups(filename, n_bins):
    bin_groups = []

    if "bb" in filename or "tb" in filename:
        bin_groups.append([1, 2, 3])
        bin_groups.append(list(range(4, 11)))
        for i in range(11, n_bins, 20):
            end = min(i + 20, n_bins + 1)
            bin_groups.append(list(range(i, end)))

    return bin_groups

def process_file(root_filepath, output_directory):
    filename = os.path.basename(root_filepath)
    name, _ = os.path.splitext(filename)

    n_bins = 320 if "bb" in filename else 256 if "tb" in filename else 0
    if n_bins == 0:
        print(f"File {filename} does not match 'bb' or 'tb' naming scheme. Skipping...")
        return

    bin_groups = generate_bin_groups(filename, n_bins)

    root_file = ROOT.TFile.Open(root_filepath)
    print(f"Opened ROOT file: {root_filepath}")

    for region in range(4):  # 处理 region 0 到 3
        tefficiency_rows = root_file.Get(f"AnalysisEfficiency/MOSS_reg{region}_3/efficiencyRows")
        tefficiency_columns = root_file.Get(f"AnalysisEfficiency/MOSS_reg{region}_3/efficiencyColumns")
        
        if tefficiency_rows and tefficiency_columns:
            print(f"Extracting and rebining row and column efficiency data for region {region}...")

            output_filename = os.path.join(output_directory, f"{name}_region{region}_passed_histograms.root")
            tefficiency_rows_rebinned = custom_rebin_by_bin_number(tefficiency_rows, bin_groups, output_filename)
            tefficiency_columns_rebinned = custom_rebin_by_bin_number(tefficiency_columns, bin_groups, output_filename)

            plot_efficiency_with_info(tefficiency_rows, tefficiency_rows_rebinned, f"Row Efficiency (Region {region})", f"{name}_region{region}_row_efficiency", n_bins, filename)
            plot_efficiency_with_info(tefficiency_columns, tefficiency_columns_rebinned, f"Column Efficiency (Region {region})", f"{name}_region{region}_column_efficiency", n_bins, filename)
    
    root_file.Close()
    print(f"Closed ROOT file: {root_filepath}")

def plot_efficiency_with_info(tefficiency, tefficiency_rebinned, title, canvas_name, x_max, filename):
    gStyle = ROOT.gStyle
    gStyle.SetOptStat(0)

    # 解析文件名以提取相关信息
    name_parts = filename.split('_')
    moss_name = name_parts[0] + "_" + name_parts[1] + "_" + name_parts[2]
    hfunit = name_parts[3].lower().strip()
    region = name_parts[4].replace('region', '')
    vcasb = name_parts[5].replace('VCASB', '')

    pitch_size = 18.0 if hfunit == "bb" else 22.5
    half_unit_name = "Bottom half unit" if hfunit == "bb" else "Top half unit"

    # 创建画布并分割为两个 TPad
    c = ROOT.TCanvas(canvas_name, title, 1000, 600)

    # 左侧绘图区域
    pad1 = ROOT.TPad("pad1", "Graph Pad", 0.0, 0.0, 0.7, 1.0)
    pad1.Draw()
    pad1.cd()

    tefficiency.SetLineColor(ROOT.kBlack)
    tefficiency.SetMarkerColor(ROOT.kBlack)
    tefficiency.Draw("AP SAME")

    tefficiency_rebinned.SetLineColor(ROOT.kRed + 1)
    tefficiency_rebinned.SetMarkerColor(ROOT.kRed + 1)
    tefficiency_rebinned.SetFillColorAlpha(ROOT.kRed + 1, 0.3) 
    tefficiency_rebinned.SetMarkerStyle(ROOT.kFullSquare)
    tefficiency_rebinned.SetLineWidth(2)
    tefficiency_rebinned.Draw("SAME E2 P")

    ROOT.gPad.Update()
    tefficiency.GetPaintedGraph().GetXaxis().SetLimits(0, x_max)

    # 添加图例
    legend = ROOT.TLegend(0.65, 0.15, 0.85, 0.4)
    legend.SetBorderSize(0)
    legend.AddEntry(tefficiency, "Efficiency", "lp")
    legend.AddEntry(tefficiency_rebinned, "Rebinned", "lp")
    legend.SetTextSize(0.03)
    legend.Draw()

    c.cd()
    pad2 = ROOT.TPad("pad2", "Text Pad", 0.7, 0.0, 1.0, 1.0)
    pad2.Draw()
    pad2.cd()

    text = ROOT.TPaveText(0.05, 0.1, 0.95, 0.9)
    text.SetTextAlign(12)
    text.SetTextFont(43)
    text.SetTextSize(15)
    text.SetFillColor(0)
    text.SetBorderSize(1)

    text.AddText(f"{moss_name}")
    text.AddText(f"{half_unit_name}, Region {region}")
    text.AddText(f"Pitch: {pitch_size} \\mu m")
    text.AddText("Ibias = 62 DAC")
    text.AddText("Ibiasn = 100 DAC")
    text.AddText("Ireset = 10 DAC")
    text.AddText("Idb = 50 DAC")
    text.AddText("Vshift = 145 DAC")
    text.AddText(f"Vcasb = {vcasb} DAC")
    text.AddText("Vcasn = 104 DAC")
    text.AddText("T = 27 C")
    text.Draw()
    
    # make a directory for the plots
    os.makedirs("./plots_colrow", exist_ok=True)
    c.SaveAs(f"./plots_colrow/{canvas_name}.pdf")

def main():
    input_directory = "./highstat_output"
    output_directory = "./json_files_inpixel_colrow"
    os.makedirs(output_directory, exist_ok=True)

    for filename in os.listdir(input_directory):
        if filename.endswith(".root"):
            root_filepath = os.path.join(input_directory, filename)
            process_file(root_filepath, output_directory)

if __name__ == "__main__":
    main()