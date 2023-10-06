import os
import numpy as np
import tensorflow as tf
import json
from tensorflow.keras.layers import Conv1D, Dropout, BatchNormalization, Flatten, Dense, AveragePooling1D, MaxPooling1D, LSTM, Lambda, Input, Bidirectional, GlobalAveragePooling1D, GlobalMaxPooling1D
import pickle
from tensorflow.keras.optimizers import Adam, SGD, Adagrad
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
import matplotlib.pyplot as plt
from keras.callbacks import EarlyStopping

import shutil
from keras import regularizers, Model


# mkan el folder elly 3mlna fe save ll features
TRAIN_DATA_PATH = os.path.join('MP_Train')
TEST_DATA_PATH = os.path.join('MP_Test')
VAL_DATA_PATH = os.path.join('MP_Val')
MAIN_DATA_PATH = TRAIN_DATA_PATH  # no longer have mp data new

LABEL_MAP_PATH = os.path.join('label_map.json')

MIN_VIDEOS = 10  # minimum number of videos for each action
FRAMES_PER_VIDEO = 30  # number of frames per video (wont be changed)


def load_features(actions, label_map: dict, data_type: str = "train") -> tuple:
    """
    This function loads the features from the npy files and returns them as numpy arrays,
    it also saves the features as npy files for future use
    """
    allowed_data_types = ['train', 'test', 'val']
    if data_type not in allowed_data_types:
        raise ValueError(
            f"Invalid value for 'param', allowed values are: {allowed_data_types}")
    data_path = TRAIN_DATA_PATH
    if data_type == "train":
        data_path = TRAIN_DATA_PATH
    elif data_type == "test":
        data_path = TEST_DATA_PATH
    elif data_type == "val":
        data_path = VAL_DATA_PATH
    if os.path.exists(f'x_{data_type}.npy') and os.path.exists(f'y_{data_type}.npy'):
        x = np.load(f'x_{data_type}.npy', allow_pickle=True)
        y = np.load(f'y_{data_type}.npy', allow_pickle=True)
        return x, y
    sequences, labels = [], []
    for action in actions:
        for sequence in os.listdir(os.path.join(data_path, action)):
            res = np.load(os.path.join(data_path, action, sequence))
            sequences.append(res)
            labels.append(label_map[action])
    sequences, labels = np.array(sequences), to_categorical(labels).astype(int)
    np.save(f'x_{data_type}.npy', sequences)
    np.save(f'y_{data_type}.npy', labels)
    return sequences, labels


def build_model(actions):
    multi = 1
    tf.random.set_seed(42)

    model = Sequential()
    model.add(Conv1D(512*multi, kernel_size=2, activation='elu',
              input_shape=(FRAMES_PER_VIDEO, 126)))
    model.add(BatchNormalization())
    model.add(AveragePooling1D(pool_size=2))
    model.add(Dropout(0.5, seed=42))

    model.add(Conv1D(256*multi, kernel_size=2, activation='elu',
              kernel_regularizer=tf.keras.regularizers.l2(l=0.01)))
    model.add(BatchNormalization())
    model.add(AveragePooling1D(pool_size=2))
    model.add(Dropout(0.5, seed=42))

    model.add(Conv1D(128*multi, kernel_size=2, activation='elu'))
    model.add(BatchNormalization())
    model.add(AveragePooling1D(pool_size=2))
    model.add(Dropout(0.5, seed=42))

    model.add(Flatten())

    model.add(Dense(512*multi, activation='elu',
              kernel_regularizer=tf.keras.regularizers.l2(l=0.01)))
    # model.add(Dropout(0.5, seed=42))
    model.add(Dense(512*multi, activation='elu',
              kernel_regularizer=tf.keras.regularizers.l2(l=0.01)))
    model.add(Dropout(0.5, seed=42))
    model.add(Dense(actions.shape[0], activation='softmax'))
    opt = Adam(learning_rate=0.0001)

    model.compile(optimizer=opt, loss='categorical_crossentropy',
                  metrics=['categorical_accuracy', 'accuracy'])

    # model.load_weights('./models/action1.04-accuracy0.74.h5')
    return model


