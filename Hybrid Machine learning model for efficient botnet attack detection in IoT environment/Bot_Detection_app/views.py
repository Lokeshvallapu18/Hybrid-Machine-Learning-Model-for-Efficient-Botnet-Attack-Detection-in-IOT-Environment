from django.shortcuts import render
import pymysql
import pandas as pd
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.utils import resample
from sklearn.metrics import accuracy_score, r2_score, mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
# Create your views here.
def index(request):
    return render(request, 'index.html')


def admin_login(request):
    return render(request,'admin/admin_login.html')


def admin_login_action(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    if username =='Admin' and password == 'Admin':
        return render(request,'admin/admin_home.html')
    else:
        context = {'data':'Login Failed..!'}
        return render(request,'admin/admin_login.html',context)


def admin_home(request):
    return render(request,'admin/admin_home.html')


def logout(request):
    return render(request,'index.html')


def upload_dataset(request):
    return render(request,'admin/upload_dataset.html')


global df
def upload_dataset_action(request):
    global df
    if request.method == 'POST':
        filename = request.FILES['dataset']
        df = pd.read_csv(filename)

        columns = df.columns.tolist()
        records = df.head(5).values.tolist()
        context = {
            'msg': 'Dataset uploaded successfully..!',
            'columns': columns,
            'records': records
        }
        return render(request, 'admin/upload_dataset.html', context)


def model_builder_login(request):
    return render(request,'model_builder/model_builder_login.html')


def model_builder_login_action(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    if username =='Admin' and password == 'Admin':
        return render(request,'model_builder/model_builder_home.html')
    else:
        context = {'data':'Login Failed..!'}
        return render(request,'model_builder/model_builder_login.html',context)


def model_builder_home(request):
    return render(request,'model_builder/,model_builder_home.html')


def user_registration(request):
    return render(request,'user/user_registration.html')

def user_registration_action(request):
    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']
    confirm_password = request.POST['confirm_password']
    if password != confirm_password:
        context = {'msg':'Password and Confirm Password are not same'}
        return render(request,'user_registration.html',context)
    

    con = pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="Bot_Detection",
        charset="utf8"
    )
    
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE username=%s or email=%s",(username,email))
    existing_user = cur.fetchone()

    if existing_user:
        con.close()
        return render(request,'user/user_registration.html',{'msg':'Username or Email already exist..!'})
    cur.execute("INSERT INTO users (username,email,password) VALUES (%s,%s,%s)",(username,email,password))

    con.commit()
    con.close()

    return render(request,'user/user_registration.html',{'msg':'Registration successful..!'})
    
def user_login(request):
    return render(request,'user/user_login.html')

def user_login_action(request):
    username = request.POST['username']
    password = request.POST['password']

    con = pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="Bot_Detection",
        charset="utf8"
    )
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE username=%s AND password=%s",(username,password))
    user = cur.fetchone()
    con.close()

    if user:
        return render(request,'user/user_home.html',{'username':'useraname'})
    else:
        return render(request,'user/user_login.html',{'msg':'Invalid Username or Password'})
    
def user_home(request):
    return render(request,'user/user_home.html')
DATASET_PATH = "dataset/iot_botnet_attack_detection_dataset.csv"
MODEL_DIR = "model"

SCALER_PATH = "model/scaler_X.joblib"
CLASSIFIER_PATH = "model/bot_classifier.h5"

def preprocess(request):

    df = pd.read_csv(DATASET_PATH)

    # Remove null & duplicates
    df = df.dropna()
    df = df.drop_duplicates()

    # Encode categorical column
    df = pd.get_dummies(df, columns=["protocol_type"])

    # Convert label
    df["botnet_attack"] = df["botnet_attack"].map({
        "Normal": 0,
        "Attack": 1
    })

    preview_html = df.head(20).to_html(
        classes="table table-bordered table-striped",
        index=False
    )

    return render(request, "model_builder/preprocess.html", {
        "msg": "Preprocessing Completed Successfully!",
        "preview": preview_html
    })
