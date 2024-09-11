import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.style as style
import json
import argparse
from datetime import date, datetime
from matplotlib.ticker import FormatStrFormatter
import itertools

style.use('wp3.mplstyle')

def get_pitch_value(hfunit):
    if hfunit == 'tb':
        return 22.5
    elif hfunit == 'bb':
        return 18
    else:
        return 22.5  # 默认值为 22.5，适用于其他 hfunit

def add_chip_info(ax1, moss_name, hu, pitch):
    moss_name_formatted = moss_name.replace("_", "\\_")
    hu_formatted = hu.upper()

    text = (
        rf"$\bf{{{moss_name_formatted} \ {hu_formatted}}}$" "\n"
        rf"Pitch: {pitch} $\mu$m" "\n"
        r"Split 2" "\n"
        r"$\it{I_{bias}} = 62 \ \mathrm{DAC}$" "\n"
        r"$\it{I_{biasn}} = 100 \ \mathrm{DAC}$" "\n"
        r"$\it{I_{reset}} = 10 \ \mathrm{DAC}$" "\n"
        r"$\it{I_{db}} = 50 \ \mathrm{DAC}$" "\n"
        r"$\it{V_{shift}} = 145 \ \mathrm{DAC}$" "\n"
        r"$\it{V_{casn}} = 104 \ \mathrm{DAC}$" "\n"
        r"$\it{V_{psub}} = -1.2 \ \mathrm{V}$" "\n"
        r"Strobe length = 6.0 $\mu$s" "\n"
        r"T = 27°C"
    )

    ax1.text(
        1.15, 0.95,
        text,
        fontsize=14,
        ha='left', va='top',
        transform=ax1.transAxes
    )

def add_fhr_limit(ax2, limit):
    ax2.axhline(limit, linestyle='dotted', color='grey')
    ax2.text(ax2.get_xlim()[1] * 0.98, limit * 1.70,
             "FHR measurement sensitivity limit",
             fontsize=9, color='grey',
             ha='right', va='top',
             )

def add_annotations(ax1, moss_name, hfunit):
    beam_info = '@ CERN PS Sept 2024, \n10 GeV/c $\\pi^{-}$'
    plot_date = str(date.today().day) + ' ' + datetime.now().strftime("%b") + ' ' + str(date.today().year)
    ax1.text(
        0.01, 0.3,
        '$\\bf{ALICE ITS3}$ beam test $\\it{WIP}$, \n'+beam_info+', \nPlotted on {}'.format(plot_date),
        fontsize=13,
        ha='left', va='top',
        transform=ax1.transAxes
    )

def add_masked_pixels_text(ax1, masked_regions=None, number_masked_regions=None):
    if masked_regions:
        if number_masked_regions:
            masked_text = f"Association window: 100 \u03BCm, masked per region ({', '.join(number_masked_regions)})."
        else:
            masked_text = f"Association window: 100 \u03BCm, masked pixels in regions {', '.join(map(str, masked_regions))}."
    else:
        masked_text = "Association window: 100 \u03BCm. No masked pixels."

    ax1.text(
        0.01, 0.025,
        masked_text,
        fontsize=9, color='black',
        ha='left', va='center',
        transform=ax1.transAxes
    )

