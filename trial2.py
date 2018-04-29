# Author: Yotam Cohen
# An Achtung learning agent using Keras-CNTK tools.
from keras.models import Sequential
from keras.layers import Activation, Input, AlphaDropout, MaxPooling2D, Dense, Flatten, Conv2D, Add, Concatenate, TimeDistributed, LeakyReLU, BatchNormalization
from keras.optimizers import Adam, SGD
from keras.models import Model
from keras.utils import plot_model
from keras.callbacks import CSVLogger
from keras.preprocessing.sequence import TimeseriesGenerator
import numpy as np
from collections import deque
import random
from PyGamePlayer.pygame_player import PyGamePlayer
from pygame.constants import K_a, K_d
import cv2
import Achtung
import keyboard_interaction
import keras.backend as K
import cntk
import pygame
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from time import time

VK_KEY_A = 0x41
VK_KEY_D = 0x44
VK_LEFT = 0x25
VK_RIGHT = 0x27

np.set_printoptions(threshold='nan', linewidth=np.nan)
BATCH_SIZE = 256
img_rows , img_cols = 200,200
img_channels = 4  # four greyscale frames

class DQNAgent():
    # A Deep Q-Learning agent
    def __init__(self, state_size, hidden_sizes, action_size):
        # Agent constructor
        self.state_size = state_size  # input layer size
        self.hidden_sizes = hidden_sizes  # hidden layer size
        self.action_size = action_size  # output layer size
        self.memory = deque(maxlen=2500)  # output history
        self.gamma = 0.9  # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.1
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()
        self.epoch = 0
        with open('plot1.csv', 'wb') as f:
            f.write('epoch,loss\n')

    def _build_model(self):
        # Neural Net for Deep Q-Learning model
        input1 = Input(shape=(img_channels,img_rows,img_cols))
        
        model1 = Conv2D(32, (8, 8), strides=(4, 4), data_format='channels_first', padding='valid')(input1)  #128*128*4
        #model1 = BatchNormalization()(model1)
        model1 = Activation('relu')(model1)
        model1 = Conv2D(64, (4, 4), strides=(2, 2), data_format='channels_first', padding='valid')(model1)
        #model1 = BatchNormalization()(model1)
        model1 = Activation('relu')(model1)
        model1 = Conv2D(64, (3, 3), strides=(1, 1), data_format='channels_first', padding='valid')(model1)
        #model1 = BatchNormalization()(model1)
        model1 = Activation('relu')(model1)
        model1 = Flatten()(model1)
        
        model1 = Dense(256)(model1)
        #model1 = BatchNormalization()(model1)
        model1 = Activation('relu')(model1)
        model1 = Dense(self.action_size)(model1)
        #model1 = BatchNormalization()(model1)
        outputs = Activation('softmax')(model1)
        
        final = Model(inputs=input1, outputs=outputs)  # [input1, input2, input3]
        #model.add(Dense(8, activation='relu'))
        final.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        return final

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        act_values = self.model.predict(state)
        print "act_values:", act_values
        return np.argmax(act_values[0])

    def replay(self, batch_size):
        print "replaying"
        minibatch = random.sample(self.memory, batch_size)
        f = open('plot1.csv', 'a')
        states = []
        targets = []
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * np.amax(self.model.predict(next_state)[0])
            target_f = self.model.predict(state)
            target_f[0][action] = target
            states.append(state)
            targets.append(target_f)

        states = np.asarray(states).reshape(batch_size,img_channels,img_rows,img_cols)
        targets = np.asarray(targets).reshape(batch_size,self.action_size)
        history = self.model.train_on_batch(states, targets)
        print history
        f.write(str(self.epoch) + ',' + str(history) + '\n')
        self.epoch += 1
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        f.close()

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)
   

