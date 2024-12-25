let uploadedFiles = [];

// Handle file selection
function handleFiles(files) {
  if (files.length > 0) {
    document.getElementById("no-files-message").style.display = "none";
    for (const file of files) {
      // Check if the file is already in the uploadedFiles array
      if (
        !uploadedFiles.some(
          (f) =>
            f.name === file.name &&
            f.size === file.size &&
            f.lastModified === file.lastModified
        )
      ) {
        uploadedFiles.push(file);
        displayThumbnail(file);
      }
    }
  }
}

// Handle file drop
function handleDrop(event) {
  event.preventDefault();
  const files = event.dataTransfer.files;
  handleFiles(files);

  // Clear the file input to avoid triggering the change event
  document.getElementById("file-input").value = "";
}

// Prevent default behavior for drag over
function handleDragOver(event) {
  event.preventDefault();
}

// Display file as a thumbnail
function displayThumbnail(file) {
  const uploadedFilesDiv = document.getElementById("uploaded-files");
  const reader = new FileReader();

  reader.onload = function (e) {
    const thumbnailDiv = document.createElement("div");
    thumbnailDiv.className = "thumbnail";

    const img = document.createElement("img");
    img.src = e.target.result;

    const removeBtn = document.createElement("button");
    removeBtn.className = "remove-btn";
    removeBtn.innerHTML = "×";
    removeBtn.onclick = function () {
      removeFile(file);
      thumbnailDiv.remove();
      if (uploadedFiles.length === 0) {
        document.getElementById("no-files-message").style.display = "block";
      }
    };

    thumbnailDiv.appendChild(img);
    thumbnailDiv.appendChild(removeBtn);
    uploadedFilesDiv.appendChild(thumbnailDiv);
  };

  reader.readAsDataURL(file);
}

// Remove file from the uploadedFiles array
function removeFile(file) {
  uploadedFiles = uploadedFiles.filter((f) => f !== file);
}

// Upload files to the backend
async function uploadFiles() {
  if (uploadedFiles.length === 0) {
    alert("Please select at least one file.");
    return;
  }

  const formData = new FormData();
  for (const file of uploadedFiles) {
    formData.append("files", file);
  }

  try {
    const response = await fetch("/", {
      method: "POST",
      body: formData,
    });

    if (response.ok) {
      alert("Files uploaded successfully!");
      let uploadedFiles = [];
      window.location.href = "/dashboard";
    } else {
      alert("Failed to upload files.");
    }
  } catch (error) {
    console.error("Error uploading files:", error);
    alert("An error occurred while uploading files.");
  }
}

// Add drag-and-drop event listeners
const uploadSection = document.getElementById("container");
uploadSection.addEventListener("drop", handleDrop);
uploadSection.addEventListener("dragover", handleDragOver);

// Handle file input change event
document
  .getElementById("file-input")
  .addEventListener("change", function (event) {
    handleFiles(event.target.files);
  });
