# -*- coding: utf-8 -*-
"""CNN.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fWf71-8bdVIEsaik_UukYboNEyLRsw88
"""

import tqdm
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
import seaborn as sns
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from keras.callbacks import ModelCheckpoint
from keras.preprocessing.image import ImageDataGenerator
from keras.layers import BatchNormalization
from keras.layers import Dropout
from keras.layers import Dense
from keras.layers import Flatten
from keras.layers import MaxPooling2D
from keras.layers import Conv2D
from keras.models import Sequential
import tensorflow as tf
import pickle
import random
import cv2
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from google.colab import files
! pip install - q kaggle
files.upload()

!nvidia-smi

!gdown - -id 1gR5-Tzr-HZicaORJEHg6uVOOcPy0YY49
!unzip rooms_dataset.zip

# Importing the libraries

# Dataset path
dataset_path = "/content/rooms_dataset"

fish_classes = os.listdir(dataset_path)
print(fish_classes)

# Storing images with their labels in a list
data = []
for fish_class in fish_classes:
    # Get all the file names
    fish_class_path = os.path.join(dataset_path, fish_class)
    fish_class_images = os.listdir(fish_class_path)
    # Add them to the list
    for image in fish_class_images:
        data.append([fish_class, os.path.join(fish_class_path, image)])

# Printing the list
print(data)

# Building a dataframe
df = pd.DataFrame(data, columns=['Fish_Class', 'Image_Path'])
print(df.head())
print()
print(df.tail())

# Checking the number of images in each class
print(df['Fish_Class'].value_counts())

# Resizing images to 75 * 75 also using tqdm for progress bar

image = []
labels = []

for i in tqdm.tqdm(range(df.shape[0])):
    img = cv2.imread(df['Image_Path'][i])
    img = cv2.resize(img, (75, 75), interpolation=cv2.INTER_AREA)
    image.append(img)
    labels.append(df['Fish_Class'][i])


# Converting the list to numpy array
image = np.array(image)
print(image.shape)


y = labels
print(y[:5])

# for y
y_labelencoder = LabelEncoder()
y = y_labelencoder.fit_transform(y)
print(y)

# Performing one hot encoding on y Output (9000, 9)
y = y.reshape(-1, 1)
onehotencoder = OneHotEncoder()
Y = onehotencoder.fit_transform(y).toarray()
print(Y.shape)


images, Y = shuffle(image, Y, random_state=1)

train_x, test_x, train_y, test_y = train_test_split(
    images, Y, test_size=0.2, random_state=1)

print(train_x.shape)
print(test_x.shape)
print(train_y.shape)
print(test_y.shape)

num_classes = 9

# architecture of the model
epochs = 20
batch_size = 32
input_shape = (75, 75, 3)

model = Sequential()
model.add(Conv2D(32, kernel_size=(3, 3),
          activation='relu', input_shape=input_shape))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(BatchNormalization())
model.add(Dropout(0.25))

model.add(Conv2D(64, kernel_size=(3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(BatchNormalization())
model.add(Dropout(0.25))

model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(BatchNormalization())
model.add(Dropout(0.25))

model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(BatchNormalization())
model.add(Dropout(0.5))

model.add(Dense(num_classes, activation='softmax'))

model.compile(loss='categorical_crossentropy',
              optimizer='adam', metrics=['accuracy'])

model.summary()

# Training the model
history = model.fit(train_x, train_y, batch_size=batch_size,
                    epochs=epochs, verbose=1, validation_data=(test_x, test_y))

# Evaluating the model
score = model.evaluate(test_x, test_y, verbose=0)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

# Predicting the model
y_pred = model.predict(test_x)
print(y_pred[:5])

# Plotting training and testing loss vs epochs
plt.plot(history.history['loss'], label='train loss')
plt.plot(history.history['val_loss'], label='val loss')
plt.legend()
plt.show()

# classification report

print(classification_report(test_y.argmax(axis=1),
      y_pred.argmax(axis=1), target_names=fish_classes))

y_pred = np.argmax(y_pred, axis=1)
y_test = np.argmax(test_y, axis=1)

cm = confusion_matrix(y_test, y_pred)
print(cm)
