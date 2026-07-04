# Hybrid Machine Learning Model for Efficient Botnet Attack Detection in IoT Environment
This project implements a machine learning-based system designed to detect botnet attacks in Internet of Things (IoT) network environments. The system analyzes network traffic data and classifies it as normal or malicious traffic.

## Project Description
The project uses multiple machine learning models to analyze IoT network traffic and detect suspicious botnet activities. The dataset is preprocessed by removing duplicate and missing values, encoding categorical features, balancing the data, and scaling network traffic features.
Multiple classification models are trained and their accuracy is compared to identify the best-performing model. The trained model is used to predict whether the network traffic represents normal activity or a botnet attack.

## Machine Learning Models
- Logistic Regression
- Random Forest
- Support Vector Machine (SVM)
- Ensemble Technique
- Artificial Neural Network (ANN)

## Key Features
- IoT network traffic analysis
- Botnet attack detection
- Data preprocessing and class balancing
- Multiple machine learning model training
- Model accuracy comparison
- Best model identification
- Normal and malicious traffic classification
- Risk level prediction
- Security recommendations

## System Modules
- **Admin Module:** Uploads and manages the IoT network traffic dataset.
- **Model Builder Module:** Preprocesses data, trains machine learning models, compares accuracy, and identifies the best model.
- **User Module:** Allows users to enter network traffic data and receive botnet attack predictions.

## Prediction
The trained model analyzes the network traffic features entered by the user and classifies the activity as:
- **Normal Traffic**
- **Botnet Attack**
The system also provides the risk level and security recommendations based on the prediction result.

## Result Analysis
The application generates pie charts and bar charts to visualize the number of normal traffic predictions and detected botnet attacks.

## Conclusion
This project demonstrates the application of machine learning and neural networks for efficient botnet attack detection in IoT environments. By training and comparing multiple models, the system provides an effective approach for identifying malicious network traffic and analyzing potential security threats.
