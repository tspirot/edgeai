"""Обележја из претренираног CNN-а (torchvision) — јаче, али тражи PyTorch.

Узима излаз средњег слоја (нпр. layer2 ResNet-18) као мапу обележја и своди је
на G×G мрежу — исти облик као ручни екстрактор, па остатак ланца не зна разлику.
"""

from __future__ import annotations

import numpy as np

from qc.features.base import BlockFeatures, FeatureExtractor


class TorchExtractor(FeatureExtractor):
    def __init__(self, cfg) -> None:  # pragma: no cover - тешка зависност
        import torch
        import torchvision

        self.cfg = cfg
        self.torch = torch
        weights = torchvision.models.ResNet18_Weights.DEFAULT
        model = torchvision.models.resnet18(weights=weights)
        self.stem = torch.nn.Sequential(
            model.conv1, model.bn1, model.relu, model.maxpool, model.layer1, model.layer2
        ).eval()
        self.preprocess = weights.transforms()

    def extract(self, image) -> BlockFeatures:  # pragma: no cover - тешка зависност
        import torch
        from PIL import Image

        img = Image.fromarray(np.asarray(image).astype("uint8"))
        x = self.preprocess(img).unsqueeze(0)
        with torch.no_grad():
            feat = self.stem(x)[0]  # (C, H, W)
        g = self.cfg.grid
        pooled = torch.nn.functional.adaptive_avg_pool2d(feat.unsqueeze(0), (g, g))[0]
        vecs = pooled.permute(1, 2, 0).reshape(g * g, -1).numpy().astype("float32")
        return BlockFeatures(vectors=vecs, grid=g)
