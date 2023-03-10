"""
Created on Tue Apr 30 18:33:40 2019

@author: MuteTunic
"""

import pandas as pd # data analysis toolkit - create, read, update, delete datasets

import numpy as np #matrix math

from sklearn.model_selection import train_test_split #to split out training and testing data 

#keras is a high level wrapper on top of tensorflow (machine learning library)

#The Sequential container is a linear stack of layers

from keras.models import Sequential

#popular optimization strategy that uses gradient descent 

from keras.optimizers import Adam

#to save our model periodically as checkpoints for loading later

from keras.callbacks import ModelCheckpoint

#what types of layers do we want our model to have?

from keras.layers import Lambda, Conv2D, MaxPooling2D, Dropout, Dense, Flatten

import argparse
import os

np.random.seed(0)

def load_data(args):

    data_df = pd.read_csv(os.path.join(os.getcwd(), args.data_dir, 'driving_log.csv'), names=['center', 'left', 'right', 'steering', 'throttle', 'reverse', 'speed'])

    X = data_df[['center', 'left', 'right']].values
    y = data_df['steering'].values
    X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=args.test_size, random_state=0)

    return X_train, X_valid, y_train, y_valid


def build_model(args):

    model = Sequential()
    model.add(Lambda(lambda x: x/127.5-1.0, input_shape=INPUT_SHAPE))
    model.add(Conv2D(24, 5, 5, activation='elu', subsample=(2, 2)))
    model.add(Conv2D(36, 5, 5, activation='elu', subsample=(2, 2)))
    model.add(Conv2D(48, 5, 5, activation='elu', subsample=(2, 2)))
    model.add(Conv2D(64, 3, 3, activation='elu'))
    model.add(Conv2D(64, 3, 3, activation='elu'))
    model.add(Dropout(args.keep_prob))
    model.add(Flatten())
    model.add(Dense(100, activation='elu'))
    model.add(Dense(50, activation='elu'))
    model.add(Dense(10, activation='elu'))
    model.add(Dense(1))
    model.summary()

    return model


def train_model(model, args, X_train, X_valid, y_train, y_valid):

    checkpoint = ModelCheckpoint('model-{epoch:03d}.h5',monitor='val_loss',verbose=0,save_best_only=args.save_best_only,mode='auto')

    model.compile(loss='mean_squared_error', optimizer=Adam(lr=args.learning_rate))

    model.fit_generator(batch_generator(args.data_dir, X_train, y_train, args.batch_size, True),args.samples_per_epoch,args.nb_epoch,max_q_size=1,validation_data=batch_generator(args.data_dir, X_valid, y_valid, args.batch_size, False),nb_val_samples=len(X_valid),callbacks=[checkpoint],verbose=1)
