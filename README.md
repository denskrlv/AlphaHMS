# AlphaHMS

<p align="center">
  <img src="hero.jpg" alt="AlphaHMS hero image" width="100%" />
  <br/>
  <sub>Photo by <a href="https://unsplash.com/@theshubhamdhage?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Shubham Dhage</a> on <a href="https://unsplash.com/photos/a-brain-displayed-with-glowing-blue-lines-2sz-3NrmZYU?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Unsplash</a></sub>
</p>

**⚡ Multi-modal Graph Neural Networks for Harmful Brain Activity Classification**

AlphaHMS is a deep-learning pipeline for classifying harmful brain activity from EEG and spectrogram recordings, built around the [HMS Harmful Brain Activity Classification](https://www.kaggle.com/competitions/hms-harmful-brain-activity-classification) Kaggle challenge. The system represents each recording as a pair of temporal graph sequences and learns a joint EEG + spectrogram representation with Graph Attention Networks, BiLSTM temporal encoders, hierarchical regional pooling, and cross-modal attention fusion.

🎯 The six target classes are: **Seizure**, **LPD** (Lateralized Periodic Discharges), **GPD** (Generalized Periodic Discharges), **LRDA** (Lateralized Rhythmic Delta Activity), **GRDA** (Generalized Rhythmic Delta Activity), and **Other**.

---

## ✨ Highlights

- 🕸️ **Graph-based EEG modelling** — each 50 s EEG recording is split into 9 overlapping 10 s windows; nodes are the 19 EEG channels and edges follow physical electrode adjacency in the 10-20 system.
- 🌈 **Graph-based spectrogram modelling** — 600 s spectrograms are split into 119 windows over 4 spatial regions (LL, RL, LP, RP) with fixed spatial connectivity.
- 🧩 **Hierarchical pooling** by clinical brain regions (Frontal, Central, Parietal, Occipital) before temporal modelling.
- 🔀 **Cross-modal fusion** with multi-head attention between EEG and spectrogram regional embeddings.
- ⚡ **PyTorch Lightning** training with mixed precision (BF16), WandB logging, cross-validation, class-weighted / KL-divergence losses, and early stopping.
- 🔍 **Explainability** via GNNExplainer and attention-weight inspection.
- 📊 **Baselines** included: EEG-only GNN and a raw-EEG MLP.

---

## 📁 Repository Layout

```
AlphaHMS/
├── assets/
│   ├── architecture.svg           # Architecture figure
│   └── make_architecture_figure.py
├── configs/                       # OmegaConf YAML configs
│   ├── graphs.yaml                # Preprocessing parameters
│   ├── model.yaml                 # Multi-modal GNN architecture
│   ├── model_eeg.yaml             # EEG-only baseline architecture
│   ├── train.yaml                 # Main training config
│   ├── train_4fold.yaml           # Cross-validation training
│   ├── train_eeg.yaml             # EEG-only baseline training
│   ├── training_mlp.yaml          # MLP baseline training
│   ├── inference_mlp.yaml         # MLP inference
│   └── smoke_test.yaml            # Quick smoke test
├── notebooks/
│   └── eda.ipynb                  # Exploratory data analysis & preprocessing
├── src/
│   ├── data/                      # Datasets, DataModules, graph builders
│   │   ├── graph_dataset.py
│   │   ├── graph_datamodule.py
│   │   ├── baseline_dataset.py
│   │   ├── baseline_datamodule.py
│   │   ├── raw_eeg_dataset.py
│   │   ├── raw_datamodule.py
│   │   ├── make_graph_dataset.py  # Build graph dataset from raw data
│   │   └── utils/
│   │       ├── eeg_process.py
│   │       └── spectrogram_process.py
│   ├── models/
│   │   ├── hms_model.py           # Multi-modal model
│   │   ├── hms_eeg_model.py       # EEG-only baseline
│   │   ├── eeg_mlp.py             # MLP baseline
│   │   ├── regularization.py
│   │   ├── explainer_wrappers.py
│   │   └── graph_layers/          # GAT, temporal, fusion, pooling, classifier
│   ├── lightning_trainer/         # LightningModules (multi-modal, EEG, MLP)
│   ├── explainers/
│   │   └── gnn_explainer.py
│   ├── train.py                   # Training entrypoint (GNN models)
│   ├── train_mlp.py               # Training entrypoint (MLP baseline)
│   ├── explain.py                 # GNNExplainer driver
│   ├── explain_attention.py       # Attention-weight analysis
│   └── explain_model.py
├── tests/                         # Pytest suite
├── inspect_data.py                # Quick data inspection utility
├── requirements.txt               # pip / uv dependencies
├── environment.yaml               # Conda environment specification
└── pytest.ini
```

---

## 🛠️ Installation

Requires **Python 3.10+** (3.11 recommended).

### Option A: pip / uv (no Conda)

With [uv](https://docs.astral.sh/uv/) (downloads Python 3.11 if needed):

```bash
uv venv --python 3.11
source .venv/bin/activate
uv pip install -r requirements.txt
```

Or with plain `venv` + pip:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The default PyPI `torch` wheel supports CUDA on Linux and MPS on Apple Silicon. To pin a specific CUDA build, install PyTorch first from [pytorch.org](https://pytorch.org/get-started/locally/) (e.g. `pip install torch --index-url https://download.pytorch.org/whl/cu121`), then install the requirements.

### Option B: Conda

```bash
conda env create -f environment.yaml -y
conda activate graph
```

The environment file deliberately omits PyTorch so you can match your local CUDA version. For CUDA 12.1:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install torch_geometric
```

---

## 📦 Dataset

### 1. Download the raw HMS data

You must accept the competition terms on Kaggle first.

```bash
mkdir -p data/raw && cd data/raw
kaggle competitions download -c hms-harmful-brain-activity-classification
unzip hms-harmful-brain-activity-classification.zip
```

Expected layout under `data/raw/`:

```
data/raw/
├── train.csv
├── train_eegs/            # parquet files, one per EEG recording
└── train_spectrograms/    # parquet files, one per spectrogram
```

### 2. Run the EDA / preprocessing notebook

```bash
jupyter execute notebooks/eda.ipynb
```

Among other things, this writes `data/raw/train_unique.csv` (duplicates of `train.csv` removed), which every later step reads.

### 3. Build the graph dataset

```bash
python src/data/make_graph_dataset.py
```

Use `--workers N` to control the number of processes. Preprocessing is resumable: patients already written to `data/processed/` are skipped.

This produces one `data/processed/patient_{id}.pt` per patient plus a `metadata.pt` index. See [src/data/README.md](src/data/README.md) for full details on graph construction, output format, and memory requirements.

---

## 🚀 Training

All training scripts log to **Weights & Biases**; run `wandb login` once before starting.

### Multi-modal GNN (main model)

```bash
python src/train.py --train-config configs/train.yaml
```

### Cross-validation

`configs/train.yaml` uses 5 folds and `configs/train_4fold.yaml` uses 4 folds. Each run trains a single fold (`data.current_fold`); select the fold with `--fold`:

```bash
python src/train.py --train-config configs/train_4fold.yaml --fold 1
```

Note that `--fold` writes the new `current_fold` back into the config file.

Resume an interrupted run with `--resume path/to/checkpoint.ckpt`.

### EEG-only GNN baseline

```bash
python src/train.py --train-config configs/train_eeg.yaml
```

### MLP baseline (raw EEG)

```bash
python src/train_mlp.py --config configs/training_mlp.yaml
```

This runs patient-level K-fold cross-validation (`--n_splits`, default 5).

### Quick smoke test

```bash
python src/train.py --train-config configs/smoke_test.yaml
```

For the GNN models, the best checkpoint is evaluated automatically at the end of training, and checkpoints are written to `checkpoints/`. The MLP baseline writes per-fold checkpoints under `checkpointing.dirpath` in its config (`artifacts/checkpoints/fold_<k>`).

---

## 🏗️ Model Architecture

<p align="center">
  <img src="assets/architecture.svg" alt="AlphaHMS architecture: scalp EEG and montage spectrograms are windowed into temporal graph sequences, encoded with GATv2, pooled into regions, modelled with BiLSTMs, fused with bidirectional cross-attention, and classified into six classes" width="100%" />
</p>

<sub>**Figure 1.** AlphaHMS pipeline. **(a)** 19-channel scalp EEG (10–20 system); electrode colours mark the clinical regions used for pooling, dashed lines the bipolar chains behind the provided spectrograms. **(b)** EEG is filtered and split into 9 overlapping 10 s windows; spectrograms are log-normalised and split into 119 windows. **(c)** Each window becomes a graph: 19 electrode nodes with 5 PSD band features and 10–20 adjacency edges (EEG), or 4 region nodes with 4 band-power features and fixed spatial edges (spectrogram). **(d)** A shared GATv2 encoder embeds every graph; EEG nodes are mean-pooled into 4 regions. **(e)** A 2-layer BiLSTM models each sequence, attention biased towards the labelled window pools it into one vector, and a linear layer expands that into 4 regional tokens per modality. **(f)** Bidirectional cross-attention fuses the modalities; per-region features are concatenated and attention-pooled. **(g)** An MLP outputs a 6-class distribution trained with KL divergence against the expert-vote distribution. Regenerate with `python assets/make_architecture_figure.py`.</sub>

The multi-modal model (see [configs/model.yaml](configs/model.yaml)) is composed of:

1. **EEG encoder** — 2-layer multi-head GATv2 (64-dim, 4 heads) over the electrode-adjacency graph → hierarchical regional pooling → 2-layer BiLSTM (128-dim, bidirectional).
2. **Spectrogram encoder** — 2-layer GATv2 (64-dim, 4 heads) over the 4 spatial regions → 2-layer BiLSTM (128-dim, bidirectional).
3. **Cross-modal fusion** — multi-head cross-attention (8 heads, 256-dim) between EEG and spectrogram regional embeddings, with attention pooling over regions.
4. **Classifier** — MLP with hidden sizes `[256, 128]`, ELU activations, dropout 0.3 → 6-class softmax.

Loss defaults to **KL divergence** against the soft expert-vote distribution; class weighting, graph-Laplacian regularization, and edge-weight penalties are all configurable.

---

## 🔬 Explainability

```bash
# GNNExplainer over test samples of a fold
python src/explain.py --model_path checkpoints/last.ckpt --current_fold 0 --num_explain 5

# GNNExplainer on a single patient file
python src/explain_model.py --model_path checkpoints/last.ckpt --data_path data/processed/patient_<id>.pt

# Attention-weight visualisation
python src/explain_attention.py --model_path checkpoints/last.ckpt --data_path data/processed/patient_<id>.pt
```

`explain.py` saves results to `explanations/` and `explain_attention.py` to `explanations/attention/`; `explain_model.py` prints its results.

---

## 🧪 Testing

```bash
pytest
```

The test suite covers the data module, preprocessing pipeline, multiprocessing, regularization, checkpoint resume, and spectrogram processing. The data module, pipeline, and multiprocessing tests need the raw and processed data (`data/raw/`, `data/processed/`); `test_regularization.py` and `test_spectrogram_preprocessing.py` run without it.

---

## 💻 Hardware Notes

- Training was developed on H200 / RTX-class GPUs with **BF16 mixed precision**.
- Preprocessing is CPU-bound and benefits from `build_workers` set to your physical core count.
- Recommended: ≥ 16 GB RAM for preprocessing, ≥ 1 modern CUDA GPU for training.

---

## 📎 Citation

If you use AlphaHMS in your research or build upon it, please cite this repository:

```bibtex
@software{kgpal2025alphahms,
  author       = {Denis Krylov and Samuel Goldie and Alberto Pasinato and Serkan Akin and Leonardo Lago},
  title        = {{AlphaHMS}: Multi-modal Graph Neural Networks for Harmful Brain Activity Classification},
  year         = {2025},
  institution  = {Delft University of Technology},
  url          = {https://github.com/denskrlv/AlphaHMS},
  note         = {Built for the HMS Harmful Brain Activity Classification challenge (Kaggle)}
}
```

---

## 📄 License

Released under the [MIT License](LICENSE).
