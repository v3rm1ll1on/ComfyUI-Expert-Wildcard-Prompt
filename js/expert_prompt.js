import { app } from "../../../scripts/app.js";

// Rainbow colors for nested brackets
const BRACKET_COLORS = [
    "#3b82f6", // Blue
    "#ec4899", // Pink
    "#10b981", // Emerald
    "#f59e0b", // Amber
    "#8b5cf6", // Purple
    "#06b6d4"  # Cyan
];

app.registerExtension({
    name: "ExpertTextPrompt.Colorizer",
    async nodeCreated(node) {
        if (node.comfyClass === "ExpertTextPrompt") {
            // Customize output slot colors (Green for Positive, Red for Negative)
            if (node.outputs) {
                if (node.outputs[0]) {
                    node.outputs[0].color_on = "#22c55e"; // Green
                    node.outputs[0].label = "positive";
                }
                if (node.outputs[1]) {
                    node.outputs[1].color_on = "#ef4444"; // Red
                    node.outputs[1].label = "negative";
                }
            }

            // Find the multiline text widget
            const textWidget = node.widgets?.find(w => w.name === "text");
            if (textWidget) {
                // Add syntax check on value change
                const originalCallback = textWidget.callback;
                textWidget.callback = function (val) {
                    checkSyntaxAndWarn(node, val);
                    if (originalCallback) return originalCallback.apply(this, arguments);
                };
            }
        }
    }
});

function checkSyntaxAndWarn(node, text) {
    if (!text) return;
    const stack = [];
    let isValid = true;
    let errorMsg = "";

    for (let i = 0; i < text.length; i++) {
        const char = text[i];
        if ("({[".includes(char)) {
            stack.push({ char, pos: i });
        } else if (")}]".includes(char)) {
            const expected = { "}": "{", ")": "(", "]": "[" }[char];
            if (stack.length === 0 || stack[stack.length - 1].char !== expected) {
                isValid = false;
                errorMsg = `Mismatched bracket '${char}' at position ${i}`;
                break;
            } else {
                stack.pop();
            }
        }
    }

    if (isValid && stack.length > 0) {
        isValid = false;
        errorMsg = `Unclosed bracket '${stack[stack.length - 1].char}' at position ${stack[stack.length - 1].pos}`;
    }

    if (!isValid) {
        node.bgcolor = "#451a1a"; // Dark red background on error
        node.title_mode = 1;
    } else {
        node.bgcolor = undefined; // Reset background
    }
}