def plot_eff_fhr(data, path_to_plots, moss_name, hfunit, x_axis_var, masked_regions=None, pitch=22.5, number_masked_regions=None):
    if masked_regions is None:
        masked_regions = []

    fig, ax1 = plt.subplots(figsize=(13, 6))
    plt.subplots_adjust(left=0.07, right=0.67, top=0.95)
    
    # 判断是否需要绘制 FHR
    plot_fhr = any(f"{region}" in data and "fhr" in data[f"{region}"] for region in range(4))
    if plot_fhr:
        ax2 = ax1.twinx()

    x_axis_min, x_axis_max = float('inf'), float('-inf')

    detection_efficiency = ax1.errorbar([], [], yerr=[], label="Detection efficiency", marker='s', color='grey', elinewidth=1.3, capsize=3)
    if plot_fhr:
        fake_hit_rate = ax1.errorbar([], [], yerr=[], label="Fake-hit rate", marker='s', markerfacecolor='none', linestyle='--', color='grey', elinewidth=1.3, capsize=3)
    region_lines = []

    color_cycle = itertools.cycle(plt.rcParams['axes.prop_cycle'].by_key()['color'])

    for region in range(4):
        if f"{region}" not in data:
            print(f"Region {region} data not found, skipping...")
            continue

        eff = data[f"{region}"].get("eff", [])
        eff_err_low = data[f"{region}"].get("eff_err_low", [])
        eff_err_up = data[f"{region}"].get("eff_err_up", [])
        
        if plot_fhr:
            if region in masked_regions:
                fhr = data[f"{region}"].get("masked_fhr", [])
                fhr_err_low = data[f"{region}"].get("masked_fhr_err_low", [])
                fhr_err_up = data[f"{region}"].get("masked_fhr_err_up", [])
            else:
                fhr = data[f"{region}"].get("fhr", [])
                fhr_err_low = data[f"{region}"].get("fhr_err_low", [])
                fhr_err_up = data[f"{region}"].get("fhr_err_up", [])

        thr = data[f"{region}"].get("thr", [])
        VCASB_region = data[f"{region}"]["VCASB"]

        if x_axis_var == "vcasb":
            x_axis = np.array(VCASB_region)
        elif x_axis_var == "thr":
            x_axis = np.array(thr)
        else:
            raise ValueError("Invalid x_axis variable. It must be 'vcasb' or 'thr'.")

        if len(x_axis) == 0:
            continue

        x_axis_min = min(x_axis_min, np.min(x_axis))
        x_axis_max = max(x_axis_max, np.max(x_axis))

        min_length = min(len(x_axis), len(eff), len(eff_err_low), len(eff_err_up))

        x_axis = x_axis[:min_length]
        eff = eff[:min_length]
        eff_err_low = eff_err_low[:min_length]
        eff_err_up = eff_err_up[:min_length]

        color = next(color_cycle)
        line = ax1.errorbar(x_axis, eff, yerr=[eff_err_low, eff_err_up], label=f"Region {region}", marker="s", color=color)
        region_lines.append(line)

        if plot_fhr:
            min_length_fhr = min(len(x_axis), len(fhr), len(fhr_err_low), len(fhr_err_up))
            fhr_x = x_axis[:min_length_fhr]
            fhr = fhr[:min_length_fhr]
            fhr_err_low = fhr_err_low[:min_length_fhr]
            fhr_err_up = fhr_err_up[:min_length_fhr]

            ax2.errorbar(fhr_x, fhr, yerr=[fhr_err_low, fhr_err_up], marker="s", linestyle="dashed", markerfacecolor="none", color=color)

        if x_axis_var == "thr" and plot_fhr:
            ax2.invert_xaxis()

    ax1.set_ylabel("Detection efficiency (%)")
    if plot_fhr:
        ax2.set_ylabel("Fake-hit rate (hits/pixel/event)")

    if x_axis_var == "vcasb":
        ax1.set_xlabel(r"$\it{V}_{\mathrm{casb}}~\mathrm{(DAC)}$")
    elif x_axis_var == "thr":
        ax1.set_xlabel(r"$Threshold~\mathrm{(VPULSEH}~\mathrm{DAC)}$")

    ax1.yaxis.set_major_formatter(FormatStrFormatter('%0.0f'))

    ax1.set_ylim(82, 100)
    if plot_fhr:
        ax2.set_ylim(0, 1e-1)
        ax2.set_yscale('symlog', linthresh=1e-8, linscale=0.90)

    ax1.set_xlim(x_axis_min - 3, x_axis_max + 3)
    if x_axis_var == "thr":
        ax1.set_xlim(x_axis_min - 1, x_axis_max + 1)

    if plot_fhr:
        ax1.legend(loc='lower right', bbox_to_anchor=(1.50, -0.09), handles=[detection_efficiency, fake_hit_rate] + [line for line in region_lines])
    else:
        ax1.legend(loc='lower right', bbox_to_anchor=(1.50, -0.09), handles=[detection_efficiency] + [line for line in region_lines])

    ax1.grid()
    ax1.set_yticks(np.linspace(ax1.get_ybound()[0], ax1.get_ybound()[1], 9))

    ax1.axhline(99, linestyle='dashed', color='grey')
    ax1.text(ax1.get_xlim()[0] - 0.014 * (ax1.get_xlim()[1] - ax1.get_xlim()[0]), 99, "", fontsize=12, ha='right', va='center')

    if plot_fhr:
        ax2.set_yticks([0, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1])
        ax2.axhline(1e-6, linestyle='dashed', color='grey')
        ax2.text(ax2.get_xlim()[1] * 0.999, 1e-6 + 0.0000005, "ITS3 FHR requirements", fontsize=9, color='grey', ha='right', va='top')

    add_chip_info(ax1, moss_name, hfunit, pitch)
    add_annotations(ax1, moss_name, hfunit)
    add_masked_pixels_text(ax1, masked_regions, number_masked_regions)

    suffix = f"_masked_region_{'_'.join(map(str, masked_regions))}" if masked_regions else ""
    plt.savefig(f"{path_to_plots}/ALICE-ITS3-2024-08_II_{moss_name}_{hfunit}_{x_axis_var}_vs_eff_fhr{suffix}.pdf")
    plt.savefig(f"{path_to_plots}/ALICE-ITS3-2024-08_II_{moss_name}_{hfunit}_{x_axis_var}_vs_eff_fhr{suffix}.png")

