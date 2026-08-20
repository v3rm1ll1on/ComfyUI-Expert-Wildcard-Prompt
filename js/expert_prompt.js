import { app } from "../../../scripts/app.js";

/**
 * ExpertTextPrompt UI Extensions
 * 
 * Sets node output slot colors and handles syntax error visual feedback.
 */

app.registerExtension({
    name: "ExpertTextPrompt.Colorizer",
    async nodeCreated(node) {
        if (node.comfyClass === "ExpertTextPrompt") {
            // Set slot pin colors (Green for Positive, Red for Negative)
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

            // Bind syntax checking to widget callbacks
            const posWidget = node.widgets?.find(w => w.name === "positive_prompt");
            const negWidget = node.widgets?.find(w => w.name === "negative_prompt");

            if (posWidget) {
                const origPos = posWidget.callback;
                posWidget.callback = function (val) {
                    checkSyntaxAndWarn(node);
                    if (origPos) return origPos.apply(this, arguments);
                };
            }

            if (negWidget) {
                const origNeg = negWidget.callback;
                negWidget.callback = function (val) {
                    checkSyntaxAndWarn(node);
                    if (origNeg) return origNeg.apply(this, arguments);
                };
            }
        }
    }
});

function checkSyntaxAndWarn(node) {
    const posWidget = node.widgets?.find(w => w.name === "positive_prompt");
    const negWidget = node.widgets?.find(w => w.name === "negative_prompt");

    const posValid = isBracketSyntaxValid(posWidget?.value || "");
    const negValid = isBracketSyntaxValid(negWidget?.value || "");

    if (!posValid || !negValid) {
        node.bgcolor = "#451a1a"; // Dark red background on syntax error
    } else {
        node.bgcolor = undefined; // Reset background
    }
}

function isBracketSyntaxValid(text) {
    if (!text) return true;
    const stack = [];
    for (let i = 0; i < text.length; i++) {
        const char = text[i];
        if ("({[".includes(char)) {
            stack.push(char);
        } else if (")}]".includes(char)) {
            const expected = { "}": "{", ")": "(", "]": "[" }[char];
            if (stack.length === 0 || stack.pop() !== expected) {
                return false;
            }
        }
    }
    return stack.length === 0;
}
