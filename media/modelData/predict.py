#!/usr/bin/python

from ast import arguments
from pickle import NONE
import sys
import os
import json
# from cv2 import imshow
# import itertools
# import shutil
# import random
# import shap
import matplotlib.cm as cm
import cv2 as cv
import tensorflow as tf
from tensorflow import keras
# from keras import backend as K
# from keras.layers import Dense, Activation,Reshape, Dropout
# from keras.optimizers import Adam
# from keras.metrics import categorical_crossentropy
# from keras.preprocessing.image import ImageDataGenerator
from keras.preprocessing import image
# from keras.models import Model
# from keras.applications import imagenet_utils
from keras.models import load_model
# from sklearn import preprocessing

# from sklearn.metrics import confusion_matrix
# from sklearn.metrics import classification_report

import numpy as np
import pandas as pd 
# from glob import glob
import matplotlib.pyplot as plt

from mobilenet import *

# results = {
#     "saliency" : NONE,
#     "gradcam" : NONE,
#     "gradcampp" : NONE,
#     "prediction" :NONE,
#     "accuracy": NONE,
#     "result" : NONE

# }
results = {
    "files":[],
    "prediction" :NONE,
    "accuracy": NONE,
    "result" : NONE

}
model = load_model('model.h5')
arguments = list(sys.argv)
load_image = keras.preprocessing.image.load_img(arguments[2],grayscale=False,
    color_mode='rgb',
    target_size=(224,224),
    keep_aspect_ratio=False
)

input_image = keras.preprocessing.image.img_to_array(load_image)
input_image = keras.preprocessing.image.img_to_array(load_image)
input_image = keras.applications.mobilenet.preprocess_input(input_image)
# print(input_image.shape)
input_arr = np.array([input_image])
y_pred = model.predict(input_arr)

classes = ["Tomato___Bacterial_spot", "Tomato___healthy", "Tomato___Late_blight", "Tomato___Septoria_leaf_spot","Tomato___Tomato_Yellow_Leaf_Curl_Virus"]
# ction => ", classes[np.argmax(y_pred)], "\naccuracy => ",str(round(y_pred[0][np.argmax(y_pred)]*100,2))+"%", "\npredictions => ",y_pred)


os.chdir(arguments[3])

print("prediction => ", classes[np.argmax(y_pred)], "\naccuracy => ",str(round(y_pred[0][np.argmax(y_pred)]*100,2))+"%", "\npredictions => ",y_pred)
print("ok8")

# Data to be written
results["prediction"] = str(classes[np.argmax(y_pred)])
results["accuracy"] = str(round(y_pred[0][np.argmax(y_pred)]*100,2))+"%"
results["result"] =  str(y_pred)

# ---------------------------------------------------------------
# saliency map
# ---------------------------------------------------------------
unmapped_image = vanila_saliencymap(model, classes, input_image)
# vanila_image = cv.applyColorMap(unmapped_image, cv.COLORMAP_JET)
plt.clf()
fig, axes = plt.subplots(1,2,figsize=(14,5))
axes[0].imshow(load_image)
i = axes[1].imshow(unmapped_image,cmap="jet",alpha=0.8)
fig.colorbar(i)
fig.savefig("vanila_"+str(os.path.basename(arguments[2])))
results["files"].append("vanila_"+str(os.path.basename(arguments[2])))
# plt.imsave("vanila_" + str(os.path.basename(arguments[2])), unmapped_image, cmap="jet")
plt.clf()
# plt.imsave("vanila_" + str(os.path.basename(arguments[2])),vanila_image)

# ---------------------------------------------------------------
# gradcam
# ---------------------------------------------------------------
fig, axes = plt.subplots(1,2,figsize=(14,5))
axes[0].imshow(load_image)
grad_matrix = gradcam( model, input_image)
i =axes[1].imshow(grad_matrix)
fig.colorbar(i)
fig.savefig("gradcam_"+str(os.path.basename(arguments[2])))
results["files"].append("gradcam_"+str(os.path.basename(arguments[2])))
plt.clf()

# ---------------------------------------------------------------
# gradcam++
# ---------------------------------------------------------------
fig, axes = plt.subplots(1,2,figsize=(14,5))
axes[0].imshow(load_image)
grad_matrix = gradcam_pp( model, input_image)
i = axes[1].imshow(grad_matrix)
fig.colorbar(i)
fig.savefig("gradcam++_"+str(os.path.basename(arguments[2])))
results["files"].append("gradcam++_"+str(os.path.basename(arguments[2])))
plt.clf()

# ---------------------------------------------------------------
# gradcam++
# ---------------------------------------------------------------
plt.clf()
shap_values = shaply(input_arr, classes,model)
shap.image_plot(shap_values,show = False)
plt.savefig("shap_"+str(os.path.basename(arguments[2])))
results["files"].append("shap_"+str(os.path.basename(arguments[2])))

plt.clf




print(results)
# Serializing json 
json_object = json.dumps(results)

  
# Writing to sample.json
with open("result.json", "w") as outfile:
    outfile.write(json_object)