class AchtungPlayer(PyGamePlayer):
    def __init__(self, state_size, hidden_sizes, action_size, key1, key2):
        super(AchtungPlayer, self).__init__(force_game_fps=300, run_real_time=True)
        self.agent = DQNAgent(state_size, hidden_sizes, action_size)
        self._last_state = None
        self._last_action = 0
        self.my_color = (255, 0, 0, 0.9)
        self.key1 = key1
        self.key2 = key2
        self.state = []
        self.epochs = 0
        self.position = (0,0)

    def find_my_player(self):
        for player in Achtung.alive:
            if player.get_color() == self.my_color:
                return player
        return None


    def get_viewpoint(self, screen_array, pos_x, pos_y):
        min_row = max(pos_y - 100, 0)
        max_row = min(min_row + 200, 720)
        min_row = max(max_row - 200, 0)
        min_col = max(pos_x - 100, 0)
        max_col = min(min_col + 200, 1080)
        min_col = max(max_col - 200, 0)
        return screen_array[min_col:max_col,min_row:max_row]


    def get_keys_pressed(self, screen_array, reward, terminal):
        """
        screen_array = pygame.map_array(pygame.display.get_surface(), screen_array)
        game_map = game_map.flatten()
        game_map[game_map > 0] = 1
        """
        screen_array = cv2.cvtColor(screen_array, cv2.COLOR_BGR2GRAY)
        # set the pixels to all be 0. or 1.
        _, screen_array = cv2.threshold(screen_array, 0, 1, cv2.THRESH_BINARY)

        
        
        player = self.find_my_player()
        if player is not None:
            for i,j in player.mask_outline:
                try:
                    screen_array[i, j] = 0.5
                except:
                    continue
            self.position = player.rect.center
            player_map = self.get_viewpoint(screen_array, self.position[0], self.position[1])
            """
            my_rect = pygame.Rect(min_col, min_row, 200, 200)
            pygame.draw.rect(pygame.display.get_surface(), self.my_color, my_rect, 2)
            """
        else:
            print "dead"
            player_map = self.get_viewpoint(screen_array, self.position[0], self.position[1])

        game_map = player_map
        #game_map = game_map.reshape(img_rows,img_cols)
        self.state.append(game_map)
        #print game_map
        #quit()
        
        """
        if(not terminal):
            player = self.find_my_player()
            position = np.array([player.get_pos()[0], player.get_pos()[1]]).astype(np.float32)  # adds the x-position of the player
            position = position.reshape(1,2,)
            angle = np.array([player.get_angle()]).astype(np.float32)  # adds the direction of the player
            angle = angle.reshape(1,1,)
        else:
            position = np.array([-1,-1]).astype(np.float32).reshape((1,2,))
            angle = np.array([-1]).astype(np.float32).reshape((1,1,))
        """
        # frame_time = self.get_game_time_ms(None) / self.get_ms_per_frame(None)
        if not terminal:
            if len(self.state) == img_channels:
                # The entire segment above prepares the data for the network
                self.state = np.asarray([self.state], dtype=np.float32)  # .reshape(1,frames,img_rows,img_cols,img_channels)
                final_input = self.state  # [self.state, position, angle]
                if self._last_state is None:
                    # if this is the first-to-fourth frame
                    self._last_state = final_input
                    if self._last_action != 2:
                        keyboard_interaction.PressKey(self._key_presses_from_action3(self._last_action))
                    self.state = []  # np.zeros((frames, img_cols, img_rows, img_channels))
                    
                    return self._key_presses_from_action(self._last_action)
                # Now it can't be the first frame, so we use it to train
                # print self.state
                self.agent.remember(self._last_state, self._last_action, reward, final_input, terminal)
                
                action = self.agent.act(final_input)
                print "{} action: ".format(self.key1), action, "epsilon:", self.agent.epsilon
                if action != 2:
                    keyboard_interaction.ReleaseKey(self._key_presses_from_action3(self._last_action))
                else:
                    keyboard_interaction.ReleaseKey(self.key1)
                    keyboard_interaction.ReleaseKey(self.key2)
                self._last_action = action
                if action != 2:
                    keyboard_interaction.PressKey(self._key_presses_from_action3(action))
                self.state = []  # np.zeros((frames, img_cols, img_rows, img_channels))
                
                return self._key_presses_from_action(action)
            # else
            
            return self._key_presses_from_action(self._last_action)
        else:
            self.epochs+=1
            if len(self.state) == img_channels:
                del(self.state[0])
            if len(self.agent.memory) > BATCH_SIZE:
                # every 60 frames, learn from your actions
                self.agent.replay(BATCH_SIZE)
                if self.epochs % 100 == 0:
                    self.agent.save(".\\save\\{}-checkpoint-{}.h5".format(self.key1, self.epochs))
            
            return self._key_presses_from_action(self._last_action)
        

    def get_feedback(self):
        player = self.find_my_player()
        if player is None:
            return (0, True)
        return (-1, False)
        

    @staticmethod
    def _key_presses_from_action(action):
        if action == 0:
            return [K_a]
        if action == 1:
            return [K_d]
        return []
    
    def _key_presses_from_action3(self, action):
        if action == 0:
            return self.key1
        if action == 1:
            return self.key2
        return 7


        


def main():
    # init env and the agent
    my_player = AchtungPlayer(1, [3], 3, VK_KEY_A, VK_KEY_D)
    plot_model(my_player.agent.model, to_file='model.png')
    #my_other_player = AchtungPlayer(1,[3], 2, VK_LEFT, VK_RIGHT)
    #my_player.agent.load(".\\save\\65-checkpoint-2680.h5")
    my_player.start()
    #my_other_player.start()
    Achtung.main()
"""
    # advance the game to the next frame based on the action
    # reward is 1 for every frame the pole survived
    next_state, reward, done, _ = env.step(action)
    reward = reward if not done else -10
    next_state = np.reshape(next_state, [1,4])

    xd

    # Remember the previous stats
    agent.remember(state, action, reward, next_state, done)

    # make next state the new current state
    state = next_state

    # done becomes True when the game ends
    if done:
        print("episode {}/{}, score: {}, e: {:.2}".format(e, episodes, t, agent.epsilon))
        break

    # train the agent with the experience of the episode
    if len(agent.memory) > batch_size:
        agent.replay(batch_size)
"""
if __name__ == "__main__":
    main()
