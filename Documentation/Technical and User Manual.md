
# SkinWise: A Web-Based Diagnostic Tool for Skin Cancer Detection

## Introduction
SkinWise is a web application that offers a significant advantage in the early detection of skin cancer, including melanoma, through advanced machine learning models. It integrates with FHIR to provide healthcare professionals with real-time diagnostic suggestions based on the analysis of skin lesion images.

## Features
- **Advanced Machine Learning Model**: Built using a convolutional neural network trained on the ISIC dataset for accurate prediction of skin cancer types.
- **FHIR Integration**: Seamlessly manage patient information with real-time synchronization to the HAPI FHIR public server for interoperability with healthcare systems.
- **User-Friendly Interface**: Designed with Streamlit for ease of use, enabling quick uploading and analysis of images.
- **Real-Time Diagnostic Suggestions**: Provides immediate, AI-driven diagnostic feedback.

## Installation & Setup
1. Clone the repository to your local machine
   ```
   git clone https://github.gatech.edu/jhuang709/SkinWise.git
   ```
2. Install the required dependencies using `pip install -r requirements.txt`.
   ```
   streamlit==1.32.2
   streamlit_option_menu==0.3.12
   fhirclient==4.1.0
   flask==3.0.3
   opencv-python==4.9.0.80
   tensorflow==2.16.1
   ```
3. Start the Streamlit application using `streamlit run app.py`.
4. Access the application through `http://localhost:8501` in your browser.

## Running with Docker
- Build the Docker image using `docker build -t skinwise .`
- Run the Docker container using `docker run -p 8501:8501 skinwise`.

## Web deployment on AWS
- **Address**: We also deployed our application on AWS, which you can access through this link: [http://ec2-13-60-53-97.eu-north-1.compute.amazonaws.com:8501/](http://ec2-13-60-53-97.eu-north-1.compute.amazonaws.com:8501/)

## Functionality
- **Data Entry**: Enter patient data manually and save to the FHIR server.
- **Image Analysis**: Upload skin lesion images and receive AI-driven diagnostic predictions, some test images can be found in https://github.gatech.edu/jhuang709/SkinWise/tree/main/test_images
- **Patient Management**: View and manage patient information fetched from the FHIR server, with CRUD operations.
- **Condition Management**: Add and update medical conditions of patients on the FHIR server.

## CRUD Operations with HAPI FHIR Server
- **Create**: Add new patient data along with conditions to the FHIR server.
- **Read**: Fetch patient information and related medical conditions from the FHIR server.
- **Update**: Modify patient data and their conditions on the FHIR server.
- **Delete**: Remove patient records and associated data from the FHIR server.

## Contributing
Contributions are welcome. Please fork the repository, create your feature branch, commit your changes, and open a pull request.

## Contact
- Jun Huang - [jhuang709@gatech.edu](mailto:jhuang709@gatech.edu)
- Zhiqiu Jiang - [zjiang88@gatech.edu](mailto:zjiang88@gatech.edu)
- Zifeng Zhang - [zzhang3138@gatech.edu](mailto:zzhang3138@gatech.edu)

## Acknowledgments
- Skin Cancer ISIC Dataset
- HAPI FHIR public server
- Streamlit
- TensorFlow
