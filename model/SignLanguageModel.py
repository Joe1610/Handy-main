import tensorflow as tf
from tensorflow.keras.layers import Conv1D, Dropout, BatchNormalization, Flatten, Dense, AveragePooling1D
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import Sequential
from numpy import ndarray
import os


class SignLanguageModel:
    def __init__(self, actions: ndarray, frames_per_video: int = 100, seed: int = 42, multi: int = 1) -> None:
        self.actions = actions
        self.frames_per_video = frames_per_video
        self.seed = seed
        self.multi = multi
        self.build_model()
       
        

    def build_model(self) -> None:
        tf.random.set_seed(self.seed)

        self.model = Sequential()
        self.model.add(Conv1D(512*self.multi, kernel_size=2, activation='elu',
                              input_shape=(self.frames_per_video, 126)))
        self.model.add(BatchNormalization())
        self.model.add(AveragePooling1D(pool_size=2))
        self.model.add(Dropout(0.5, seed=self.seed))

        self.model.add(Conv1D(256*self.multi, kernel_size=2, activation='elu'))
        self.model.add(BatchNormalization())
        self.model.add(AveragePooling1D(pool_size=2))
        self.model.add(Dropout(0.5, seed=self.seed))

        self.model.add(Conv1D(128*self.multi, kernel_size=2, activation='elu'))
        self.model.add(BatchNormalization())
        self.model.add(AveragePooling1D(pool_size=2))
        self.model.add(Dropout(0.5, seed=self.seed))

        self.model.add(Flatten())

        self.model.add(Dense(512*self.multi, activation='elu'))
        self.model.add(Dense(512*self.multi, activation='elu'))
        self.model.add(Dropout(0.5, seed=self.seed))
        self.model.add(Dense(len(self.actions), activation='softmax'))
        opt = Adam(learning_rate=0.0001)

        self.model.compile(optimizer=opt, loss='categorical_crossentropy',
                           metrics=['categorical_accuracy', 'accuracy'])
        

    def train(self, X_train, y_train, X_val, y_val, batch_size=16,epochs=1000):
        early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=300)
        tensorboard = tf.keras.callbacks.TensorBoard(
            log_dir=os.path.join("logs", 'test'))
        
        checkpoint = tf.keras.callbacks.ModelCheckpoint(
            './models/best_model.h5', monitor='val_accuracy', verbose=1,
            save_best_only=True, mode='max', save_freq='epoch', save_weights_only=False
        )

        callbacks_list = [checkpoint, tensorboard, early_stopping]
        self.history = self.model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size,
                            validation_data=(X_val, y_val), verbose=1, callbacks=callbacks_list,  use_multiprocessing=True)
        return self.history
    
    