import { useState, useEffect } from "react";

function App() {
  const [file, setFile] = useState(null);
  const [imageUrl, setImageUrl] = useState("");
  const [apiUrl, setApiUrl] = useState("");

  useEffect(() => {
    fetch("/config.json")
      .then((response) => response.json())
      .then((config) => {
        console.log("API URL:", config.API_URL);
        setApiUrl(config.API_URL);
      })
      .catch((error) => console.error("Error loading config:", error));
  }, []);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

const handleUpload = async () => {
  if (!file) {
    alert("Please select a file.");
    return;
  }

  const reader = new FileReader();
  reader.readAsDataURL(file);
  reader.onload = async () => {
    const base64Data = reader.result.split(",")[1]; // Extract Base64 string

    const payload = JSON.stringify({
      action: "upload",
      file_name: file.name,
      file_data: base64Data,
    });

    const response = await fetch(`${apiUrl}/images`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: payload,
    });

    if (!response.ok) {
      alert("Upload failed!");
      return;
    }

    const data = await response.json();
    setImageUrl(data.imageUrl);
    console.log("SUCCESS");
  };
};


  return (
    <div style={{ padding: "20px", textAlign: "center" }}>
      <h1>Image Uploader</h1>
      <input
        type="file"
        onChange={handleFileChange}
        style={{ marginBottom: "10px", padding: "5px" }}
      />
      <button
        onClick={handleUpload}
        disabled={!apiUrl || !file} // Ensure button is enabled only when file and apiUrl are set
        style={{
          padding: "10px 20px",
          cursor: apiUrl && file ? "pointer" : "not-allowed",
          backgroundColor: apiUrl && file ? "#4CAF50" : "#ddd",
          color: apiUrl && file ? "white" : "#777",
          border: "none",
          borderRadius: "4px",
        }}
      >
        Upload
      </button>

      {imageUrl && (
        <div>
          <h2>Uploaded Image:</h2>
          <img src={imageUrl} alt="Uploaded" width="300" />
        </div>
      )}
    </div>
  );
}

export default App;
