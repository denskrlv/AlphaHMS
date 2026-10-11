"""Tests for regional pooling of EEG and spectrogram node embeddings."""

import sys
from pathlib import Path

import pytest
import torch

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.models.graph_layers.hierarchical_pooling import HierarchicalPoolingLayer

EEG_CHANNELS = [
    "Fp1", "F3", "C3", "P3", "F7", "T3", "T5", "O1", "Fz", "Cz", "Pz",
    "Fp2", "F4", "C4", "P4", "F8", "T4", "T6", "O2",
]


def test_eeg_channels_pooled_into_four_regions():
    """19 EEG channels are mean-pooled into Frontal/Central/Parietal/Occipital."""
    pool = HierarchicalPoolingLayer(channels=EEG_CHANNELS, num_regions=4)
    counts = torch.bincount(pool.channel_to_region, minlength=4)
    assert counts.tolist() == [7, 5, 5, 2]

    x = torch.randn(2, 19, 8)
    out = pool(x)
    assert out.shape == (2, 4, 8)
    occipital = [EEG_CHANNELS.index("O1"), EEG_CHANNELS.index("O2")]
    assert torch.allclose(out[:, 3], x[:, occipital].mean(dim=1))


def test_spectrogram_regions_pass_through():
    """Spectrogram nodes are already regions and must not be pooled together."""
    pool = HierarchicalPoolingLayer(channels=["LL", "RL", "LP", "RP"], num_regions=4)
    assert pool.channel_to_region is None

    x = torch.randn(2, 4, 8)
    assert torch.equal(pool(x), x)


def test_unknown_eeg_channel_raises():
    with pytest.raises(ValueError):
        HierarchicalPoolingLayer(channels=EEG_CHANNELS[:-1] + ["EKG"], num_regions=4)