def train_model(model, X_train, y_train, X_val, y_val, batch_size=16):

    early_stopping = EarlyStopping(monitor='val_loss', patience=30)
    tensorboard = tf.keras.callbacks.TensorBoard(
        log_dir=os.path.join("logs", 'test'))

    checkpoint = tf.keras.callbacks.ModelCheckpoint(
        f'./models/best_model{batch_size}.h5', monitor='val_accuracy', verbose=1,
        save_best_only=True, mode='max', save_freq='epoch', save_weights_only=False
    )

    callbacks_list = [checkpoint, tensorboard, early_stopping]
    history = model.fit(X_train, y_train, epochs=1000, batch_size=batch_size,
                        validation_data=(X_val, y_val), verbose=1, callbacks=callbacks_list,  use_multiprocessing=True)
    return history


def show_test_results(model, X_test, y_test):
    if model is None or X_test is None or y_test is None:
        raise Exception("model, X_test and y_test must be given")

    # Show results
    y_pred = model.predict(X_test)
    y_pred = np.argmax(y_pred, axis=1)
    y_test = np.argmax(y_test, axis=1)
    test_accuracy = 100 * np.sum(y_pred == y_test)/y_test.shape[0]
    print("Test Accuracy: {:.2f}%".format(
        test_accuracy))

    return test_accuracy


def get_word(word):

    synonym_map = {}
    with open(os.path.join('MS-ASL', "MSASL_synonym.json")) as f:
        data = json.load(f)
        for synonym in data:
            synonym_map[synonym[0]] = synonym
    word = word.lower()
    word = word.split("/")[0]
    word = word.replace("-", " ")
    word = word.replace("#", "")
    for key, value in synonym_map.items():
        if word in value:
            return key
    return word


def main():
    actions = []
    actions_count = {}
    limit = 0
    actions = os.listdir(MAIN_DATA_PATH)
    actions = np.array(actions)

    # # load label map from json file
    # with open(LABEL_MAP_PATH) as fp:
    #     label_map = json.load(fp)

    # {"0":"action1", "1":"action2", "2":"action3"}

    # actions = np.array(list(label_map.values()))
    print("we have {} actions".format(actions.shape[0]))

    label_map = {label: num for num, label in enumerate(actions)}

    print("label map: ", label_map)

    # delete the old json file if exists
    if os.path.exists(LABEL_MAP_PATH):
        os.remove(LABEL_MAP_PATH)

    # save label map into json file reversed and
    with open(LABEL_MAP_PATH, 'w') as fp:
        json.dump({v: k for k, v in label_map.items()}, fp)

    # load x_test and y_test and x_val and y_val and x_train and y_train

    X_train, y_train = load_features(actions, label_map, data_type='train')
    X_test, y_test = load_features(actions, label_map, data_type='test')
    X_val, y_val = load_features(actions, label_map, data_type='val')
    print("loaded x_test, y_test, x_val, y_val, x_train, y_train")

    # get the actions from the y_val

    batch_sizes = [
        # 32,
        # 16,
        # 8,
        # 4,
        # 2,

        # actions.shape[0]
        # 20,
        # actions.shape[0]//2,
        actions.shape[0]//4
        # # actions.shape[0]*4,
        # actions.shape[0]*2,
        # 2
    ]

    # sort the batch sizes
    batch_sizes.sort(reverse=True)
    batch_sizes_info = {}

    max_accuracy = 0
    average_accuracy = 0

    for batch_size in batch_sizes:
        model = build_model(actions)

        history = train_model(model, X_train, y_train,
                              X_val, y_val, batch_size=batch_size)
        # save the history to a file using pickle
        with open(f'history{batch_size}.pkl', 'wb') as f:
            pickle.dump(history.history, f)

        model.load_weights(f"./models/best_model{batch_size}.h5")

        del X_train
        del y_train
        del X_val
        del y_val
        # accuracy = show_test_results(model, X_test, y_test)
        X_test, y_test = load_features(actions, label_map, data_type='test')
        loss, categorical_accuracy, accuracy = model.evaluate(
            X_test, y_test, verbose=1)

        # 2 floating point precision
        accuracy = round(accuracy, 2)
        categorical_accuracy = round(categorical_accuracy, 2)
        loss = round(loss, 2)
        # save loss and accuracy to batch_sizes_info
        batch_info = {
            "loss": loss,
            "categorical_accuracy": categorical_accuracy,
            "accuracy": accuracy,
            "batch_size": batch_size
        }
        batch_sizes_info[batch_size] = batch_info
        if accuracy > max_accuracy:
            max_accuracy = accuracy
        average_accuracy += accuracy

    average_accuracy /= len(batch_sizes)

    print(
        f"batch_sizes_info: {batch_sizes_info} max_accuracy: {max_accuracy} average_accuracy: {average_accuracy}")

    return batch_sizes_info, max_accuracy, average_accuracy


if __name__ == '__main__':
    main()
