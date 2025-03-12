document.addEventListener("DOMContentLoaded", () => {
    const socket = io();  // Connect to WebSocket
    const resultsDiv = document.getElementById("results");

    socket.on("scan_update", (data) => {
        const lineElement = document.createElement("p");
        lineElement.textContent = data.line;
        resultsDiv.appendChild(lineElement);
    });

    document.getElementById("startScan").addEventListener("click", () => {
        const scanType = document.querySelector("input[name='scanType']:checked").value;
        const targetIP = document.getElementById("ipAddress").value;
        const fullNetwork = document.getElementById("fullNetwork").checked;

        resultsDiv.innerHTML = "";  // Clear previous results

        fetch("/scan", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ scanType, targetIP, fullNetwork })
        }).then(response => response.json())
          .then(data => {
              const downloadLink = document.createElement("a");
              downloadLink.href = data.downloadLink;
              downloadLink.textContent = "Download Full Scan Results";
              resultsDiv.appendChild(downloadLink);
          });
    });
});
