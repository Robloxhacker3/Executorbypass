document.getElementById("bypassBtn").addEventListener("click", async () => {
    const url = document.getElementById("urlInput").value;
    const responseElement = document.getElementById("response");
    responseElement.innerHTML = "Bypassing... Please wait.";

    if (url) {
        try {
            const response = await fetch("/api/bypass", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ url }),
            });

            const result = await response.json();
            if (result.success) {
                responseElement.innerHTML = `Bypass successful: <a href="${result.link}" target="_blank">Click here</a>`;
            } else {
                responseElement.innerHTML = `Error: ${result.error}`;
            }
        } catch (error) {
            responseElement.innerHTML = "Error occurred while bypassing.";
            console.error(error);
        }
    } else {
        responseElement.innerHTML = "Please enter a valid link.";
    }
});
