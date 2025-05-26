from pathlib import Path
from methods.filter import (
    load_yaml_config, load_json, save_json,
    filter_element_json, reorder_keys,
    filter_target_layer_json, reorder_keys_target_layer,
    decode_unicode, apply_pset_filter, load_selected_keys
)



def filter_data_sheets():
    # Load master config
    master_config_path = Path("config/master_config.yaml")
    master_config = load_yaml_config(master_config_path)

    filter_mode = master_config.get("filter_config", {}).get("mode")
    preset_name = master_config.get("filter_config", {}).get("preset", "")
    custom_path = master_config.get("filter_config", {}).get("custom_path", "")

    if filter_mode == "custom":
        config_dir = Path(custom_path)
    elif filter_mode == "preset":
        config_dir = Path(f"config/data_filters/filter_presets/{preset_name}")
    else:
        raise ValueError(f"Invalid filter mode: {filter_mode}. Must be 'custom' or 'preset'.")

    # Resolve YAML paths dynamically
    yaml_path_element = config_dir / "filter_element.yaml"
    yaml_path_target_layer = config_dir / "filter_target_layer.yaml"

    # Paths for input/output folders
    element_input_dir = Path("data/pipeline/step_01_data_extraction/step_01c_dissect_layers/Elements")
    element_output_dir = Path("data/pipeline/step_01_data_extraction/step_01d_filter_data/Elements")

    target_layer_input_dir = Path("data/pipeline/step_01_data_extraction/step_01c_dissect_layers/Target_Layers")
    target_layer_output_dir = Path("data/pipeline/step_01_data_extraction/step_01d_filter_data/Target_Layers")

    # Decode any weird strings (especially in Psets)
    decode_unicode(str(element_input_dir))
    decode_unicode(str(target_layer_input_dir))

    # Load YAML filters
    config_element = load_yaml_config(yaml_path_element)
    config_target_layer = load_yaml_config(yaml_path_target_layer)

    # Get "empty value" boolean from master config
    remove_empty = master_config.get("filter_config", {}).get("remove_empty_values", False)

    # Load optional Pset filter configuration (with selected keys)
    use_pset_filter = master_config.get("filter_config", {}).get("use_pset_filter", False)
    pset_key_file = master_config.get("filter_config", {}).get("pset_key_file", "")
    selected_keys = set()
    if use_pset_filter and pset_key_file:
        selected_keys = load_selected_keys(pset_key_file)


    # Process element files
    for file_path in element_input_dir.glob("*.json"):
        try:
            data = load_json(file_path)
            filtered = filter_element_json(data, config_element, remove_empty)
            if use_pset_filter and selected_keys:
                filtered = apply_pset_filter(filtered, selected_keys)
            top_order = master_config.get("filter_config", {}).get("element_key_order", [])
            if top_order:
                filtered = reorder_keys(filtered, top_order)
            save_json(filtered, element_output_dir / file_path.name)
        except Exception:
            continue

    # Process target layer files
    for file_path in target_layer_input_dir.glob("*.json"):
        try:
            data = load_json(file_path)
            filtered = filter_target_layer_json(data, config_target_layer, remove_empty)
            if use_pset_filter and selected_keys:
                filtered = apply_pset_filter(filtered, selected_keys)
            top_order = master_config.get("filter_config", {}).get("target_layer_key_order", [])
            nested_order = master_config.get("filter_config", {}).get("building_element_context_key_order", [])
            if top_order:
                filtered = reorder_keys_target_layer(filtered, top_order)
            if "Building Element Context" in filtered and nested_order:
                filtered["Building Element Context"] = reorder_keys_target_layer(
                    filtered["Building Element Context"], nested_order
                )
            save_json(filtered, target_layer_output_dir / file_path.name)
        except Exception:
            continue

if __name__ == "__main__":
    filter_data_sheets()