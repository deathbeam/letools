import json
import xml.dom.minidom
import xml.etree.ElementTree as ET
import argparse
import os


def load_json_data(filename):
    with open(filename, "r", encoding="utf-8") as f:
        items = json.load(f)
        print(f"Loaded {len(items)} items from {filename}")
        return items

def create_filter(items, output_filename):
    print(f"Creating filter with {len(items)} unique items...")

    # Create root ItemFilter element
    root = ET.Element("ItemFilter")
    # Add rules element
    rules_element = ET.SubElement(root, "rules")
    # Create a single rule for all unique items
    rule_element = ET.SubElement(rules_element, "Rule")

    # Add rule type
    type_element = ET.SubElement(rule_element, "type")
    type_element.text = "HIDE"

    # Add conditions
    conditions_element = ET.SubElement(rule_element, "conditions")

    # Add RarityCondition
    rarity_condition = ET.SubElement(conditions_element, "Condition")
    rarity_condition.set(
        "{http://www.w3.org/2001/XMLSchema-instance}type", "RarityCondition"
    )

    rarity_element = ET.SubElement(rarity_condition, "rarity")
    rarity_element.text = "UNIQUE"

    min_lp_element = ET.SubElement(rarity_condition, "minLegendaryPotential")
    min_lp_element.set("{http://www.w3.org/2001/XMLSchema-instance}nil", "true")

    max_lp_element = ET.SubElement(rarity_condition, "maxLegendaryPotential")
    max_lp_element.text = "0"

    min_ww_element = ET.SubElement(rarity_condition, "minWeaversWill")
    min_ww_element.set("{http://www.w3.org/2001/XMLSchema-instance}nil", "true")

    max_ww_element = ET.SubElement(rarity_condition, "maxWeaversWill")
    max_ww_element.text = "14"

    # Add UniquesCondition
    condition_element = ET.SubElement(conditions_element, "Condition")
    condition_element.set(
        "{http://www.w3.org/2001/XMLSchema-instance}type", "UniquesCondition"
    )

    # Add unique IDs
    unique_ids_element = ET.SubElement(condition_element, "uniqueIds")
    for item in items:
        if "id" in item:  # Make sure the item has an ID
            id_element = ET.SubElement(unique_ids_element, "unsignedShort")
            id_element.text = str(item["id"])

    # Add additional required elements
    color_element = ET.SubElement(rule_element, "color")
    color_element.text = "5"

    is_enabled = ET.SubElement(rule_element, "isEnabled")
    is_enabled.text = "true"

    level_dependent = ET.SubElement(rule_element, "levelDependent")
    level_dependent.text = "false"

    min_lvl = ET.SubElement(rule_element, "minLvl")
    min_lvl.text = "0"

    max_lvl = ET.SubElement(rule_element, "maxLvl")
    max_lvl.text = "0"

    emphasized = ET.SubElement(rule_element, "emphasized")
    emphasized.text = "false"

    name_override = ET.SubElement(rule_element, "nameOverride")
    name_override.text = "BAD UNIQUES"

    # Register namespace for the i:type attribute
    ET.register_namespace("i", "http://www.w3.org/2001/XMLSchema-instance")

    # Create and write the tree with pretty formatting
    with open(output_filename, "w", encoding="utf-8") as f:
        rough_string = ET.tostring(root, "utf-8")
        reparsed = xml.dom.minidom.parseString(rough_string)
        f.write(
            reparsed.toprettyxml(indent="  ")[23:]
        )  # Skip the XML declaration that toprettyxml adds

    print(f"Filter saved to {output_filename}")


def filter_items(items):
    filtered_items = []
    for item in items:
        if item['rarityTier'] == "T4" and item['canDropRandomly']:
            filtered_items.append(item)
    print(f"Filtered {len(filtered_items)} items")
    return filtered_items


def main():
    parser = argparse.ArgumentParser(
        description="Create Last Epoch filter from scraped unique items"
    )
    parser.add_argument(
        "--input",
        "-i",
        default="output/unique_items.json",
        help="Path to the JSON file containing scraped unique items",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="output/unique_items.xml",
        help="Path to save the output XML filter file",
    )

    args = parser.parse_args()

    # Make sure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    # Load data and create filter
    items = load_json_data(args.input)
    items = filter_items(items)
    create_filter(items, args.output)


if __name__ == "__main__":
    main()
