from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Details
import cv2
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from pathlib import Path
import shutil
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report, r2_score
import tensorflow as tf
import os
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'index.html')

def start_video(request):
    global video_capture
    video_capture = cv2.VideoCapture(1)

    currentframe = 0
    frame_skip = 10
    current = 0
    if not os.path.exists('data'): 
        os.makedirs('data') 
    while True:
        ret, frame = video_capture.read()

        if ret:
            if currentframe % frame_skip == 0:
                name = './data/frame' + str(current) + '.jpg'
                print('Creating...' + name)
                cv2.imwrite(name, frame)
                current += 1

            currentframe += 1
        else:
            break


    video_capture.release()
    return HttpResponse("Video capturing stopped.")

def stop_video(request):
    global video_capture  # Access the global variable
    video_capture.release()
    return HttpResponse("Video capturing stopped.")


def video (request):
    return render(request, 'video.html')

def monitor (request):
    return render(request, 'monitor.html')

def selectoption(request):
    return render(request, 'selectoption.html')
    
def crack_detection(request):
    positive_dir = Path(r'C:\\Users\\abish\\OneDrive\\Desktop\\datas\\Positive')
    negative_dir = Path(r'C:\\Users\\abish\\OneDrive\\Desktop\\datas\\Negative')
    model_file = 'my_model.h5'

    def generate_df(img_dir, label):
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.tiff', '*.webp']
        file_paths = []

        for ext in image_extensions:
            file_paths.extend(img_dir.glob(ext))

        file_paths = pd.Series(file_paths, name='Filepath').astype(str)
        if len(file_paths) == 0:
            print(f"No images found in directory: {img_dir}")
            return pd.DataFrame(columns=['Filepath', 'Label'])

        labels = pd.Series(label, name='Label', index=file_paths.index)
        df = pd.concat([file_paths, labels], axis=1)

        print(df.head())
        
        return df

    positive_df = generate_df(positive_dir, 'POSITIVE')
    negative_df = generate_df(negative_dir, 'NEGATIVE')

    all_df = pd.concat([positive_df, negative_df], axis=0).sample(frac=1, random_state=1).reset_index(drop=True)
    print(all_df)
    # new 
    logger.info(all_df)
    

    train_df, test_df = train_test_split(all_df,
                                        train_size=0.7,
                                        shuffle=True,
                                        random_state=1)

    train_gen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255,
                                                            validation_split=0.2)

    test_gen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255)
    train_data = train_gen.flow_from_dataframe(train_df, 
                                            x_col='Filepath',
                                            y_col='Label',
                                            target_size=(120,120), 
                                            color_mode='rgb',
                                            class_mode='binary',
                                            batch_size=32,
                                            shuffle=True,
                                            seed=42,
                                            subset='training')


    val_data = train_gen.flow_from_dataframe(train_df, 
                                            x_col='Filepath',
                                            y_col='Label',
                                            target_size=(120,120), 
                                            color_mode='rgb',
                                            class_mode='binary',
                                            batch_size=32,
                                            shuffle=True,
                                            seed=42,
                                            subset='validation')


    test_data = test_gen.flow_from_dataframe(test_df, 
                                            x_col='Filepath',
                                            y_col='Label',
                                            target_size=(120,120), 
                                            color_mode='rgb',
                                            class_mode='binary',
                                            batch_size=32,
                                            shuffle=False,
                                            seed=42)
    print(test_data)
    # new 
    logger.info(test_data)
    def evaluate_model(model, test_data):
        
        results = model.evaluate(test_data, verbose=0)
        loss = results[0]
        accuracy = results[1]
      
        print(f'Test Loss {loss:.5f}')
          # new 
        logger.info(f'Test Loss {loss:.5f}')
        print(f'Test Accuracy {accuracy * 100:.2f} %')
          # new 
        logger.info(f'Test Accuracy {accuracy * 100:.2f} %')
        
        
        # predicted y values
        y_pred = np.squeeze((model.predict(test_data) >= 0.5).astype(int))

        y_certain = np.squeeze((model.predict(test_data)).astype(int))
        
        conf_matr = confusion_matrix(test_data.labels, y_pred)
        
        class_report = classification_report(test_data.labels, y_pred,
                                            target_names=['NEGATIVE', 'POSITIVE'])
        
        plt.figure(figsize=(6,6))
        
        sns.heatmap(conf_matr, fmt='g', annot=True, cbar=False, vmin=0, cmap='Blues')
        
        plt.xticks(ticks=np.arange(2) + 0.5, labels=['NEGATIVE', 'POSITIVE'])
        plt.yticks(ticks=np.arange(2) + 0.5, labels=['NEGATIVE', 'POSITIVE'])
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.title('Confusion Matrix')
        # plt.show()
        
        print('r2 Score : ', r2_score(test_data.labels, y_pred))
        # new 
        logger.info('r2 Score : ', r2_score(test_data.labels, y_pred))
        print()
        print('Classification Report :\n......................\n', class_report)
        # new 
        logger.info('Classification Report :\n......................\n', class_report)
        

    def test_new_data(model, dir_path, save_path):
        new_test_dir = Path(dir_path)
        df_new = generate_df(new_test_dir, 'Testing')
        
        test_data_new = test_gen.flow_from_dataframe(df_new, 
                                                    x_col='Filepath',
                                                    y_col='Label',
                                                    target_size=(120,120), 
                                                    color_mode='rgb',
                                                    batch_size=5,
                                                    shuffle=False,
                                                    seed=42)
        
        y_pred = np.squeeze((model.predict(test_data_new) >= 0.5).astype(int))
        y_certain = model.predict(test_data_new).round(6)
        
        y_out = []
        for i in y_pred:
            if i == 0:
                y_out.append('Negative (Not Crack)')
            else:
                y_out.append('Positive (Crack)')
                
        result = pd.DataFrame(np.c_[y_out, y_certain], columns=['Result', 'Confidence of being Cracked'])
        
        # Creating a new directory for cracked images
        cracked_images_dir = Path(save_path)
        cracked_images_dir.mkdir(parents=True, exist_ok=True)
        
        # Copying cracked images to the new directory
        for index, row in df_new.iterrows():
            if y_pred[index] == 1:  # If the image is predicted as cracked
                img_path = row['Filepath']
                shutil.copy(img_path, cracked_images_dir / f"cracked_{index}.jpg")
        
        return result


    if os.path.exists(model_file):
        # Load the trained model if the file exists
        loaded_model = tf.keras.models.load_model(model_file)
        evaluate_model(loaded_model, test_data)
        results = test_new_data(loaded_model, r'./data', r'./static/image/crackedimages')
        results.to_csv(r'./final_results.csv')
        # return JsonResponse({'status': 'success', 'message': 'Model evaluated successfully'})
        return redirect('showimages')
    else:
        inputs = tf.keras.Input(shape=(120,120,3))
        x = tf.keras.layers.Conv2D(filters=16, kernel_size=(3,3), activation='relu')(inputs)
        x = tf.keras.layers.MaxPool2D(pool_size=(2,2))(x)
        x = tf.keras.layers.Conv2D(filters=32, kernel_size=(3,3), activation='relu')(x)
        x = tf.keras.layers.MaxPool2D(pool_size=(2,2))(x)

        x = tf.keras.layers.GlobalAveragePooling2D()(x)
        outputs = tf.keras.layers.Dense(1, activation='sigmoid')(x)
        model = tf.keras.Model(inputs=inputs, outputs=outputs)
        model.compile(optimizer='adam',
                    loss='binary_crossentropy',
                    metrics=['accuracy'])
        model.summary()
        history = model.fit(train_data, validation_data=val_data, epochs=100, 
                        callbacks=[tf.keras.callbacks.EarlyStopping(monitor='val_loss',
                                                                    patience=3,
                                                                    restore_best_weights=True)
                                    ])
        model.save('my_model.h5')
        evaluate_model(model, test_data)
        results = test_new_data(model, r'./data', r'../static/image/crackedimages')
        results.to_csv(r'./final_results.csv')
        fig = px.line(history.history,
                    y=['loss', 'val_loss'],
                    labels={'index':'Epoch'},
                    title='Training and Validation Loss over Time')

        fig.show()
        # return JsonResponse({'status': 'success', 'message': 'Model trained successfully'})
        return redirect('showimages')
    return HttpResponse("Model file does not exist or an error occurred.")

