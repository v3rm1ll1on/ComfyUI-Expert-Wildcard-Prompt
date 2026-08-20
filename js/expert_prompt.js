import { app } from "../../../scripts/app.js";

/**
 * ExpertTextPrompt Colorizer & Syntax Overlay
 * 
 * Uses a zero-jump backdrop overlay approach.
 * The original textarea handles native typing, focus, selections, and cursor movements.
 * Transparent text in textarea lets the colored backdrop div show through perfectly aligned.
 */

app.registerExtension({
    name: "ExpertTextPrompt.Colorizer",
    async nodeCreated(node) {
        if (node.comfyClass === "ExpertTextPrompt") {
            // Set output slot colors
            if (node.outputs) {
                if (node.outputs[0]) {
                    node.outputs[0].color_on = "#22c55e"; // Green for Positive
                    node.outputs[0].label = "positive";
                }
                if (node.outputs[1]) {
                    node.outputs[1].color_on = "#ef4444"; // Red for Negative
                    node.outputs[1].label = "negative";
                }
            }

            // Bind syntax checking and overlay styling to widgets
            const posWidget = node.widgets?.find(w => w.name === "positive_prompt");
            const negWidget = node.widgets?.find(w => w.name === "negative_prompt");

            if (posWidget) setupWidgetOverlay(node, posWidget, false);
            if (negWidget) setupWidgetOverlay(node, negWidget, true);
        }
    }
});

function setupWidgetOverlay(node, widget, isDefaultNegative = false) {
    const origCallback = widget.callback;
    widget.callback = function (val) {
        checkSyntaxAndWarn(node);
        if (origCallback) return origCallback.apply(this, arguments);
    };

    // Attach overlay when input HTML element is available
    setTimeout(() => {
        const textarea = widget.inputEl;
        if (!textarea) return;

        createBackdropOverlay(textarea, isDefaultNegative);
    }, 100);
}

function createBackdropOverlay(textarea, isDefaultNegative) {
    if (textarea.dataset.hasOverlay === "true") return;
    textarea.dataset.hasOverlay = "true";

    const parent = textarea.parentElement || textarea.parentNode;
    if (!parent) return;

    // Ensure parent container is relative
    if (window.getComputedStyle(parent).position === "static") {
        parent.style.position = "relative";
    }

    // Create backdrop container
    const backdrop = document.createElement("div");
    backdrop.className = "expert-prompt-backdrop";
    
    // Style backdrop to sit directly behind textarea with exact same font, padding, and line height
    const computed = window.getComputedStyle(textarea);
    
    Object.assign(backdrop.style, {
        position: "absolute",
        top: textarea.offsetTop + "px",
        left: textarea.offsetLeft + "px",
        width: textarea.offsetWidth + "px",
        height: textarea.offsetHeight + "px",
        fontFamily: computed.fontFamily,
        fontSize: computed.fontSize,
        lineHeight: computed.lineHeight,
        padding: computed.padding,
        border: computed.border,
        boxSizing: computed.boxSizing,
        whiteSpace: "pre-wrap",
        wordWrap: "break-word",
        overflow: "hidden",
        pointerEvents: "none",
        color: "transparent",
        backgroundColor: "transparent",
        zIndex: "1"
    });

    // Make textarea transparent so backdrop colors shine through
    textarea.style.position = "relative";
    textarea.style.zIndex = "2";
    textarea.style.backgroundColor = "transparent";
    textarea.style.color = "rgba(255, 255, 255, 0.85)"; // Fallback text color

    parent.insertBefore(backdrop, textarea);

    const updateHighlighting = () => {
        const text = textarea.value || "";
        backdrop.innerHTML = highlightPromptText(text, isDefaultNegative) + "<br>";
        backdrop.scrollTop = textarea.scrollTop;
        backdrop.scrollLeft = textarea.scrollLeft;
    };

    textarea.addEventListener("input", updateHighlighting);
    textarea.addEventListener("scroll", updateHighlighting);
    updateHighlighting();
}

function highlightPromptText(text, isDefaultNegative) {
    if (!text) return "";

    // Escape HTML special characters
    let escaped = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");

    // Highlight bracket depths
    let depth = 0;
    const bracketColors = ["#60a5fa", "#f472b6", "#34d399", "#fbbf24", "#a78bfa", "#38bdf8"];
    let result = "";

    // Parse tokens and apply styles
    // 1. Group Tags [GRP:...] -> Cyan Bold
    escaped = escaped.replace(/(\[GRP:[^\]]+\])/g, '<span style="color:#22d3ee; font-weight:bold;">$1</span>');

    // 2. Solo ! -> Gold/Yellow
    escaped = escaped.replace(/(^|\s|,)(\![^,\n]+)/g, '$1<span style="color:#facc15; font-weight:bold;">$2</span>');

    // 3. Mute // -> Dim Grey
    escaped = escaped.replace(/(\/\/[^,\n]+)/g, '<span style="color:#6b7280; text-decoration:line-through; opacity:0.7;">$1</span>');

    // 4. Negative Prefix - -> Bright Red
    escaped = escaped.replace(/(^|\s|,)(-[a-zA-Z0-9_]+)/g, '$1<span style="color:#f87171; font-weight:bold;">$2</span>');

    // 5. Placeholder $negative -> Purple/Magenta
    escaped = escaped.replace(/(\$negative\b)/g, '<span style="color:#c084fc; font-weight:bold; background:rgba(192,132,252,0.15); padding:0 2px; border-radius:2px;">$1</span>');

    // 6. Percentages inside wildcards (e.g. 70%, 20%?) -> Emerald
    escaped = escaped.replace(/(\b\d+%(?:\?)?)/g, '<span style="color:#34d399; font-weight:bold;">$1</span>');

    return escaped;
}

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
