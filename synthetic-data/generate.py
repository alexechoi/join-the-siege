import os
import pandas as pd
import numpy as np
import pickle
import logging
from tqdm import tqdm  # Progress bar
from openai import OpenAI  # Updated import for OpenAI client

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set OpenAI API key - retrieve from environment variables
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Generate synthetic data
def generate_synthetic_data(prompt, n_samples=50):
    responses = []
    for _ in tqdm(range(n_samples), desc=f"Generating samples for '{prompt[:15]}...'"):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            n=1,
            temperature=0.7
        )
        text = response.choices[0].message.content.strip()
        responses.append(text)
    return responses

# Define prompts for different document classes
prompts = {
    'drivers_license': 'Generate the text content of a realistic driver\'s license, including typical fields like name, address, date of birth, license number, and expiration date.',
    'bank_statement': 'Generate a realistic bank statement summary, including account holder information, transactions, balances, and dates.',
    'invoice': 'Generate the text of a typical invoice, including seller information, buyer information, itemized charges, total amount due, and due date.',
    'resume': 'Generate the text of a professional resume, including sections like summary, experience, education, and skills.',
    'medical_report': 'Generate a realistic medical report, including patient information, diagnosis, treatment plan, and physician notes.'
}

# Generate synthetic data for each class
data = []
for label, prompt in prompts.items():
    logging.info(f"Generating data for class: {label}")
    texts = generate_synthetic_data(prompt, n_samples=50)
    for text in texts:
        data.append({'text': text, 'label': label})

# Create a DataFrame
df = pd.DataFrame(data)

# Save data to CSV
df.to_csv('synthetic_data.csv', index=False)
logging.info("Synthetic data saved to 'synthetic_data.csv'.")

# Save data to TXT (one document per line)
with open('synthetic_data.txt', 'w') as f:
    for index, row in df.iterrows():
        f.write(f"__label__{row['label']} {row['text']}\n")
logging.info("Synthetic data saved to 'synthetic_data.txt'.")

# Optionally, save data to JSON
df.to_json('synthetic_data.json', orient='records', lines=True)
logging.info("Synthetic data saved to 'synthetic_data.json'.")

# --- Training a Classifier ---

# Split data into features and labels
X = df['text']
y = df['label']

# Convert text data to numerical features using TF-IDF vectorization
vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
X_vectors = vectorizer.fit_transform(X)

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X_vectors, y, test_size=0.2, random_state=42, stratify=y
)

# Initialize and train the classifier
classifier = LogisticRegression(max_iter=1000)
classifier.fit(X_train, y_train)
logging.info("Classifier training completed.")

# Save the classifier model to a .pkl file
with open('../models/classifier_model.pkl', 'wb') as model_file:
    pickle.dump((classifier, vectorizer), model_file)
logging.info("Classifier model saved as '../models/classifier_model.pkl'.")

# Evaluate the classifier
y_pred = classifier.predict(X_test)
logging.info("\nClassification Report:\n%s", classification_report(y_test, y_pred))