def corrosion_detection(request):
    positive_dir = Path(r'C:\\Users\\abish\\OneDrive\\Desktop\\corrosion dataset\\Positive')
    negative_dir = Path(r'C:\\Users\\abish\\OneDrive\\Desktop\\corrosion dataset\\Negative')
    model_file = 'my_model_corroded.h5'

    def generate_df(img_dir, label):
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.tiff', '*.webp']
        file_paths = []

        for ext in image_extensions:
            file_paths.extend(img_dir.glob(ext))

        file_paths = pd.Series(file_paths, name='Filepath').astype(str)
        if len(file_paths) == 0:
            print(f"No images found in directory: {img_dir}")
            return pd.DataFrame(columns=['Filepath', 'Label'])

        labels = pd.Series(label, name='Label', index=file_paths.index)
        df = pd.concat([file_paths, labels], axis=1)

        # Debugging: Print the DataFrame to check its structure
        print(df.head())
        
        return df

    positive_df = generate_df(positive_dir, 'POSITIVE')
    negative_df = generate_df(negative_dir, 'NEGATIVE')

    # concatenate both positive and negative df
    all_df = pd.concat([positive_df, negative_df], axis=0).sample(frac=1, random_state=1).reset_index(drop=True)
    print(all_df)
    train_df, test_df = train_test_split(all_df,
                                        train_size=0.7,
                                        shuffle=True,
                                        random_state=1)

    train_gen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255,
                                                            validation_split=0.2)

    test_gen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255)
    train_data = train_gen.flow_from_dataframe(train_df, 
                                            x_col='Filepath',
                                            y_col='Label',
                                            target_size=(120,120), 
                                            color_mode='rgb',
                                            class_mode='binary',
                                            batch_size=32,
                                            shuffle=True,
                                            seed=42,
                                            subset='training')


    val_data = train_gen.flow_from_dataframe(train_df, 
                                            x_col='Filepath',
                                            y_col='Label',
                                            target_size=(120,120), 
                                            color_mode='rgb',
                                            class_mode='binary',
                                            batch_size=32,
                                            shuffle=True,
                                            seed=42,
                                            subset='validation')


    test_data = test_gen.flow_from_dataframe(test_df, 
                                            x_col='Filepath',
                                            y_col='Label',
                                            target_size=(120,120), 
                                            color_mode='rgb',
                                            class_mode='binary',
                                            batch_size=32,
                                            shuffle=False,
                                            seed=42)
    print(test_data)

    def evaluate_model(model, test_data):
        
        results = model.evaluate(test_data, verbose=0)
        loss = results[0]
        accuracy = results[1]
        
        print(f'Test Loss {loss:.5f}')
        print(f'Test Accuracy {accuracy * 100:.2f} %')
        
        
        # predicted y values
        y_pred = np.squeeze((model.predict(test_data) >= 0.5).astype(int))

        y_certain = np.squeeze((model.predict(test_data)).astype(int))
        
        conf_matr = confusion_matrix(test_data.labels, y_pred)
        
        class_report = classification_report(test_data.labels, y_pred,
                                            target_names=['NEGATIVE', 'POSITIVE'])
        
        plt.figure(figsize=(6,6))
        
        sns.heatmap(conf_matr, fmt='g', annot=True, cbar=False, vmin=0, cmap='Blues')
        
        plt.xticks(ticks=np.arange(2) + 0.5, labels=['NEGATIVE', 'POSITIVE'])
        plt.yticks(ticks=np.arange(2) + 0.5, labels=['NEGATIVE', 'POSITIVE'])
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.title('Confusion Matrix')
        # plt.show()
        
        print('r2 Score : ', r2_score(test_data.labels, y_pred))
        print()
        print('Classification Report :\n......................\n', class_report)
        

    def test_new_data(model, dir_path, save_path):
        new_test_dir = Path(dir_path)
        df_new = generate_df(new_test_dir, 'Testing')
        
        test_data_new = test_gen.flow_from_dataframe(df_new, 
                                                    x_col='Filepath',
                                                    y_col='Label',
                                                    target_size=(120,120), 
                                                    color_mode='rgb',
                                                    batch_size=5,
                                                    shuffle=False,
                                                    seed=42)
        
        y_pred = np.squeeze((model.predict(test_data_new) >= 0.5).astype(int))
        y_certain = model.predict(test_data_new).round(6)
        
        y_out = []
        for i in y_pred:
            if i == 0:
                y_out.append('Negative (No Corrosion)')
            else:
                y_out.append('Positive (Corroded)')
                
        result = pd.DataFrame(np.c_[y_out, y_certain], columns=['Result', 'Confidence of being Corroded'])
        
        # Creating a new directory for Corroded images
        corroded_image_dir = Path(save_path)
        corroded_image_dir.mkdir(parents=True, exist_ok=True)
        
        # Copying Corroded images to the new directory
        for index, row in df_new.iterrows():
            if y_pred[index] == 1:  # If the image is predicted as Corroded
                img_path = row['Filepath']
                shutil.copy(img_path, corroded_image_dir / f"corroded_{index}.jpg")
        
        return result


    if os.path.exists(model_file):
        # Load the trained model if the file exists
        loaded_model = tf.keras.models.load_model(model_file)
        evaluate_model(loaded_model, test_data)
        results = test_new_data(loaded_model, r'./data', r'./static/image/corrodedimages')
        results.to_csv(r'./corroded_results.csv')
        return redirect('showcorrodedimages')
    else:
        inputs = tf.keras.Input(shape=(120,120,3))
        x = tf.keras.layers.Conv2D(filters=16, kernel_size=(3,3), activation='relu')(inputs)
        x = tf.keras.layers.MaxPool2D(pool_size=(2,2))(x)
        x = tf.keras.layers.Conv2D(filters=32, kernel_size=(3,3), activation='relu')(x)
        x = tf.keras.layers.MaxPool2D(pool_size=(2,2))(x)

        x = tf.keras.layers.GlobalAveragePooling2D()(x)
        outputs = tf.keras.layers.Dense(1, activation='sigmoid')(x)
        model = tf.keras.Model(inputs=inputs, outputs=outputs)
        model.compile(optimizer='adam',
                    loss='binary_crossentropy',
                    metrics=['accuracy'])
        # print model summary
        model.summary()
        history = model.fit(train_data, validation_data=val_data, epochs=100, 
                        callbacks=[tf.keras.callbacks.EarlyStopping(monitor='val_loss',
                                                                    patience=3,
                                                                    restore_best_weights=True)
                                    ])
        model.save('my_model_corroded.h5')
        evaluate_model(model, test_data)
        results = test_new_data(model, r'./data', r'./static/image/corrodedimages')
        results.to_csv(r'./corroded_results.csv')
        fig = px.line(history.history,
                    y=['loss', 'val_loss'],
                    labels={'index':'Epoch'},
                    title='Training and Validation Loss over Time')

        fig.show()
        return redirect('showcorrodedimages')
    return HttpResponse("Model file does not exist or an error occurred.")

    
