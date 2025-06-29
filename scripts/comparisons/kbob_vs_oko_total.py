import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def plot_total_gwp_clustered(kbob_csv, okobau_csv, output_path):
    # Indicators to aggregate
    kbob_indicators = [
        "Global Warming Potential Manufacturing [kgCO2-eqv]",
        "Global Warming Potential Disposal [kgCO2-eqv]",
        "Global Warming Potential Total [kgCO2-eqv]",
    ]

    okobau_indicators = [
        "GWPtotal (A1-A3)",
        "GWPtotal (A4)",
        "GWPtotal (A5)",
        "GWPtotal (C1)",
        "GWPtotal (C2)",
        "GWPtotal (C3)",
        "GWPtotal (C4)",
        "GWPtotal"
    ]

    # Load data
    kbob_df = pd.read_csv(kbob_csv, na_values=["not matched", "not available", ""])
    okobau_df = pd.read_csv(okobau_csv, na_values=["not matched", "not available", ""])

    # Store results
    indicators = []
    means = []
    errors = []
    colors = []

    # Color scheme
    kbob_color = "#3399cc"       # darker skyblue
    okobau_color = "orchid"

    # Process KBOB indicators
    for ind in kbob_indicators:
        min_col, mean_col, max_col = f"{ind} (min)", f"{ind} (mean)", f"{ind} (max)"
        if all(col in kbob_df.columns for col in [min_col, mean_col, max_col]):
            mean_total = kbob_df[mean_col].sum()
            diffs = kbob_df[[max_col, min_col]].dropna()
            error_total = ((diffs[max_col] - diffs[min_col]) / 2).clip(lower=0).sum()

            indicators.append(ind)
            means.append(mean_total)
            errors.append(error_total)
            colors.append(kbob_color)
        else:
            print(f"Missing columns for KBOB indicator: {ind}")

    # Process ÖKOBAUDAT indicators
    for ind in okobau_indicators:
        min_col, mean_col, max_col = f"{ind} (min)", f"{ind} (mean)", f"{ind} (max)"
        if all(col in okobau_df.columns for col in [min_col, mean_col, max_col]):
            mean_total = okobau_df[mean_col].sum()
            diffs = okobau_df[[max_col, min_col]].dropna()
            error_total = ((diffs[max_col] - diffs[min_col]) / 2).clip(lower=0).sum()

            indicators.append(ind)
            means.append(mean_total)
            errors.append(error_total)
            colors.append(okobau_color)
        else:
            print(f"Missing columns for ÖKOBAUDAT indicator: {ind}")

    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))

    # Define special colors
    kbob_color = "#f5c396"
    kbob_total_color = "#db8c2e"    # darker blue for total
    okobau_color = "#e1d3f9"
    okobau_total_color = "#c3a6f3"  # darker magenta for total

    # Bar placement settings
    kbob_letter_width = 0.3
    okobau_letter_width = 0.15
    okobau_total_width = 0.3

    # Build x positions
    kbob_count = len(kbob_indicators)
    okobau_letters = okobau_indicators[:-1]  # all except GWPtotal
    okobau_total = okobau_indicators[-1]

    kbob_x = [i * 0.4 for i in range(kbob_count)]
    kbob_widths = [kbob_letter_width] * kbob_count

    # Start ÖKOBAUDAT group with a gap
    start_oko = kbob_x[-1] + 0.5
    okobau_letter_x = [start_oko + i * 0.2 for i in range(len(okobau_letters))]
    okobau_letter_widths = [okobau_letter_width] * len(okobau_letters)

    # Position total bar with 0.3 gap after last letter
    okobau_total_x = okobau_letter_x[-1] + 0.3
    okobau_total_widths = [okobau_total_width]

    # Merge all
    x_positions = kbob_x + okobau_letter_x + [okobau_total_x]
    bar_widths = kbob_widths + okobau_letter_widths + okobau_total_widths
    all_indicators = kbob_indicators + okobau_letters + [okobau_total]

    # Plot each bar
    for x_val, width, mean, err, label in zip(x_positions, bar_widths, means, errors, indicators):
        if label == "Global Warming Potential Total [kgCO2-eqv]":
            color = kbob_total_color
        elif label == "GWPtotal":
            color = okobau_total_color
        elif label in kbob_indicators:
            color = kbob_color
        else:
            color = okobau_color

        ax.bar(x_val, mean, yerr=err, capsize=4, width=width, color=color, edgecolor='none')



    # Update x-axis ticks
    ax.set_xticks(x_positions)
    ax.set_xticklabels(indicators, rotation=45, ha='right', fontsize=8)

    ax.set_ylabel("Total GWP [kgCO2-eqv]", fontsize=10)
    ax.set_title("Total Global Warming Potential – KBOB vs ÖKOBAUDAT", fontsize=12)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, which='major', linestyle='-', linewidth=0.5, color='gray', alpha=0.4)



    plt.tight_layout()

    # Save as PNG and PDF
    output_path = Path(output_path)
    plt.savefig(output_path.with_suffix(".png"), dpi=300)
    plt.savefig(output_path.with_suffix(".pdf"), format="pdf")
    plt.close()
    print(f"Saved: {output_path.with_suffix('.png')} and .pdf")

# Example usage
if __name__ == "__main__":
    kbob_csv = "data/pipeline/step_03_lca_calculation/step_03b_gross_emissions/kbob/BoQ.csv"
    okobau_csv = "data/pipeline/step_03_lca_calculation/step_03b_gross_emissions/oekobaudat/BoQ.csv"
    output_path = "data/output/comparison/total_gwp_clustered_plot"
    plot_total_gwp_clustered(kbob_csv, okobau_csv, output_path)
