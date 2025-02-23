chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "fetchTranscript") {
      fetchTranscript(message.videoUrl)
          .then(transcript => {
              sendResponse({ segments: transcript });
          })
          .catch(error => {
              sendResponse({ error: error.message });
          });
      return true; // Keeps the message channel open for async response
  }
});

async function fetchTranscript(videoUrl) {
  try {
      let videoId = new URL(videoUrl).searchParams.get("v");
      console.log("Extracted Video ID:", videoId);

      if (!videoId) throw new Error("Invalid video URL");

      let response = await fetch(`https://some-api.com/transcripts/${videoId}`);
      if (!response.ok) throw new Error("Failed to fetch transcript");

      let data = await response.json();
      console.log("Transcript data received:", data);
      
      return data.segments || [];
  } catch (err) {
      console.error("Error fetching transcript:", err.message);
      throw new Error("Transcript not available");
  }
}
