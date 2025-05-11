import { useState, useEffect } from "react";

function App() {
  const [file, setFile] = useState(null);
  const [images, setImages] = useState([]);
  const [apiUrl, setApiUrl] = useState("");
  const [loadingImages, setLoadingImages] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    // Load API URL from config
    fetch("/config.json")
      .then((response) => response.json())
      .then((config) => {
        setApiUrl(config.API_URL);
        // Load images immediately after API URL is set
        fetchImages(config.API_URL);
      })
      .catch((error) => console.error("Error loading config:", error));
  }, []);

  const fetchImages = async (apiUrl) => {
    try {
      setLoadingImages(true);
      const response = await fetch(`${apiUrl}images`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
        mode: "cors",
      });

      if (!response.ok) {
        throw new Error("Failed to fetch images");
      }

      const data = await response.json();
      console.log("Fetched images:", data.images);
      console.log("Fetched IMAGE 1:", data.images[0]);
      console.log("Fetched IMAGE 1 url:", data.images[0].imageUrl);

      setImages(data.images);
    } catch (error) {
      console.error("Error fetching images:", error);
    } finally {
      setLoadingImages(false);
    }
  };

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file || !apiUrl) {
      alert("Please select a file and ensure API is configured");
      return;
    }

    setUploading(true);
    const reader = new FileReader();

    reader.onload = async () => {
      try {
        const base64Data = reader.result.split(",")[1];

        const response = await fetch(`${apiUrl}images`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            file_name: file.name,
            file_data: base64Data,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || "Upload failed");
        }

        const data = await response.json();
        console.log("Upload successful:", data);
        await fetchImages(apiUrl);
        alert("Image uploaded successfully!");
      } catch (error) {
        console.error("Upload error:", error);
        alert(`Upload failed: ${error.message}`);
      } finally {
        setUploading(false);
      }
    };

    reader.onerror = () => {
      setUploading(false);
      alert("Error reading file");
    };

    reader.readAsDataURL(file); // This reads the file as a data URL (base64)
  };

  const handleDelete = async () => {
    if (!file || !apiUrl) return;
    setDeleting(true);
    console.log("Disabled?", !apiUrl || !file || deleting);
    console.log({ apiUrl, file, deleting });  
    
    try {
      const response = await fetch(`${apiUrl}images?key=${encodeURIComponent(file.name)}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
        mode: "cors",
        body: JSON.stringify({
          file_name: file.name,
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Delete failed");
      }

      const data = await response.json();
      console.log("Delete successful:", data);
      await fetchImages(apiUrl);
      alert("Delete successful");
    } catch (error) {
      console.error("Delete error:", error);
      alert(`Delete failed: ${error.message}`);
    } finally {
      setDeleting(false);
    }

  }

  return (
    <div style={{ padding: "20px", maxWidth: "800px", margin: "0 auto" }}>
      <h1 style={{ textAlign: "center", marginBottom: "30px" }}>
        Image Gallery
      </h1>

      {/* Upload Section */}
      <div
        style={{
          backgroundColor: "#f5f5f5",
          padding: "20px",
          borderRadius: "8px",
          marginBottom: "30px",
          position: "relative", // For loading overlay
        }}
      >
        {/* Loading overlay during upload */}
        {uploading && (
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: "rgba(255,255,255,0.7)",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              zIndex: 10,
            }}
          >
            <div
              style={{
                padding: "20px",
                backgroundColor: "#fff",
                borderRadius: "8px",
                boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
                textAlign: "center",
              }}
            >
              <div
                style={{
                  display: "inline-block",
                  width: "40px",
                  height: "40px",
                  border: "4px solid #f3f3f3",
                  borderTop: "4px solid #3498db",
                  borderRadius: "50%",
                  animation: "spin 1s linear infinite",
                  marginBottom: "10px",
                }}
              ></div>
              <p>Uploading your image...</p>
            </div>
          </div>
        )}

        <h2>Upload New Image</h2>
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          disabled={uploading}
          style={{
            margin: "10px 0",
            padding: "10px",
            border: "1px solid #ddd",
            borderRadius: "4px",
            width: "100%",
            opacity: uploading ? 0.7 : 1,
          }}
        />
        <div style={{display: "flex", gap: "20px"}}>
          <button
          onClick={handleUpload}
          disabled={!apiUrl || !file || uploading}
          style={{
            padding: "10px 20px",
            backgroundColor: !apiUrl || !file || uploading ? "#ddd" : "#4CAF50",
            color: !apiUrl || !file || uploading ? "#777" : "white",
            border: "none",
            borderRadius: "4px",
            cursor: !apiUrl || !file || uploading ? "not-allowed" : "pointer",
            fontSize: "16px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "8px",
            }}
          >
            {uploading ? (
              <>
                <span
                  style={{
                    display: "inline-block",
                    width: "16px",
                    height: "16px",
                    border: "2px solid #f3f3f3",
                    borderTop: "2px solid #3498db",
                    borderRadius: "50%",
                    animation: "spin 1s linear infinite",
                  }}
                ></span>
                Uploading...
              </>
            ) : (
              "Upload Image"
            )}
          </button>
          <button
            onClick={handleDelete}
            disabled={!apiUrl || !file || deleting}
            //disabled={false}
              style={{
                padding: "10px 20px",
                backgroundColor: !apiUrl || !file || deleting ? "#f5b5b5" : "#e02424",
                color: !apiUrl || !file || deleting ? "#777" : "white",
                border: "none",
                borderRadius: "4px",
                cursor: !apiUrl || !file || deleting ? "not-allowed" : "pointer",
                fontSize: "16px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "8px",
              }}
              >
              {deleting ? (
                <>
                  <span
                      style={{
                        display: "inline-block",
                        width: "16px",
                        height: "16px",
                        border: "2px solid #f3f3f3",
                        borderTop: "2px solid #3498db",
                        borderRadius: "50%",
                        animation: "spin 1s linear infinite",
                      }}
                  ></span>
                    Deleting
                </>
                ) : (
                "Delete Images"
              )}
          </button>
        </div>
      </div>

      {/* Image Gallery Section */}
      <div>
        <h2 style={{ marginBottom: "20px" }}>Your Images</h2>
        {loadingImages ? (
          <div
            style={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              height: "200px",
            }}
          >
            <div
              style={{
                width: "40px",
                height: "40px",
                border: "4px solid #f3f3f3",
                borderTop: "4px solid #3498db",
                borderRadius: "50%",
                animation: "spin 1s linear infinite",
              }}
            ></div>
          </div>
        ) : images.length === 0 ? (
          <p>No images found. Upload your first image!</p>
        ) : (
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(250px, 1fr))",
              gap: "20px",
            }}
          >
            {images.map((image) => {
              return (
                <div
                  key={image.key}
                  style={{
                    border: "1px solid #eee",
                    borderRadius: "8px",
                    overflow: "hidden",
                    boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
                    position: "relative",
                  }}
                >
                  <img
                    src={image.imageUrl}
                    alt={image.key}
                    style={{
                      width: "100%",
                      height: "200px",
                      objectFit: "cover",
                    }}
                  />
                  <div style={{ padding: "10px" }}>
                    <p
                      style={{
                        margin: "0",
                        fontSize: "14px",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {image.key}
                    </p>
                    <p
                      style={{
                        margin: "5px 0 0",
                        fontSize: "12px",
                        color: "#666",
                      }}
                    >
                      Uploaded: {new Date(image.lastModified).toLocaleString()}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Add CSS for spinner animation */}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default App;
