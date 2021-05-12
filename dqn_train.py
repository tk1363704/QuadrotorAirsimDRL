import gym
from gym import spaces

from airsim.AirSimClient import *
from airgym.envs.airsim_env import AirSimEnv
from airgym.envs.drone_env import AirSimDroneEnv

from stable_baselines3 import DQN
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv, VecTransposeImage
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.callbacks import EvalCallback, BaseCallback, EveryNTimesteps, CheckpointCallback

import matplotlib.pyplot as plt
from tensorboard import program
import numpy as np
import math
import time
import os

# connect to the AirSim simulator
client = MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)

env = DummyVecEnv(
    [
        lambda: Monitor(
            gym.make(
                "airgym:airsim-drone-sample-v0",
                ip_address="127.0.0.1",
                step_length=1,
                image_shape=(84, 84, 1),
                destination=np.array([0,0,0]),
            )
        )
    ]
)

# Wrap env as VecTransposeImage to allow SB to handle frame observations
env = VecTransposeImage(env)


# Initialize RL algorithm type and parameters
model = DQN(
    "CnnPolicy",
    env,
    learning_rate=0.00025,
    verbose=1,
    batch_size=32,
    train_freq=4,
    target_update_interval=200,
    learning_starts=200,
    buffer_size=10000,
    max_grad_norm=10,
    exploration_fraction=0.1,
    exploration_final_eps=0.01,
    tensorboard_log='./tb_logs/',
)


############################################# Callbacks #############################################

# eval_callback = EvalCallback(
#     env,
#     callback_on_new_best=None,
#     n_eval_episodes=5,
#     best_model_save_path="./model/",
#     log_path="./eval_log/",
#     eval_freq=500,
# )

checkpoint_callback = CheckpointCallback(save_freq=100, save_path='./checkpoint/12_May/',
                                         name_prefix='dqn_policy')


# Train for a certain number of timesteps
# model.learn(
#     total_timesteps=int(time_steps),
#     tb_log_name="dqn_" + str(time_steps) + "_time_steps",
#     reset_num_timesteps=False,
#     **kwargs
# )

time_steps = 10000 #approximately 13 hours 40 mins

model.learn(
    total_timesteps=int(time_steps),
    log_interval=5,
    tb_log_name="train_" + str(time_steps) + "_steps",
    callback=checkpoint_callback,
)

# Save policy weights
model.save("model/dqn_airsim_drone_policy")