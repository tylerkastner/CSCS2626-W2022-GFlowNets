import torch.nn as nn

class RewardNetwork(nn.Module):
  def __init__(
    self,
    state_dim,
    hidden_dim1 = 128,
    out_features = 1,
  ):
    super(RewardNetwork, self).__init__()
    self.net = nn.Sequential(
      nn.Linear(state_dim, hidden_dim1),
      nn.ReLU(),
      nn.Linear(hidden_dim1, hidden_dim1),
      nn.ReLU(),
      nn.Linear(hidden_dim1, hidden_dim1),
      nn.ReLU(),
      nn.Linear(hidden_dim1, out_features),
    )
    # self.net = nn.Sequential(
    #   nn.Linear(state_dim, out_features)
    # )

  def forward(self, x):
    x = x/15 - 0.5
    return self.net(x)
