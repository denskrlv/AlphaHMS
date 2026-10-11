# Data Preprocessing Pipeline

This directory contains utilities to preprocess raw EEG and Spectrogram data into PyTorch Geometric graphs.

## Overview

The preprocessing pipeline:
1. Loads raw EEG (50s) and Spectrogram (600s) data for each labeled sample
2. Applies signal preprocessing (EEG: band-pass, notch, z-score; Spectrogram: clip, log, normalize)
3. Extracts temporal windows with 50% overlap
4. Computes features and builds graphs:
   - **EEG**: 9 temporal graphs per sample (19 nodes, 64 directed edges from physical electrode adjacency)
   - **Spectrogram**: 119 temporal graphs per sample (4 nodes, 8 fixed spatial edges)
5. Saves processed graphs grouped by `patient_id`

## File Structure

```
src/data/
├── utils/
│   ├── eeg_process.py          # EEG preprocessing, feature extraction & graph building
│   └── spectrogram_process.py  # Spectrogram preprocessing, feature extraction & graph building
├── make_graph_dataset.py       # Main preprocessing script
├── graph_dataset.py            # Graph Dataset (multi-modal / EEG-only)
├── graph_datamodule.py         # LightningDataModule with stratified patient-level K-fold
├── baseline_dataset.py
├── baseline_datamodule.py
├── raw_eeg_dataset.py          # Raw EEG Dataset for the MLP baseline
└── raw_datamodule.py
```

## Configuration

All hyperparameters are defined in `configs/graphs.yaml`:

### EEG Parameters
- **Sampling rate**: 200 Hz
- **Window size**: 10 seconds (2,000 samples)
- **Stride**: 5 seconds (50% overlap)
- **Channels**: 19 EEG channels (excludes EKG)
- **Preprocessing**: Butterworth band-pass 0.5–50 Hz, 60 Hz notch, per-channel z-score
- **Frequency bands**: Delta, Theta, Alpha, Beta, Gamma (Welch PSD)
- **Edge creation**: Physical electrode adjacency in the 10-20 system (`ELECTRODE_ADJACENCY` in `utils/eeg_process.py`), unweighted

### Spectrogram Parameters
- **Duration**: 600 seconds
- **Window size**: 10 seconds
- **Stride**: 5 seconds (50% overlap)
- **Regions**: LL, RL, LP, RP (4 spatial regions)
- **Preprocessing**: Clip to [1e-2, 1e6], log, normalize
- **Frequency bands**: Delta, Theta, Alpha, Beta (spectrograms only go up to ~20 Hz)
- **Aggregation**: Mean pooling over frequency bins
- **Edges**: Fixed spatial connectivity (8 edges)

## Usage

Run all commands from the repository root.

### 1. Create the deduplicated label file

The pipeline reads `data/raw/train_unique.csv`, which is produced by `notebooks/eda.ipynb` (it drops rows of `train.csv` that are duplicated by `eeg_id` and vote counts).

### 2. Run Full Preprocessing

```bash
python src/data/make_graph_dataset.py
```

Options:
- `--workers / -w N` — number of worker processes (default: CPU count − 1)
- `--config PATH` — configuration file (default: `configs/graphs.yaml`)

This will:
- Process all samples from `train_unique.csv` (~20k)
- Group by `patient_id`
- Save one `.pt` file per patient in `data/processed/`
- Save metadata with patient IDs and sample counts (updated every 100 patients)

Preprocessing is resumable: patients that already have a `patient_{id}.pt` file are skipped, so you can safely re-run the script after an interruption.

**Expected output:**
```
data/processed/
├── patient_12345.pt
├── patient_12346.pt
├── ...
└── metadata.pt
```

To inspect the result:

```bash
python inspect_data.py
```

## Output Format

### Patient Files

Each `patient_{patient_id}.pt` contains a dictionary keyed by `label_id`:

```python
{
    label_id_1: {
        'eeg_graphs': [graph_0, graph_1, ..., graph_8],    # 9 PyG Data objects
        'spec_graphs': [graph_0, graph_1, ..., graph_118],  # 119 PyG Data objects
        'target': tensor([...])  # (6,) float tensor: normalized expert vote distribution
    },
    label_id_2: {
        ...
    },
    ...
}
```

### Metadata File

`metadata.pt` contains:

```python
{
    'n_patients': ...,
    'n_samples': ...,
    'patient_ids': [12345, 12346, ...],
    'samples_per_patient': {12345: 20, 12346: 15, ...},
    'config': {...}  # Full configuration used
}
```

## Graph Structure

Every graph also carries `time_idx` (window position) and `is_center` (whether the window contains the labeled region).

### EEG Graph
- **Nodes**: 19 (one per EEG channel)
- **Node features**: (19, 5) - 5 band powers per channel
- **Edges**: 64 directed edges (32 neighboring electrode pairs, both directions); identical for every window
- **Edge features**: (64, 1) - all ones (unweighted)

### Spectrogram Graph
- **Nodes**: 4 (LL, RL, LP, RP regions)
- **Node features**: (4, 4) - 4 aggregated band powers per region
- **Edges**: 8 (fixed spatial connectivity)
- **Edge features**: None

## Loading Processed Data

```python
import torch

# Load single patient (weights_only=False is required for PyG Data objects)
patient_data = torch.load('data/processed/patient_12345.pt', weights_only=False)

# Access specific sample
sample = patient_data[label_id]
eeg_graphs = sample['eeg_graphs']      # List[Data] of length 9
spec_graphs = sample['spec_graphs']    # List[Data] of length 119
target = sample['target']              # (6,) vote distribution

# Load metadata
metadata = torch.load('data/processed/metadata.pt', weights_only=False)
all_patient_ids = metadata['patient_ids']
```

## Label Mapping

Index order of the 6-class target vector:

```python
{
    'Seizure': 0,
    'LPD': 1,      # Lateralized Periodic Discharges
    'GPD': 2,      # Generalized Periodic Discharges
    'LRDA': 3,     # Lateralized Rhythmic Delta Activity
    'GRDA': 4,     # Generalized Rhythmic Delta Activity
    'Other': 5     # Other/Normal
}
```

## Memory Requirements

- **RAM**: ~16-32 GB recommended for full preprocessing
- **Disk**: ~5-10 GB for processed data (all patients)
- **GPU**: Not required for preprocessing

## Troubleshooting

### Missing Files
- Ensure `data/raw/train_unique.csv` exists (run `notebooks/eda.ipynb`)
- Ensure `data/raw/train_eegs/` and `data/raw/train_spectrograms/` contain parquet files

### Out of Memory
- Reduce the number of workers with `--workers`

### Shape Mismatches
- Check that EEG files have correct length (should be ≥10,000 samples)
- Verify spectrogram files have 'time' column

## Next Steps

After preprocessing, train a model (see the main [README](../../README.md#-training)). Train/validation splits are created by `HMSDataModule` using patient-level K-fold cross-validation configured in `configs/train*.yaml`.

## References

- 10-20 system: Standard EEG electrode placement used for graph adjacency
- Welch's method: Estimates power spectral density
- PyTorch Geometric: Graph neural network library
