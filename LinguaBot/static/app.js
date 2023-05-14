let recording = false;
let mediaRecorder;
let audioChunks = [];

async function handleResponse(userMessageContent, responseText, audioData = null) {
   // Append the user's message to the chat container
   const userMessage = document.createElement("div");
   userMessage.classList.add("message", "user-message");
   userMessage.textContent = userMessageContent;
   $("#chat-container").append(userMessage);
 
   // Append ChatGPT's response to the chat container
   const chatGPTResponse = document.createElement("div");
   chatGPTResponse.classList.add("message", "assistant-message");
   chatGPTResponse.textContent = responseText;
   $("#chat-container").append(chatGPTResponse);
 
   // Clear the input field and scroll to the bottom
   $("#prompt").val("");
   $("#chat-container").scrollTop($("#chat-container")[0].scrollHeight);
 
   // Play audio response from ChatGPT, if available
   if (audioData) {
     const audioBlob = new Blob([Uint8Array.from(atob(audioData), c => c.charCodeAt(0))], { type: "audio/mpeg" });
     const audioUrl = URL.createObjectURL(audioBlob);
     const audioElement = new Audio(audioUrl);
     audioElement.play();
   }
}


$("#save-chat-button").click(async function () {
  const history = Array.from(document.querySelectorAll(".message")).map((message) => ({
    role: message.classList.contains("user-message") ? "user" : "assistant",
    content: message.textContent,
  }));

  const response = await fetch("/save-history", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ conversation_history: history }),
  });

  const { success } = await response.json();
  if (success) {
    alert("Chat history saved successfully.");
  } else {
    alert("Failed to save chat history.");
  }
});

 
$("#chat-form").submit(async function (event) {
   event.preventDefault();
   const prompt = $("#prompt").val();
   const history = Array.from(document.querySelectorAll(".message")).map((message) => ({
     role: message.classList.contains("user-message") ? "user" : "assistant",
     content: message.textContent,
   }));
 
   const response = await fetch("/", {
     method: "POST",
     headers: { "Content-Type": "application/x-www-form-urlencoded" },
     body: new URLSearchParams({ prompt, history: JSON.stringify(history) }),
   });
 
   const { response_text, audio_data } = await response.json();
   handleResponse(prompt, response_text, audio_data);
});
 
 
$("#record-button").click(async function () {
  try {
    if (!recording) {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(mediaStream, { mimeType: "audio/webm" });
      audioChunks = [];

      mediaRecorder.addEventListener("dataavailable", (event) => {
        audioChunks.push(event.data);
      });

      mediaRecorder.addEventListener("stop", async () => {
        const audioBlob = new Blob(audioChunks, { type: "audio/mpeg" });
        const audioUrl = URL.createObjectURL(audioBlob);

        // Send audio to the server
        const formData = new FormData();
        formData.append("audio", audioBlob);

        // Define history variable here
        const history = Array.from(document.querySelectorAll(".message")).map((message) => ({
          role: message.classList.contains("user-message") ? "user" : "assistant",
          content: message.textContent,
        }));

        console.log("History before sending to server:", history);

        formData.append("history", JSON.stringify(history));

        const response = await fetch("/send-audio", {
          method: "POST",
          body: formData,
        });

        const { response_text, audio_data, user_text } = await response.json();

        // Call the same process to handle the response and display it
        handleResponse(user_text, response_text, audio_data);
      });

      mediaRecorder.start();
      recording = true;
      $("#record-button").text("Stop");
    } else {
      mediaRecorder.stop();
      recording = false;
      $("#record-button").text("Record");
    }
  } catch (error) {
      console.error("Error accessing microphone:", error);
      alert("Error accessing microphone. Please check your browser permissions and try again.");
  }
});
