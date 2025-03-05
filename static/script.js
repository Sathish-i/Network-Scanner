document.addEventListener("DOMContentLoaded", () => {
    const fullNetworkCheckbox = document.getElementById("fullNetwork");
    const ipAddressInput = document.getElementById("ipAddress");
    const startScanButton = document.getElementById("startScan");
    const confirmationDiv = document.getElementById("confirmation");
    const scanDetails = document.getElementById("scanDetails");
    const confirmScanButton = document.getElementById("confirmScan");
    const cancelScanButton = document.getElementById("cancelScan");
    const resultsDiv = document.getElementById("results");

    fullNetworkCheckbox.addEventListener("change", () => {
        ipAddressInput.disabled = fullNetworkCheckbox.checked;
    });

    startScanButton.addEventListener("click", () => {
        const scanType = document.querySelector("input[name='scanType']:checked").value;
        const targetIP = ipAddressInput.value;
        const fullNetwork = fullNetworkCheckbox.checked;
        
        scanDetails.textContent = `Scan Type: ${scanType.toUpperCase()}${fullNetwork ? " (Full Network)" : ""}`;
        confirmationDiv.classList.remove("hidden");
    });

    cancelScanButton.addEventListener("click", () => {
        confirmationDiv.classList.add("hidden");
    });
});