def build_model(request):

    df = pd.read_csv(DATASET_PATH)

    # ---------- Encoding ----------
    df = pd.get_dummies(df, columns=["protocol_type"])

    df["botnet_attack"] = df["botnet_attack"].map({
        "Normal": 0,
        "Attack": 1
    })

    X = df.drop(columns=["botnet_attack"])
    y = df["botnet_attack"]

    # ---------- Balance Dataset ----------
    df_balanced = pd.concat([X, y], axis=1)

    majority = df_balanced[df_balanced.botnet_attack == 0]
    minority = df_balanced[df_balanced.botnet_attack == 1]

    minority_upsampled = resample(
        minority,
        replace=True,
        n_samples=len(majority),
        random_state=42
    )

    df_balanced = pd.concat([majority, minority_upsampled])

    X_balanced = df_balanced.drop(columns=["botnet_attack"])
    y_balanced = df_balanced["botnet_attack"]

    # ---------- Train Test Split ----------
    X_train, X_test, y_train, y_test = train_test_split(
        X_balanced, y_balanced,
        test_size=0.2,
        random_state=42
    )

    # ---------- Scaling ----------
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(scaler, SCALER_PATH)

    results = {}

    # ================= Logistic Regression =================
    lr = LogisticRegression(max_iter=500)
    lr.fit(X_train_scaled, y_train)
    lr_acc = accuracy_score(y_test, lr.predict(X_test_scaled))
    results["Logistic Regression"] = round(lr_acc * 100, 2)
    joblib.dump(lr, os.path.join(MODEL_DIR, "logistic_model.pkl"))

    # ================= Random Forest =================
    rf = RandomForestClassifier(n_estimators=300, random_state=42)
    rf.fit(X_train, y_train)
    rf_acc = accuracy_score(y_test, rf.predict(X_test))
    results["Random Forest"] = round(rf_acc * 100, 2)
    joblib.dump(rf, os.path.join(MODEL_DIR, "rf_model.pkl"))

    # ================= SVM =================
    svm = SVC(kernel="rbf", probability=True)
    svm.fit(X_train_scaled, y_train)
    svm_acc = accuracy_score(y_test, svm.predict(X_test_scaled))
    results["SVM"] = round(svm_acc * 100, 2)
    joblib.dump(svm, os.path.join(MODEL_DIR, "svm_model.pkl"))

    # ================= XGBoost =================
    xgb = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        eval_metric="logloss"
    )
    xgb.fit(X_train, y_train)
    xgb_acc = accuracy_score(y_test, xgb.predict(X_test))
    results["XGBoost"] = round(xgb_acc * 100, 2)
    joblib.dump(xgb, os.path.join(MODEL_DIR, "xgb_model.pkl"))

    # ================= ANN =================
    ann = Sequential([
        Dense(128, activation='relu', input_shape=(X_train_scaled.shape[1],)),
        Dropout(0.3),
        Dense(64, activation='relu'),
        Dropout(0.2),
        Dense(1, activation='sigmoid')
    ])

    ann.compile(
        optimizer=Adam(0.001),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )

    ann.fit(X_train_scaled, y_train, epochs=30, batch_size=32, verbose=0)

    ann_pred = (ann.predict(X_test_scaled) > 0.5).astype(int)
    ann_acc = accuracy_score(y_test, ann_pred)

    ann.save(CLASSIFIER_PATH)
    results["Neural Network (ANN)"] = round(ann_acc * 100, 2)

    # ---------- Best Model ----------
    best_model_name = max(results, key=results.get)
    best_accuracy = results[best_model_name]

    return render(request, "model_builder/build_model.html", {
        "msg": "All Models Trained Successfully!",
        "results": results,
        "best_model": best_model_name,
        "best_accuracy": best_accuracy
    })
