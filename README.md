# 🩺 Differential Diagnosis

**Differential Diagnosis** is a full-stack web application that predicts potential diseases based on user-reported symptoms. Built with Flask, Python, JavaScript, and CSS, the platform integrates a machine learning model to deliver real-time diagnostic feedback and allows users to maintain a personal history of illnesses. The app features secure login functionality to ensure data privacy and personalized access.

**Link to Demo:** [Link](https://youtu.be/ra71DG-NXfE)

## 🚀 Features

- **Symptom-Based Disease Prediction**  
  Users enter their symptoms into a simple interface. These are processed by a trained XGBoost machine learning model to return a probable disease.

- **Custom Disease Information Rendering**  
  Based on the diagnosis, custom templates are dynamically rendered with relevant information about the predicted disease.

- **User Health History Tracker**  
  Logged-in users can add previous illnesses and view a timeline of their personal diagnosis history, including dates.

- **Secure Authentication**  
  Includes sign-up/login functionality with hashed passwords and secure session management to protect sensitive user data.

## 🧠 Machine Learning Integration

The disease prediction engine is powered by an **XGBoost classifier** trained on the [Disease Prediction Dataset](https://www.kaggle.com/datasets/kaushil268/disease-prediction-using-machine-learning) from Kaggle. The model maps user symptoms to potential diseases with high accuracy and is seamlessly integrated into the Flask backend to deliver real-time results.

## 👥 Team Contributions

- **Vishnu**  
  Led the team, built the machine learning model, integrated the Flask backend, and implemented the health history tracking feature.

- **Zong**  
  Contributed extensively to Flask development and created most of the disease templates diisplayed after diagnosing the user.

- **Shushant**  
  Led the frontend design and styling using CSS and assisted in building informative templates for each disease.

## 🔐 Security Highlights

- Password hashing for secure user authentication
- Structure built to support scalability and future enhancements

## 💡 Future Enhancements

- Expand dataset coverage to include more diseases and symptoms  
- Improve the machine learning model 
- Improve the disease templates  
- Enable multi-language support for accessibility

---

> Built by **Vishnu**, **Zong**, and **Shushant**
