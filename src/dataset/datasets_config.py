# entry structure
# - dataset name
# -- included_labels
# -- include_operator
# -- excluded_labels
datasets_config = {
    "dataset_v01_busicorp": {
        "included_labels": ["Business & Corporate"],
        "include_operator": "AND",
        "excluded_labels": [
            "E-Commerce",
            "Technology",
            "Portfolio",
            "Food & Drink",
        ],
    },
    "dataset_v01_tech": {
        "included_labels": ["Technology"],
        "include_operator": "AND",
        "excluded_labels": [
            "E-Commerce",
            "Business & Corporate",
            "Portfolio",
            "Food & Drink",
        ],
    },
    "dataset_v01_tech_white": {
        "included_labels": ["Technology", "White"],
        "include_operator": "AND",
        "excluded_labels": ["Colorful"],
    },
    "dataset_v01_white": {
        "included_labels": ["White"],
        "include_operator": "AND",
        "excluded_labels": ["Colorful"],
    },
    "dataset_v01_startups_clean": {
        "included_labels": ["Startups", "Clean"],
        "include_operator": "AND",
        "excluded_labels": [],
    },
    "dataset_v01_all": {
        "included_labels": [],
        "include_operator": "AND",
        "excluded_labels": [],
    },
}