ENCODERS_PATH = "model/encoders.pkl"
SCALER_PATH = "model/scaler_X.joblib"
CLASSIFIER_PATH = "model/fraud_classifier.h5"
REGRESSOR_PATH = "model/anomaly_regressor.h5"
def enter_test_data(request):

    if request.method == "POST":
        try:

            form_data = {
                "device_id": float(request.POST.get("device_id")),
                "packet_size": float(request.POST.get("packet_size")),
                "packet_rate": float(request.POST.get("packet_rate")),
                "connection_duration": float(request.POST.get("connection_duration")),
                "source_port": float(request.POST.get("source_port")),
                "destination_port": float(request.POST.get("destination_port")),
                "failed_login_attempts": float(request.POST.get("failed_login_attempts")),
                "traffic_volume": float(request.POST.get("traffic_volume")),
                "cpu_usage": float(request.POST.get("cpu_usage")),
                "memory_usage": float(request.POST.get("memory_usage")),
                "anomaly_score": float(request.POST.get("anomaly_score")),
                "protocol_type_TCP": float(request.POST.get("protocol_type_TCP")),
                "protocol_type_UDP": float(request.POST.get("protocol_type_UDP")),
                "protocol_type_ICMP": float(request.POST.get("protocol_type_ICMP")),
            }

            # Convert to dataframe
            input_df = pd.DataFrame([form_data])

            # Load scaler
            scaler = joblib.load(SCALER_PATH)
            X_scaled = scaler.transform(input_df)

            # Load ANN model
            classifier = load_model(CLASSIFIER_PATH)

            # Prediction
            pred_value = classifier.predict(X_scaled)[0][0]
            pred = 1 if pred_value >= 0.5 else 0

            # ================= RESULT & RECOMMENDATIONS =================

            if pred == 1:
                status = "BOTNET ATTACK DETECTED 🚨"
                risk_level = "HIGH RISK"

                recommendation = [
                    "Immediately isolate the IoT device from the network.",
                    "Block suspicious IP addresses using firewall rules.",
                    "Reset device credentials and enable strong authentication.",
                    "Update firmware to latest security patch.",
                    "Monitor network traffic continuously for anomalies."
                ]

            else:
                status = "NORMAL TRAFFIC ✅"
                risk_level = "LOW RISK"

                recommendation = [
                    "Device behavior appears normal.",
                    "Maintain regular firmware updates.",
                    "Enable intrusion detection monitoring.",
                    "Use secure communication protocols.",
                    "Perform periodic security audits."
                ]

            return render(request, "user/enter_test_data.html", {
                "msg": "Detection Completed Successfully!",
                "bot_status": status,
                "risk_level": risk_level,
                "recommendations": recommendation,
                "input_data": form_data
            })

        except Exception as e:
            return render(request, "user/enter_test_data.html", {
                "error": str(e)
            })

    return render(request, "user/enter_test_data.html")
import matplotlib.pyplot as plt
from django.conf import settings
import uuid
def user_analysis(request):

    df = pd.read_csv(DATASET_PATH)

    df["botnet_attack"] = df["botnet_attack"].map({
        "Normal": 0,
        "Attack": 1
    })

    attack_counts = df["botnet_attack"].value_counts()

    labels = ["Normal Traffic", "Botnet Attack"]
    values = [attack_counts.get(0, 0), attack_counts.get(1, 0)]

    graph_path = os.path.join(settings.MEDIA_ROOT, "analysis")
    os.makedirs(graph_path, exist_ok=True)

    unique_id = uuid.uuid4().hex

    # PIE
    pie_file = f"pie_{unique_id}.png"
    plt.figure()
    plt.pie(values, labels=labels, autopct="%1.1f%%")
    plt.title("IoT Traffic Distribution")
    plt.savefig(os.path.join(graph_path, pie_file))
    plt.close()

    # BAR
    bar_file = f"bar_{unique_id}.png"
    plt.figure()
    plt.bar(labels, values)
    plt.title("Botnet Attack Count")
    plt.savefig(os.path.join(graph_path, bar_file))
    plt.close()

    return render(request, "user/analysis.html", {
        "pie_chart": f"/media/analysis/{pie_file}",
        "bar_chart": f"/media/analysis/{bar_file}",
        "normal_count": values[0],
        "attack_count": values[1],
    })