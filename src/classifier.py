import logging
import os
import pickle
from werkzeug.datastructures import FileStorage

# Configure logging at the module level
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the classifier and vectorizer at the module level
MODEL_PATH = './models/classifier_model.pkl'
try:
    with open(MODEL_PATH, 'rb') as model_file:
        classifier, vectorizer = pickle.load(model_file)
    logging.info(f"Classifier model and vectorizer loaded from '{MODEL_PATH}'.")
except Exception as e:
    logging.exception(f"Failed to load classifier model and vectorizer: {e}")
    classifier = None
    vectorizer = None

def classify_file(file: FileStorage):
    """
    Classifies the uploaded file based on its content using ensemble methods.

    Parameters:
    - file: The uploaded file.

    Returns:
    - A string indicating the class of the file.
    """

    try:
        filename = file.filename.lower()
        file_extension = os.path.splitext(filename)[1]

        # Allowed file extensions
        ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg', '.docx', '.xlsx', '.txt'}

        if file_extension not in ALLOWED_EXTENSIONS:
            logging.error(f"Unsupported file extension: {file_extension}")
            return "unsupported file type"

        def extract_text(file, file_extension):
            text = ''
            if file_extension in ['.png', '.jpg', '.jpeg']:
                try:
                    from PIL import Image
                    import pytesseract

                    image = Image.open(file.stream)
                    text = pytesseract.image_to_string(image)
                    logging.debug(f"Extracted text from image: {text[:100]}...")
                except ImportError:
                    logging.error("pytesseract or PIL not installed. Cannot extract text from images.")
                except Exception as e:
                    logging.error(f"OCR extraction failed: {e}")
            elif file_extension == '.pdf':
                try:
                    from pdfminer.high_level import extract_text as extract_pdf_text
                    # Save the file to a temporary file
                    import tempfile

                    with tempfile.NamedTemporaryFile(delete=True, suffix='.pdf') as tmp_file:
                        file.seek(0)
                        tmp_file.write(file.read())
                        tmp_file.flush()
                        text = extract_pdf_text(tmp_file.name)
                    logging.debug(f"Extracted text from PDF: {text[:100]}...")
                except ImportError:
                    logging.error("pdfminer.six not installed. Cannot extract text from PDFs.")
                except Exception as e:
                    logging.error(f"PDF text extraction failed: {e}")
            elif file_extension == '.docx':
                try:
                    import docx2txt
                    import tempfile

                    with tempfile.NamedTemporaryFile(delete=True, suffix='.docx') as tmp_file:
                        file.seek(0)
                        tmp_file.write(file.read())
                        tmp_file.flush()
                        text = docx2txt.process(tmp_file.name)
                    logging.debug(f"Extracted text from DOCX: {text[:100]}...")
                except ImportError:
                    logging.error("docx2txt not installed. Cannot extract text from DOCX files.")
                except Exception as e:
                    logging.error(f"DOCX text extraction failed: {e}")
            elif file_extension == '.xlsx':
                try:
                    import pandas as pd
                    file.seek(0)
                    df = pd.read_excel(file)
                    text = df.to_string()
                    logging.debug(f"Extracted text from XLSX: {text[:100]}...")
                except ImportError:
                    logging.error("pandas not installed. Cannot extract text from XLSX files.")
                except Exception as e:
                    logging.error(f"XLSX text extraction failed: {e}")
            elif file_extension == '.txt':
                try:
                    file.seek(0)
                    text = file.read().decode('utf-8', errors='ignore')
                    logging.debug(f"Extracted text from TXT: {text[:100]}...")
                except Exception as e:
                    logging.error(f"TXT file read failed: {e}")
            else:
                logging.error(f"Unsupported file extension: {file_extension}")

            return text

        # Initialize a list to hold possible predictions
        predictions = []

        # Extract text from the file
        text = extract_text(file, file_extension)

        # For non-image files, use text-based classifier
        if file_extension not in ['.png', '.jpg', '.jpeg']:
            if text:
                logging.debug("Text extraction succeeded.")
                if classifier is not None and vectorizer is not None:
                    # Preprocess and vectorize the extracted text
                    text_vector = vectorizer.transform([text])

                    # Predict the classification of the text
                    predicted_class = classifier.predict(text_vector)[0]
                    predictions.append(predicted_class)
                    logging.info(f"Text-based classifier predicted: '{predicted_class}'")
                else:
                    logging.warning("Classifier or vectorizer not available for text classification.")
            else:
                logging.warning("No text extracted from the file.")
        else:
            logging.info("Skipping text-based classifier for image files.")

        # Filename-based classification (should always be attempted)
        filename_based_class = filename_classification(filename)
        if filename_based_class:
            predictions.append(filename_based_class)
            logging.info(f"Filename-based classification predicted: '{filename_based_class}'")
        else:
            logging.debug("Filename-based classification did not match any class.")

        # Keyword-based classification
        keyword_based_class = keyword_classification(text)
        if keyword_based_class:
            predictions.append(keyword_based_class)
            logging.info(f"Keyword-based classification predicted: '{keyword_based_class}'")
        else:
            logging.debug("Keyword-based classification did not match any class.")

        # Aggregate predictions
        if predictions:
            from collections import Counter
            prediction_counts = Counter(predictions)
            final_prediction = prediction_counts.most_common(1)[0][0]
            logging.info(f"Final predicted class for '{filename}': '{final_prediction}'")
            return final_prediction
        else:
            logging.info(f"Could not classify file '{filename}'.")
            return "unknown file"

    except Exception as e:
        logging.exception(f"An error occurred during classification: {e}")
        return "error during classification"

def filename_classification(filename):
    """
    Classify based on keywords in the filename.
    """
    filename_lower = filename.lower()
    filename_keywords = {
        'drivers_license': ['driver_license', 'drivers_license', 'driver_licence', 'drivers_licence', 'dl', 'license', 'licence'],
        'bank_statement': ['bank_statement', 'statement', 'bank'],
        'invoice': ['invoice', 'bill', 'receipt'],
        'resume': ['resume', 'cv'],
        'medical_report': ['medical', 'report'],
    }
    for class_name, keywords in filename_keywords.items():
        for keyword in keywords:
            if keyword in filename_lower:
                logging.debug(f"Filename keyword '{keyword}' matched for class '{class_name}'.")
                return class_name
    logging.debug("No filename keywords matched.")
    return None

def keyword_classification(text):
    """
    Classify based on keywords in the text content.
    """
    if not text:
        return None
    text_lower = text.lower()
    classification_keywords = {
        'drivers_license': ["driver's license", "drivers license", "driver licence", "driver's licence"],
        'bank_statement': ["bank statement", "account summary", "account balance"],
        'invoice': ["invoice", "bill", "statement of account", "amount due"],
        'resume': ['resume', 'curriculum vitae', 'cv', 'education', 'experience'],
        'medical_report': ['medical', 'diagnosis', 'treatment', 'patient', 'physician', 'health'],
    }
    for class_name, keywords in classification_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                logging.debug(f"Text keyword '{keyword}' matched for class '{class_name}'.")
                return class_name
    logging.debug("No text keywords matched.")
    return None