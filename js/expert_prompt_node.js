import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "ExpertTextPrompt.CombinationsDisplay",
    async nodeCreated(node) {
        if (node.comfyClass === "ExpertTextPrompt") {
            const widget = node.addWidget("text", "combinations_info", "Combinations: -", () => {}, {
                serialize: false,
            });
            widget.inputEl.readOnly = true;
            widget.inputEl.style.color = "#76b9ed";
            widget.inputEl.style.fontWeight = "bold";
            widget.inputEl.style.textAlign = "center";
            widget.inputEl.style.background = "rgba(0,0,0,0.25)";
            widget.inputEl.style.border = "1px solid rgba(255,255,255,0.15)";
            widget.inputEl.style.borderRadius = "4px";

            const origOnExecuted = node.onExecuted;
            node.onExecuted = function(message) {
                if (origOnExecuted) {
                    origOnExecuted.apply(this, arguments);
                }
                if (message?.text && message.text[0]) {
                    widget.value = message.text[0];
                }
            };
        }
    }
});
