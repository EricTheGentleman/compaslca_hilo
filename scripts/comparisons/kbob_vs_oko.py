import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.patches import Patch
import matplotlib.ticker as ticker

def plot_kbob_vs_okobaudat(kbob_csv, okobau_csv, output_dir):

    # Colors
    kbob_objecttype_color = "#3399cc"   # darker skyblue
    kbob_unique_color = "#993399"      # darker orchid
    okobau_objecttype_color = "skyblue"
    okobau_unique_color = "orchid"

    kbob_indicator = "Global Warming Potential Total [kgCO2-eqv]"
    okobau_indicator = "GWPtotal"

    kbob_cols = {
        "min": f"{kbob_indicator} (min)",
        "mean": f"{kbob_indicator} (mean)",
        "max": f"{kbob_indicator} (max)"
    }
    okobau_cols = {
        "min": f"{okobau_indicator} (min)",
        "mean": f"{okobau_indicator} (mean)",
        "max": f"{okobau_indicator} (max)"
    }

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    kbob_df = pd.read_csv(kbob_csv, na_values=["not matched", "not available", ""])
    okobau_df = pd.read_csv(okobau_csv, na_values=["not matched", "not available", ""])

    required_kbob = ["Name", "Compiled"] + list(kbob_cols.values())
    required_okobau = ["Name", "Compiled"] + list(okobau_cols.values())
    if not all(col in kbob_df.columns for col in required_kbob):
        print("Missing required columns in KBOB.")
        return
    if not all(col in okobau_df.columns for col in required_okobau):
        print("Missing required columns in ÖKOBAUDAT.")
        return

    for col in kbob_cols.values():
        kbob_df[col] = pd.to_numeric(kbob_df[col], errors='coerce')
    for col in okobau_cols.values():
        okobau_df[col] = pd.to_numeric(okobau_df[col], errors='coerce')

    # Prepare KBOB subset
    kbob_df["KBOB_mean"] = kbob_df[kbob_cols["mean"]]
    kbob_df["KBOB_error"] = (kbob_df[kbob_cols["max"]] - kbob_df[kbob_cols["min"]]) / 2
    kbob_data = kbob_df[["Name", "KBOB_mean", "KBOB_error", "Compiled"]].rename(columns={"Compiled": "KBOB_Compiled"})

    # Prepare ÖKOBAUDAT subset
    okobau_df["ÖKOBAUDAT_mean"] = okobau_df[okobau_cols["mean"]]
    okobau_df["ÖKOBAUDAT_error"] = (okobau_df[okobau_cols["max"]] - okobau_df[okobau_cols["min"]]) / 2
    okobau_data = okobau_df[["Name", "ÖKOBAUDAT_mean", "ÖKOBAUDAT_error", "Compiled"]].rename(columns={"Compiled": "ÖKOBAUDAT_Compiled"})

    # Merge both datasets
    merged = pd.merge(kbob_data, okobau_data, on="Name", how="outer")

    # Determine top 20 elements by max GWP from either source
    merged["max_mean"] = merged[["KBOB_mean", "ÖKOBAUDAT_mean"]].max(axis=1)
    merged = merged.sort_values(by="max_mean", ascending=False).head(20).reset_index(drop=True)

    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.4
    x = range(len(merged))
    x_kbob = [i - bar_width / 2 for i in x]
    x_okobau = [i + bar_width / 2 for i in x]

    # KBOB bars and placeholders
    for i in x:
        if pd.notna(merged["KBOB_mean"].iloc[i]):
            color = kbob_objecttype_color if merged["KBOB_Compiled"].iloc[i] else kbob_unique_color
            ax.bar(x_kbob[i], merged["KBOB_mean"].iloc[i], width=bar_width, color=color, edgecolor='none')
            err = ax.errorbar(x_kbob[i], merged["KBOB_mean"].iloc[i], yerr=merged["KBOB_error"].iloc[i],
                              fmt='none', ecolor='black', capsize=3.5, linewidth=0.7)
            for cap in err[1]:
                cap.set_linewidth(0.3)
        else:
            height = merged["ÖKOBAUDAT_mean"].iloc[i] if pd.notna(merged["ÖKOBAUDAT_mean"].iloc[i]) else 0
            ax.bar(x_kbob[i], height, width=bar_width, color='lightgrey', edgecolor='none', alpha=0.7)
            ax.bar(x_kbob[i], height, width=bar_width, color='none', edgecolor='silver', hatch='//', linewidth=0.8)

    # ÖKOBAUDAT bars and placeholders
    for i in x:
        if pd.notna(merged["ÖKOBAUDAT_mean"].iloc[i]):
            color = 'skyblue' if merged["ÖKOBAUDAT_Compiled"].iloc[i] else 'orchid'
            ax.bar(x_okobau[i], merged["ÖKOBAUDAT_mean"].iloc[i], width=bar_width, color=color, edgecolor='none')
            err = ax.errorbar(x_okobau[i], merged["ÖKOBAUDAT_mean"].iloc[i], yerr=merged["ÖKOBAUDAT_error"].iloc[i],
                              fmt='none', ecolor='black', capsize=3.5, linewidth=0.7)
            for cap in err[1]:
                cap.set_linewidth(0.3)
        else:
            height = merged["KBOB_mean"].iloc[i] if pd.notna(merged["KBOB_mean"].iloc[i]) else 0
            ax.bar(x_okobau[i], height, width=bar_width, color='lightgrey', edgecolor='none', alpha=0.7)
            ax.bar(x_okobau[i], height, width=bar_width, color='none', edgecolor='silver', hatch='//', linewidth=0.8)

    # X-axis labels
    ax.set_xticks(x)
    ax.set_xticklabels(merged["Name"], rotation=45, ha='right', fontsize=7)
    for i, label in enumerate(ax.get_xticklabels()):
        label.set_color(kbob_objecttype_color if merged["KBOB_Compiled"].iloc[i] else kbob_unique_color)


    # Labels and title
    ax.set_ylabel(kbob_indicator, fontsize=8)
    ax.set_title("Top 20 Elements by GWP – KBOB vs ÖKOBAUDAT", fontsize=10)

    ax.legend(handles=[
        Patch(facecolor=kbob_objecttype_color, label='KBOB – ObjectType'),
        Patch(facecolor=kbob_unique_color, label='KBOB – Unique Element'),
        Patch(facecolor=okobau_objecttype_color, label='ÖKOBAUDAT – ObjectType'),
        Patch(facecolor=okobau_unique_color, label='ÖKOBAUDAT – Unique Element'),
        Patch(facecolor='lightgrey', edgecolor='silver', hatch='//', label='Missing in one source')
    ], loc='upper right', fontsize=7, frameon=False)

    ax.set_axisbelow(True)
    # Set major and minor y-axis ticks
    ax.yaxis.set_major_locator(ticker.MultipleLocator(5000))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(1000))

    # Major grid lines (5000): bold/dark
    ax.grid(which='major', axis='y', linestyle='-', linewidth=0.5, color='gray', alpha=0.6)

    # Minor grid lines (1000): thin/light
    ax.grid(which='minor', axis='y', linestyle='--', linewidth=0.3, color='lightgrey', alpha=0.5)


    plt.tight_layout()

    # Save
    output_path = Path(output_dir) / "gwp_comparison_plot"
    plt.savefig(output_path.with_suffix(".png"), dpi=400)
    plt.savefig(output_path.with_suffix(".pdf"), format="pdf")
    plt.close()
    print(f"Saved: {output_path}")

# Example usage
if __name__ == "__main__":
    kbob_csv = "data/pipeline/step_03_lca_calculation/step_03b_gross_emissions/kbob/BoQ.csv"
    oekobaudat_csv = "data/pipeline/step_03_lca_calculation/step_03b_gross_emissions/oekobaudat/BoQ.csv"
    output_dir = "data/output/comparison"
    plot_kbob_vs_okobaudat(kbob_csv, oekobaudat_csv, output_dir)

