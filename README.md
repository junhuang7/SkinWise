
# SkinWise: A Web-Based Diagnostic Tool for Skin Cancer Detection

## Introduction
SkinWise revolutionizes the approach to skin cancer detection, particularly melanoma, by incorporating advanced machine learning models and FHIR standards. It empowers healthcare professionals with precise, real-time diagnostic suggestions.

## Features
- **Advanced Machine Learning Model**: Leverages the Skin Cancer ISIC dataset for top-notch accuracy.
- **FHIR Integration**: Guarantees efficient data interoperability within healthcare systems.
- **User-Friendly Interface**: Offers a straightforward process for uploading and analyzing skin lesion images.
- **Real-Time Diagnostic Suggestions**: Immediate, insightful diagnostic feedback for healthcare professionals.

## Getting Started

### Prerequisites
- Python 3.12.1
- Flask
- PyTorch/TensorFlow/Keras
- Streamlit
- Deta
- A web browser

### Installation
1. Secure a copy of the repository on your local machine.
   ```
   git clone https://github.gatech.edu/jhuang709/SkinWise.git
   ```
2. Set up the necessary dependencies.
   ```
   pip install -r requirements.txt
   ```
3. Ready the database.
   ```
   flask db upgrade
   ```
4. Activate the Flask app.
   ```
   flask run
   ```
5. Utilize a web browser to explore SkinWise at `http://127.0.0.1:5000/`.

### Running with Docker
1. Build the Docker image from the project directory:
   ```
   docker build -t skinwise .
   ```
2. Run the container:
   ```
   docker run -p 8501:8501 skinwise
   ```
3. Access SkinWise through your web browser at `http://localhost:8501`.

## Usage
Explore various functionalities like data uploading for analysis, viewing results, and accessing historical data on the user dashboard.

## Contributing
Contributions are welcome. To contribute, fork the repository, create your feature branch, commit your changes, push to the branch, and initiate a pull request.

## License
SkinWise is under the MIT License.

## Contact
- Jun Huang - [email](mailto:jhuang709@gatech.edu)
- Zhiqiu Jiang - [email](mailto:zjiang88@gatech.edu)
- Zifeng Zhang - [email](mailto:zzhang3138@gatech.edu)

## Acknowledgments
- Skin Cancer ISIC Dataset
- Fast Healthcare Interoperability Resources (FHIR)