def plot_res_cls(data, path_to_plots, moss_name, hfunit, x_axis_var, masked_regions=None, pitch=22.5, number_masked_regions=None):
    if masked_regions is None:
        masked_regions = []

    fig, ax1 = plt.subplots(figsize=(13, 6))
    plt.subplots_adjust(left=0.07, right=0.67, top=0.95)
    ax2 = ax1.twinx()

    x_axis_min, x_axis_max = float('inf'), float('-inf')

    spatial_resolution = ax1.errorbar([], [], yerr=[], label="Spatial resolution", marker='s', color='grey', elinewidth=1.3, capsize=3)
    cluster_size = ax1.errorbar([], [], yerr=[], label="Cluster size", marker='s', markerfacecolor='none', linestyle='--', color='grey', elinewidth=1.3, capsize=3)
    
    region_lines = []

    color_cycle = itertools.cycle(plt.rcParams['axes.prop_cycle'].by_key()['color'])

    for region in range(4):
        if f"{region}" not in data:
            print(f"Region {region} data not found, skipping...")
            continue

        res = data[f"{region}"].get("res_RMS_mean", [])
        res_err = data[f"{region}"].get("res_err", [])
        cls = data[f"{region}"].get("cluster_size_mean", [])
        cls_err = data[f"{region}"].get("cluster_size_mean_err", [])
        thr = data[f"{region}"].get("thr", [])
        VCASB_region = data[f"{region}"]["VCASB"]

        if x_axis_var == "vcasb":
            x_axis = np.array(VCASB_region)
        elif x_axis_var == "thr":
            x_axis = np.array(thr)
        else:
            raise ValueError("Invalid x_axis variable. It must be 'vcasb' or 'thr'.")

        if len(x_axis) == 0:
            continue

        x_axis_min = min(x_axis_min, np.min(x_axis))
        x_axis_max = max(x_axis_max, np.max(x_axis))

        min_length = min(len(x_axis), len(res), len(res_err), len(cls), len(cls_err))

        x_axis = x_axis[:min_length]
        res = res[:min_length]
        res_err = res_err[:min_length]
        cls = cls[:min_length]
        cls_err = cls_err[:min_length]

        color = next(color_cycle)
        line = ax1.errorbar(x_axis, res, yerr=res_err, label=f"Region {region}", marker="s", color=color)
        region_lines.append(line)

        ax2.errorbar(x_axis, cls, yerr=cls_err, marker="s", linestyle="dashed", markerfacecolor="none", color=color)

        if x_axis_var == "thr":
            ax2.invert_xaxis()

    ax1.set_ylabel("Spatial resolution (\u03BCm)")
    ax2.set_ylabel("Cluster size (pixels)")

    if x_axis_var == "vcasb":
        ax1.set_xlabel(r"$\it{V}_{\mathrm{casb}}~\mathrm{(DAC)}$")
    elif x_axis_var == "thr":
        ax1.set_xlabel(r"$Threshold~\mathrm{(VPULSEH}~\mathrm{DAC)}$")

    ax1.yaxis.set_major_formatter(FormatStrFormatter('%0.0f'))
    ax2.yaxis.set_major_formatter(FormatStrFormatter('%0.2f'))

    ax1.set_ylim(2, 10)
    ax2.set_ylim(1, 2)

    ax1.set_xlim(x_axis_min - 3, x_axis_max + 3)
    if x_axis_var == "thr":
        ax1.set_xlim(x_axis_min - 1, x_axis_max + 1)

    ax1.legend(loc='lower right', bbox_to_anchor=(1.50, -0.09), handles=[spatial_resolution, cluster_size] + [line for line in region_lines])

    ax1.grid()

    add_chip_info(ax1, moss_name, hfunit, pitch)
    add_annotations(ax1, moss_name, hfunit)
    add_masked_pixels_text(ax1, masked_regions, number_masked_regions)

    plt.savefig(f"{path_to_plots}/ALICE-ITS3-2024-08_II_{moss_name}_{hfunit}_{x_axis_var}_vs_res_cls.pdf")
    plt.savefig(f"{path_to_plots}/ALICE-ITS3-2024-08_II_{moss_name}_{hfunit}_{x_axis_var}_vs_res_cls.png")

