import { app } from "../../../scripts/app.js";

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

            // Find multiline text widgets
            const posWidget = node.widgets?.find(w => w.name === "positive_prompt");
            const negWidget = node.widgets?.find(w => w.name === "negative_prompt");

            if (posWidget) {
                const origPos = posWidget.callback;
                posWidget.callback = function (val) {
                    checkSyntaxAndWarn(node, val);
                    if (origPos) return origPos.apply(this, arguments);
                };
            }

            if (negWidget) {
                const origNeg = negWidget.callback;
                negWidget.callback = function (val) {
                    checkSyntaxAndWarn(node, val);
                    if (origNeg) return origNeg.apply(this, arguments);
                };
            }
        }
    }
});

function checkSyntaxAndWarn(node, text) {
    if (!text) return;
    const stack = [];
    let isValid = true;

    for (let i = 0; i < text.length; i++) {
        const char = text[i];
        if ("({[".includes(char)) {
            stack.push({ char, pos: i });
        } else if (")}]".includes(char)) {
            const expected = { "}": "{", ")": "(", "]": "[" }[char];
            if (stack.length === 0 || stack[stack.length - 1].char !== expected) {
                isValid = false;
                break;
            } else {
                stack.pop();
            }
        }
    }

    if (isValid && stack.length > 0) {
        isValid = false;
    }

    if (!isValid) {
        node.bgcolor = "#451a1a"; // Dark red background on syntax error
    } else {
        node.bgcolor = undefined; // Reset background
    }
}
