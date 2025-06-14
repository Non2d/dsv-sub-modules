# Directory Structure

This document describes the improved directory structure for the macro-structural features project.

## Current Structure

```
macro-structual-features/
├── main.py                    # Main entry point for calculation
├── CLAUDE.md                  # Project documentation
├── README.md                  # Original README
├── STRUCTURE.md              # This file
├── __init__.py               # Package initialization
├── src/                      # Source code
│   ├── __init__.py
│   ├── calculator.py         # Main calculator class
│   ├── models.py            # Data models
│   └── features/            # Feature calculation modules
│       ├── __init__.py
│       ├── distance.py      # Distance feature calculation
│       ├── interval.py      # Interval feature calculation
│       ├── order.py         # Order feature calculation
│       └── rally.py         # Rally feature calculation
├── tests/                   # Test files
│   ├── __init__.py
│   └── test_distance.py     # Distance feature tests
├── evaluation/              # Evaluation and analysis scripts
│   └── __init__.py
├── scripts/                 # Utility scripts
│   ├── __init__.py
│   ├── demo.py             # Demo script
│   └── run_tests.py        # Test runner
└── data/                   # Data files
    ├── debate_scripts.json
    ├── json2argument_framework.py
    ├── macro_structural_features.tsv
    ├── macro_structural_features_enhanced.tsv
    └── motion_title_content_answer.csv
```

## Usage

### Running the main calculation
```bash
python3 main.py
```

### Running the demo
```bash
python3 scripts/demo.py
```

### Running tests
```bash
python3 scripts/run_tests.py
```

## Benefits of New Structure

1. **Clean root directory**: Only essential files in the root
2. **Logical separation**: Source code, tests, scripts, and data are properly separated
3. **Easy imports**: Proper Python package structure with `__init__.py` files
4. **Maintainable**: Clear organization makes it easy to find and maintain code
5. **Extensible**: Easy to add new features, tests, and evaluation scripts

## Migration Notes

- All core functionality moved to `src/` directory
- Test files moved to `tests/` directory
- Utility scripts moved to `scripts/` directory
- Import paths updated to work with new structure
- Relative paths used for cross-directory imports