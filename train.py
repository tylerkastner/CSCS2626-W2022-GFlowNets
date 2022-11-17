import torch
import numpy as np
import yaml
import munch
import dill

from sample_trajs import generate_trajs
from networks.reward_network import RewardNetwork
from gfn.src.gfn.envs import HyperGrid
from grid import train_grid_gfn
import matplotlib.pyplot as plt
from gfn.src.gfn.distributions import (
    EmpiricalTrajectoryDistribution,
    TrajectoryBasedTerminatingStateDistribution,
    TrajectoryDistribution,
)

def train(config, env):
  all_states = env.build_grid()

  trajectories = generate_trajs(env=env, n=10)
  with open("./trajectories", "wb") as dill_file:
    dill.dump(resultstatsDF, dill_file)


  last_states = torch.cat([traj.states.states_tensor[-2] for traj in trajectories])
  last_states_one_hot = torch.nn.functional.one_hot(last_states, num_classes=config.env.height)
  last_states_grid = (last_states_one_hot[:,0,:][:,:,None] * last_states_one_hot[:,1,:][:,None]).to(torch.float32)
  last_states_grid = last_states_grid.mean(0)
  plt.matshow(last_states_grid)
  plt.title('Behavior distribution')
  plt.show()

  # # add 1 for action
  # reward_net = RewardNetwork(state_dim = state_shape + 1)

  reward_net = RewardNetwork(state_dim=env.ndim)
  reward_optimizer = torch.optim.Adam(reward_net.parameters(), lr=1e-3)

  reward_losses = []

  n_gfn_sample = 100
  #gfn_parametrization, trajectories_sampler_gfn = train_grid_gfn(config, None, reward_net=reward_net, n_train_steps=100)
  for i_traj, traj in enumerate(trajectories):
    print(i_traj)
    # states, actions = traj.states.states_tensor, torch.unsqueeze(traj.actions, -1)
    # # Remove last state in trajectory since there is no reward to predict from it
    # states = states[:-1]
    #
    # states_and_actions = torch.cat((states, actions), dim=-1)
    # states_and_actions = states_and_actions.to(torch.float32)
    #
    # rewards = reward_net(states_and_actions)
    #
    # # No average since for now there is a single trajectory in batch - to change if we increase BS
    # trajectory_reward = torch.sum(rewards)
    #
    # # This is the Z which will be learnt by GFlowNet
    # Z = 1
    #
    # loss = trajectory_reward - np.log(Z)
    # reward_optimizer.zero_grad()
    # loss.backward()
    # reward_optimizer.step()
    #
    # reward_losses.append(loss.detach())

    ####################################################################################################################
    ####################################################################################################################
    ####################################################################################################################

    states = traj.states.states_tensor
    last_state = states[-2].to(torch.float32)

    trajectory_reward = reward_net(last_state)
    all_rewards = reward_net(all_states.states_tensor.reshape(-1, config.env.ndim))
    Z = torch.mean(torch.exp(-all_rewards))
    if i_traj % 1000 == 0:
      plt.matshow(-all_rewards.reshape(config.env.height, config.env.height).detach().numpy())
      plt.title(i_traj)
      plt.show()

    # # This is the Z which will be learnt by GFlowNet
    # gfn_sample = trajectories_sampler_gfn.sample(n_gfn_sample).last_states.states_tensor.to(torch.float32)
    # gfn_Z = torch.exp(gfn_parametrization.logZ.tensor)
    # sample_likelihood = torch.exp(-reward_net(gfn_sample)).detach() / gfn_Z.detach()
    # Z = torch.mean(torch.exp(-reward_net(gfn_sample)) / sample_likelihood)

    loss = trajectory_reward + torch.log(Z)
    loss = loss.mean()
    reward_optimizer.zero_grad()
    loss.backward()
    reward_optimizer.step()

    reward_losses.append(loss.detach())

    # Fit gfn to new reward function
    #gfn_parametrization, trajectories_sampler_gfn = train_grid_gfn(config, gfn_parametrization, trajectories_sampler_gfn, reward_net=reward_net, n_train_steps=100)


if __name__ == '__main__':
  with open("config.yml", "r") as ymlfile:
    config = yaml.safe_load(ymlfile)
  config = munch.munchify(config)

  env = HyperGrid(ndim=config.env.ndim,
                  height=config.env.height,
                  R0=0.01)
  train(config, env)
