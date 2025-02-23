document.getElementById("generate").addEventListener("click", () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        let videoUrl = tabs[0].url;
  
        console.log("Fetching transcript for:", videoUrl);
  
        fetch("http://localhost:5000/process", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ link: videoUrl })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error("Error:", data.error);
                document.getElementById("transcript").value = "Error: " + data.error;
                return;
            }
  
            let text = data.segments.map(s => `[${s.timestamp}] ${s.summary}`).join("\n\n");
            document.getElementById("transcript").value = text;
        })
        .catch(error => {
            console.error("Error fetching transcript:", error);
            document.getElementById("transcript").value = "Error fetching transcript!";
        });
    });
  });
  
  document.getElementById("download").addEventListener("click", () => {
    let content = document.getElementById("transcript").value;
  
    if (!content.trim()) {
        alert("No transcript available!");
        return;
    }
  
    let blob = new Blob([content], { type: "text/plain" });
    let url = URL.createObjectURL(blob);
  
    chrome.downloads.download({
        url,
        filename: "transcript.txt"
    });
  });
  