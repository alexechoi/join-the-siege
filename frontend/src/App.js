import { useState } from 'react';

function App() {
  const [file, setFile] = useState(null);
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
    setError(null); // Clear any previous errors when a new file is selected
    setResponse(null); // Clear previous response
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file) {
      setError("Please select a file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      setLoading(true);
      setError(null); // Reset error state before the API call
      const res = await fetch('http://127.0.0.1:5000/classify_file', {
        method: 'POST',
        body: formData,
      });

      // Handle specific HTTP response statuses
      if (!res.ok) {
        if (res.status === 400) {
          throw new Error("Unsupported file type. Please upload a valid file.");
        } else if (res.status === 500) {
          throw new Error("Server error. Please try again later.");
        } else {
          throw new Error("An unknown error occurred. Please try again.");
        }
      }

      const data = await res.json();
      setResponse(data.file_class);
    } catch (error) {
      console.error("Error:", error);
      if (error.message.includes("Failed to fetch")) {
        setError("Could not connect to the server. Please ensure the API is running.");
      } else {
        setError(error.message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">File Classifier</h1>
      <form
        onSubmit={handleSubmit}
        className="bg-white p-6 rounded shadow-md w-full max-w-md space-y-4"
      >
        <input
          type="file"
          onChange={handleFileChange}
          className="w-full border border-gray-300 rounded p-2"
        />
        <button
          type="submit"
          className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 flex items-center justify-center"
          disabled={loading}
        >
          {loading ? (
            <div className="flex items-center space-x-2">
              <div className="loader rounded-full border-4 border-t-4 border-gray-200 h-5 w-5"></div>
              <span>Uploading...</span>
            </div>
          ) : (
            "Submit"
          )}
        </button>
      </form>

      {/* Display spinner while loading */}
      {loading && (
        <div className="mt-4 flex justify-center">
          <div className="loader rounded-full border-4 border-t-4 border-blue-500 h-8 w-8 animate-spin"></div>
        </div>
      )}

      {/* Display response if successful */}
      {response && (
        <div className="mt-6 p-4 bg-green-100 text-green-800 rounded shadow">
          <strong>Classification Result:</strong> {response}
        </div>
      )}

      {/* Display error message if an error occurs */}
      {error && (
        <div className="mt-6 p-4 bg-red-100 text-red-800 rounded shadow">
          <strong>Error:</strong> {error}
        </div>
      )}
    </div>
  );
}

export default App;