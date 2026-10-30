
import torch
import torch.nn as nn

from src.attention.self_attention import (
    GeneTokenEmbedding,
    SelfAttention,
)


class GeneExpressionAttentionClassifier(nn.Module):
    """Custom Self-Attention classifier for gene-expression data."""

    def __init__(
        self,
        num_genes=500,
        embed_dim=32,
        hidden_dim=32,
        num_classes=2,
        dropout=0.3,
    ):
        super().__init__()

        self.embedding = GeneTokenEmbedding(embed_dim=embed_dim)
        self.attention = SelfAttention(embed_dim=embed_dim)

        self.classifier = nn.Sequential(
            nn.Linear(embed_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, num_classes),
        )

    def forward(self, x):
        if x.ndim != 2:
            raise ValueError("Input must have shape (batch_size, num_genes).")

        if x.shape[1] != 500:
            raise ValueError(f"Expected 500 genes, received {x.shape[1]}.")

        tokens = self.embedding(x)
        attended, attention_weights = self.attention(tokens)
        pooled = attended.mean(dim=1)
        logits = self.classifier(pooled)

        return logits, attention_weights


if __name__ == "__main__":
    torch.manual_seed(42)

    model = GeneExpressionAttentionClassifier(
        num_genes=500,
        embed_dim=32,
        hidden_dim=32,
        num_classes=2,
        dropout=0.3,
    )

    x = torch.randn(4, 500)
    logits, weights = model(x)

    print("Logits:", tuple(logits.shape))
    print("Attention weights:", tuple(weights.shape))
    print("Trainable parameters:", sum(
        p.numel() for p in model.parameters() if p.requires_grad
    ))

    assert logits.shape == (4, 2)
    assert weights.shape == (4, 500, 500)

    print("Classifier test passed.")
