import subprocess

# Define the pipeline steps with custom keys
MODULES = [
    {"key": "p1", "name": "     Preview Category Inference Prompt", "path": "lca_pipeline/step_02_material_matching/step_02a_inference/preview_category_prompt.py", "main": False},
    {"key": "p2", "name": "     Preview Material Inference Prompt", "path": "lca_pipeline/step_02_material_matching/step_02a_inference/preview_material_prompt.py", "main": False},
    {"key": "01", "name": "     MODULE 01 → Data Extraction", "main": True},
    {"key": "01a", "name": "    Submodule 01a → Extract All Data from IFC model", "path": "lca_pipeline/step_01_data_extraction/step_01a_extract_all/run.py", "main": False},
    {"key": "01b", "name": "    Submodule 01b → Aggregate Data", "path": "lca_pipeline/step_01_data_extraction/step_01b_aggregate_elements/run.py", "main": False},
    {"key": "01c", "name": "    Submodule 01c → Dissect Layers", "path": "lca_pipeline/step_01_data_extraction/step_01c_dissect_layers/run.py", "main": False},
    {"key": "01d", "name": "    Submodule 01d → Filter JSON Data sheets", "path": "lca_pipeline/step_01_data_extraction/step_01d_filter_data/run.py", "main": False},
    {"key": "02", "name": "     MODULE 02 → LLM-based material matching", "main": True},
    {"key": "02a", "name": "    Submodule 02a → LLM inference of all JSON instances", "path": "lca_pipeline/step_02_material_matching/step_02a_inference/run.py", "main": False},
    {"key": "02b", "name": "    Submodule 02b → Combine LLM inference outputs", "path": "lca_pipeline/step_02_material_matching/step_02b_bookkeeping/run.py", "main": False},
    {"key": "03", "name": "     MODULE 03 → LCA Calculation", "main": True},
    {"key": "03a", "name": "    Submodule 03a → Append specific indicators to elements", "path": "lca_pipeline/step_03_lca_calculation/step_03a_specific_indicators/run.py", "main": False},
    {"key": "03b", "name": "    Submodule 03b → Calculate gross emissions", "path": "lca_pipeline/step_03_lca_calculation/step_03b_gross_emissions/run.py", "main": False},
    {"key": "04", "name": "     MODULE 04 → Create LCA report", "path": "lca_pipeline/step_04_lca_report/run.py", "main": False},
]

def run_module(module):
    print(f"\n🔧 Running module: {module['name']}")
    try:
        subprocess.run(["python", module["path"]], check=True)
        print(f"Finished: {module['name']}")
    except subprocess.CalledProcessError as e:
        print(f"Error running {module['name']}: {e}")

def pipeline_menu():
    while True:
        print("\n==========================")
        print("♻️  COMPAS_LCA PIPELINE ♻️")
        print("==========================\n")
        print("Execute the pipeline sequentially!")
        print("Enter the corresponding characters to run a specific module:\n")

        for i, mod in enumerate(MODULES):
            print(f"  {mod['key'].upper()}. {mod['name']}")

            if mod["key"].lower() == "p2":
                print("")
            
            if mod["key"].lower() == "01d":
                print("")

            if mod["key"].lower() == "02b":
                print("")
            if mod["key"].lower() == "03b":
                print("")
            if mod["key"].lower() == "04":
                print("")

        print("  R. Run all modules sequentially")
        print("  Q. Quit")

        choice = input("\nYour choice: ").strip().lower()

        if choice == "q":
            print("Exiting.")
            break

        elif choice == "r":
            main_modules = [mod for mod in MODULES if mod.get("main")]
            for main_mod in main_modules:
                prefix = main_mod["key"]
                submodules = [mod for mod in MODULES if mod["key"].startswith(prefix) and not mod.get("main")]

                if not submodules:
                    print(f"\n  No submodules found for {prefix} ({main_mod['name'].strip()})")
                else:
                    print(f"\n Running all submodules for {main_mod['name']}")
                    for submod in submodules:
                        run_module(submod)
                        input("Press Enter to continue...")

            print("\n All grouped submodules completed.\n")


        elif choice in [mod["key"].lower() for mod in MODULES]:
            selected = next(mod for mod in MODULES if mod["key"].lower() == choice)

            if selected.get("main"):
                # Normalize comparison to lowercase
                prefix = selected["key"].lower()
                submodules = [mod for mod in MODULES if mod["key"].lower().startswith(prefix) and not mod.get("main")]

                if not submodules:
                    print(f"No submodules found for {prefix}.")
                else:
                    for submod in submodules:
                        run_module(submod)
                        input("Press Enter to continue...")
            else:
                run_module(selected)
                input("Press Enter to return to the menu...")

if __name__ == "__main__":
    pipeline_menu()
