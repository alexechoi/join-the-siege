# Heron Coding Challenge - File Classifier

## Overview

This repository provides a basic endpoint for classifying files based on their content and filename. It includes the ability to generate synthetic data to train a machine learning classifier on document types, deploy the classifier API, and access it via a simple frontend.

The classifier and accompanying API handle various document types, including PDFs, images, Word documents, and Excel files, using a trained model or a simple filename-based approach if content extraction fails. 

---

## Setup Instructions

### 1. Clone the Repository

```
git clone <repository_url>
cd join-the-siege
```

### 2. Python Virtual Environment and Dependencies

Set up a Python virtual environment and install dependencies.

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Synthetic Data Generation

To generate synthetic data, you can use the provided script ```generate.py``` under ```synthetic-data```. This script will generate synthetic data for various document types and save it to CSV, JSON, and TXT files. It will also train a classifier model and save it to a ```.pkl``` file in the ```models``` directory.

### Generate Synthetic Data

1. Set OpenAI API Key: If you want to generate synthetic data using OpenAI, you'll need to set the OPENAI_API_KEY environment variable. Add this key to your environment:

```
export OPENAI_API_KEY='your_openai_api_key'
```

Alternatively, you can place the key in a ```.env``` file or use a pre-trained model provided in the ```models``` directory if you do not wish to generate new data.

**2. Run the Data Generation Script:**

```
cd synthetic-data
python generate.py
```

This script will:

- Generate synthetic text data for document types like driver's license, bank statement, invoice, resume, and medical report.
- Save generated data to CSV, JSON, and TXT files.
- Train a classifier on the generated data and save the model as ```classifier_model.pkl``` in the models directory.

---

## Running the API

The Flask app exposes an API endpoint for classifying files. The app can be run locally or in a Docker container.

### Running locally
**1. Start the Flask API:**
```
python -m src.app
```

**Testing the API:**
You can test the API using ```curl```:
```
curl -X POST -F 'file=@path_to_file.pdf' http://127.0.0.1:5000/classify_file
```

### Running with Docker
To deploy the API with Docker, use the provided Dockerfile located in the ```src``` directory.

**1. Build the Docker Image:**

```docker build -t file-classifier -f src/Dockerfile .```

**2. Run the Docker Container:**

```docker run -p 8080:8080 file-classifier```

**3. Test the API in Docker:**
Use the following ```curl``` command to test the API running in Docker:

```curl -X POST -F 'file=@path_to_file.pdf' http://127.0.0.1:8080/classify_file```

---

## Frontend

The frontend is a React application that allows users to upload files and view classification results from the backend API.

### Key Features

- **File Upload**: Allows users to upload files directly from their device.
- **Spinner**: Displays a loading spinner while awaiting a response from the API.
- **Error Handling**: Provides error messages if an unsupported file type is uploaded or if the API request fails.
- **Classification Display**: Shows the classification result of the uploaded file after the API processes it.

### Setting Up the Frontend

1. **Navigate to the Frontend Directory**:

   ```shell
   cd frontend```

2. **Install Dependencies**:

    ```npm install```

3. **Run the Frontend:**:

    ```npm start```

This command starts the frontend on ```http://localhost:3000```. If needed, configure CORS in the Flask API to allow requests from the frontend.

---

## Project Structure

- `src`: Contains the backend Flask API and classifier code.
  - `app.py`: Main Flask API file.
  - `classifier.py`: Classifier logic and file classification.
- `synthetic-data`: Synthetic data generation and model training.
  - `generate.py`: Script to generate synthetic data and train the model.
- `models`: Contains pre-trained classifier model.
- `frontend`: Contains the React frontend code.

---

## Key Features

1. **Synthetic Data Generation**:
   - Use OpenAI to generate data and train a model.
   - Pre-trained model included if OpenAI API key is not available.

2. **Classifier API**:
   - Supports document classification based on content or filename.
   - Limits file types and sizes to prevent unsupported uploads.
   - Rate-limited API to prevent abuse.

3. **Frontend**:
   - Simple React frontend with file upload.
   - Spinner and error messages for better user experience.