def main(hfunit, moss_name, x_axis_var, masked_regions=None, number_masked_regions=None):
    if masked_regions is None:
        masked_regions = []

    if masked_regions and number_masked_regions:
        number_masked_regions = number_masked_regions.split(',')
        if len(number_masked_regions) != 4:
            raise ValueError("Exactly four numbers must be provided for --number_masked_regions.")

    path_to_json = f"json_files/{moss_name}/{hfunit}"
    path_to_plots = f"plots/{moss_name}/{hfunit}"

    os.makedirs(path_to_plots, exist_ok=True)

    pitch = get_pitch_value(hfunit)

    with open(f'{path_to_json}/{moss_name}_{hfunit}.json') as f:
        data = json.load(f)

    plot_eff_fhr(data, path_to_plots, moss_name, hfunit, x_axis_var, masked_regions, pitch, number_masked_regions)
    # plot_res_cls(data, path_to_plots, moss_name, hfunit, x_axis_var, masked_regions, pitch, number_masked_regions)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plotting script for ALICE ITS3 beam test.')
    parser.add_argument('hfunit', type=str, choices=['t6', 't7', 'b4', 'bb', 'tb'], help='HF Unit, e.g., t6, t7, b4, bb, or tb')
    parser.add_argument('moss_name', type=str, choices=['MOSS-2_W02F4', 'MOSS-3_W08B6', 'babyMOSS-2_3_W04E2', 'babyMOSS-2_3_W24B5', 'babyMOSS-2_2_W21D4'], help='MOSS Name, e.g., MOSS-2_W02F4, MOSS-3_W08B6, or babyMOSS-2_3_W04E2') 
    parser.add_argument('x_axis_var', type=str, choices=['vcasb', 'thr'], help='X-axis variable (VCASB or THR)')
    parser.add_argument('--masked_region', '-mr', nargs='+', type=int, default=[], help='Specify regions to use masked FHR (e.g., --masked_region 0 1)')
    parser.add_argument('--number_masked_regions', '-nmp', type=str, help='Specify four numbers separated by commas for masked per region (e.g., --number_masked_regions 2,2,3,4)')
    args = parser.parse_args()

    main(args.hfunit, args.moss_name, args.x_axis_var, args.masked_region, args.number_masked_regions)
