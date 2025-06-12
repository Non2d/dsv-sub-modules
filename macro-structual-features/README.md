# Macro-Structural Features Calculator

This module implements algorithms to calculate four macro-structural features of rebuttals in parliamentary debates:

1. **Distance**: Measures temporal distance of rebuttals across speeches
2. **Rally**: Measures connectivity of rebuttal chains (A→B→C patterns)
3. **Interval**: Measures dispersion of rebuttals within speeches
4. **Order**: Measures crossing patterns of rebuttals from same speech

## Installation

```bash
cd macro-structual-features
python -m pip install -e .
```

## Usage

### Basic Usage

```python
from macro_structual_features import MacroStructuralCalculator, DebateData, Rebuttal

# Define debate structure
speeches = [1, 3, 5, 7, 9, 11]  # End indices of each speech
rebuttals = [
    Rebuttal(src=2, dst=0),  # ADU 2 rebuts ADU 0
    Rebuttal(src=4, dst=1),  # ADU 4 rebuts ADU 1
    Rebuttal(src=6, dst=2),  # ADU 6 rebuts ADU 2
]

# Calculate features
data = DebateData(speeches, rebuttals)
calculator = MacroStructuralCalculator(data)
results = calculator.calculate_all()

print(results)
# Output: {'distance': 0.5, 'rally': 0.083, 'interval': 0.0, 'order': -1.0}
```

### Individual Feature Calculation

```python
# Calculate individual features
distance = calculator.calc_distance()
rally = calculator.calc_rally()
interval = calculator.calc_interval()
order = calculator.calc_order()
```

## Data Format

### Speeches
List of end indices for each speech. For example:
- `[1, 3, 5, 7, 9, 11]` represents 6 speeches with 2 statements each
- `[2, 5, 8, 11, 14, 17, 20, 23]` represents 8 speeches with 3 statements each

### Rebuttals
List of `Rebuttal(src, dst)` objects where:
- `src`: Index of the source ADU (argument making the rebuttal)
- `dst`: Index of the destination ADU (argument being rebutted)

## Algorithms

### Distance (Algorithm 1)
Calculates the ratio of "distant" rebuttals among rebuttals from speeches 4 and later. A rebuttal is distant if:
- It spans 3+ speeches, OR
- It's from the second-to-last speech and spans 2+ speeches

### Rally (Algorithm 3)
Measures rebuttal chain connectivity by counting cases where one rebuttal's destination becomes another's source, normalized by speeches × rebuttals.

### Interval (Algorithm 2)
Measures dispersion of multiple rebuttals from the same speech to the same target, calculating gaps between source positions.

### Order (Algorithm 4)
Detects crossing rebuttal patterns from the same speech. Returns -1 if no crossings exist, otherwise returns rebuttals/crossings ratio.

## Testing

```bash
python -m unittest test_calculator.py -v
```

## Sample Data

The module includes several sample datasets:
- `get_sample_north_american_style()`: 6-speech North American format
- `get_sample_asian_style()`: 8-speech Asian format  
- `get_sample_interval_case()`: Multiple rebuttals with gaps
- `get_sample_rally_chain()`: Connected rebuttal chains
- `get_sample_order_crossing()`: Crossing rebuttal patterns

## Demo

```bash
python main.py
```

Runs a demonstration with all sample datasets and displays calculated features.