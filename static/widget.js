(function () {
    const script = document.currentScript;

    const widgetId = script.getAttribute("data-widget-id");

    if (!widgetId) {
        console.error("FlyRank: data-widget-id is required.");
        return;
    }

    const API_URL = "http://localhost:8000";

    const container = document.createElement("div");

    container.innerHTML = `
        <div id="flyrank-widget" style="
            max-width: 420px;
            padding: 24px;
            border: 1px solid #ddd;
            border-radius: 12px;
            font-family: Arial, sans-serif;
            background: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        ">
            <h2 style="margin-top: 0;">Contact Us</h2>

            <form id="flyrank-form">

                <input
                    type="text"
                    id="flyrank-name"
                    placeholder="Your Name"
                    required
                    style="
                        width: 100%;
                        padding: 10px;
                        margin-bottom: 12px;
                        box-sizing: border-box;
                    "
                />

                <input
                    type="email"
                    id="flyrank-email"
                    placeholder="Your Email"
                    required
                    style="
                        width: 100%;
                        padding: 10px;
                        margin-bottom: 12px;
                        box-sizing: border-box;
                    "
                />

                <textarea
                    id="flyrank-message"
                    placeholder="Your Message"
                    rows="4"
                    style="
                        width: 100%;
                        padding: 10px;
                        margin-bottom: 12px;
                        box-sizing: border-box;
                    "
                ></textarea>

                <input
                    type="text"
                    id="flyrank-honeypot"
                    autocomplete="off"
                    tabindex="-1"
                    style="display:none;"
                />

                <button
                    type="submit"
                    style="
                        width: 100%;
                        padding: 12px;
                        border: none;
                        border-radius: 8px;
                        background: #111;
                        color: white;
                        cursor: pointer;
                    "
                >
                    Submit
                </button>

                <p id="flyrank-status" style="margin-bottom: 0;"></p>

            </form>
        </div>
    `;

    script.parentNode.insertBefore(container, script);

    const form = container.querySelector("#flyrank-form");
    const status = container.querySelector("#flyrank-status");

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        status.textContent = "Submitting...";

        const name = container.querySelector("#flyrank-name").value;
        const email = container.querySelector("#flyrank-email").value;
        const message = container.querySelector("#flyrank-message").value;
        const honeypot = container.querySelector("#flyrank-honeypot").value;

        try {
            const response = await fetch(`${API_URL}/submissions`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    widget_id: Number(widgetId),
                    name: name,
                    email: email,
                    message: message,
                    honeypot: honeypot
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || data.message || "Submission failed");
            }

            status.textContent = "Thank you! Your submission was received.";

            form.reset();

            console.log("FlyRank submission:", data);

        } catch (error) {
            console.error("FlyRank error:", error);

            status.textContent =
                "Something went wrong. Please try again.";
        }
    });

})();