def showimages(request):
    def get_image_names(directory):
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')  
        image_names = []

        for filename in os.listdir(directory):
            if filename.lower().endswith(image_extensions):
                image_names.append(filename)

        return image_names
    directory = './static/image/crackedimages'
    image_names = get_image_names(directory)
    return render(request, 'showimages.html',  {'my_list': image_names})

def showcorrodedimages(request):
    def get_image_names(directory):
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')  
        image_names = []

        for filename in os.listdir(directory):
            if filename.lower().endswith(image_extensions):
                image_names.append(filename)

        return image_names
    directory = './static/image/corrodedimages'
    image_names = get_image_names(directory)
    return render(request, 'showcorrodedimages.html',  {'my_list': image_names})
# def index(request):
#     return render(request, 'index.html')

# def video(request):
#     cam = cv2.VideoCapture(0) 
#     try: 
#         if not os.path.exists('data'): 
#             os.makedirs('data') 
#     except OSError: 
#         print('Error: Creating directory of data') 

#     currentframe = 0
#     frame_skip = 30 
#     current = 232
#     while True: 
#         ret, frame = cam.read() 

#         if ret: 
#             if currentframe % frame_skip == 0: 
#                 name = './data/frame' + str(current) + '.jpg'
#                 print('Creating...' + name)
#                 cv2.imwrite(name, frame) 
#                 current+=1
            
#             currentframe += 1
#         else: 
#             break
#     cam.release() 
#     return render(request, 'video.html')

# Import necessary modules and functions...