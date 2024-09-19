document.addEventListener("DOMContentLoaded", () => {
  const fileInput = document.getElementById("file-input");
  const uploadBtn = document.getElementById("upload-btn");
  const userMessageInput = document.getElementById("user-message");
  const sendBtn = document.getElementById("send-btn");
  const chatMessages = document.getElementById("chat-messages");
  const loadingOverlay = document.getElementById("loading-overlay");

  uploadBtn.addEventListener("click", async () => {
    const file = fileInput.files[0];
    if (!file) {
      alert("Please select a file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    loadingOverlay.classList.remove("hidden");

    try {
      const response = await fetch("/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          alert("File uploaded and processed successfully!");
        } else {
          alert("Error processing the file.");
        }
      } else {
        alert("Error uploading the file.");
      }
    } catch (error) {
      console.error("Error:", error);
      alert("An error occurred while uploading the file.");
    } finally {
      loadingOverlay.classList.add("hidden");
    }
  });

  sendBtn.addEventListener("click", sendMessage);
  userMessageInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      sendMessage();
    }
  });

  async function sendMessage() {
    const message = userMessageInput.value.trim();
    if (!message) return;

    displayMessage(message, "user-message");
    userMessageInput.value = "";

    try {
      const response = await fetch("/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: message }),
      });

      if (response.ok) {
        const result = await response.json();
        displayMessage(result.response, "bot-message");
      } else {
        displayMessage(
          "Error: Unable to get response from the chatbot.",
          "bot-message"
        );
      }
    } catch (error) {
      console.error("Error:", error);
      displayMessage("Error: An unexpected error occurred.", "bot-message");
    }
  }

  function displayMessage(message, className) {
    const messageElement = document.createElement("div");
    messageElement.classList.add("message", className);
    messageElement.textContent = message;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
});
