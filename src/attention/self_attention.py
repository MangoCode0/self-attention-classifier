
import math

import torch
import torch.nn as nn
import torch.nn.functional as F


class GeneTokenEmbedding(nn.Module):
    """Convert each gene's expression value into a 32-dimensional token."""

    def __init__(self, embed_dim: int = 32):
        super().__init__()
        self.projection = nn.Linear(1, embed_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Input: (batch_size, num_genes)
        x = x.unsqueeze(-1)

        # Output: (batch_size, num_genes, embed_dim)
        return self.projection(x)


class SelfAttention(nn.Module):
    """Scaled dot-product self-attention."""

    def __init__(self, embed_dim: int = 32):
        super().__init__()

        self.query = nn.Linear(embed_dim, embed_dim)
        self.key = nn.Linear(embed_dim, embed_dim)
        self.value = nn.Linear(embed_dim, embed_dim)

        self.scale = math.sqrt(embed_dim)

    def forward(self, x: torch.Tensor):
        # x: (batch_size, num_tokens, embed_dim)

        Q = self.query(x)
        K = self.key(x)
        V = self.value(x)

        # Calculate attention scores between tokens.
        scores = torch.matmul(Q, K.transpose(-2, -1))
        scores = scores / self.scale

        # Normalize attention scores.
        attention_weights = F.softmax(scores, dim=-1)

        # Combine token representations using attention weights.
        output = torch.matmul(attention_weights, V)

        return output, attention_weights


if __name__ == "__main__":
    torch.manual_seed(42)

    batch_size = 2
    num_genes = 500
    embed_dim = 32

    x = torch.randn(batch_size, num_genes)

    embedding = GeneTokenEmbedding(embed_dim=embed_dim)
    attention = SelfAttention(embed_dim=embed_dim)

    tokens = embedding(x)
    output, weights = attention(tokens)

    print("Input shape:", tuple(x.shape))
    print("Embedded tokens:", tuple(tokens.shape))
    print("Attention output:", tuple(output.shape))
    print("Attention weights:", tuple(weights.shape))

    assert tokens.shape == (2, 500, 32)
    assert output.shape == (2, 500, 32)
    assert weights.shape == (2, 500, 500)

    # Each row of attention weights should sum to approximately 1.
    assert torch.allclose(
        weights.sum(dim=-1),
        torch.ones(2, 500),
        atol=1e-5,
    )

    print("Self-attention component test passed.")
