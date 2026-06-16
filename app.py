import json
import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(
    page_title="Sinhala Text Tagging Tool",
    layout="wide"
)

st.title("Sinhala Text Tagging Tool")
st.write(
    "Paste your text in the editor, select a word/sentence/phrase, "
    "then click the required tag button."
)

DEFAULT_TEXT = """
"""

editor_html = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    body {
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 12px;
        background: #ffffff;
    }

    .toolbar {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 12px;
        position: sticky;
        top: 0;
        background: white;
        padding-bottom: 10px;
        z-index: 10;
        border-bottom: 1px solid #ddd;
    }

    button {
        padding: 8px 14px;
        border: 1px solid #bbb;
        border-radius: 8px;
        cursor: pointer;
        font-size: 14px;
        background: #f8f8f8;
    }

    button:hover {
        background: #eaeaea;
    }

    .primary {
        background: #e8f0ff;
        border-color: #9dbbff;
    }

    .danger {
        background: #ffecec;
        border-color: #ffb3b3;
    }

    #editor {
        min-height: 370px;
        border: 1px solid #ccc;
        border-radius: 10px;
        padding: 14px;
        font-size: 18px;
        line-height: 1.8;
        white-space: pre-wrap;
        outline: none;
        overflow-y: auto;
        background: #fff;
    }

    #editor:focus {
        border-color: #4d90fe;
        box-shadow: 0 0 0 2px rgba(77, 144, 254, 0.15);
    }

    .label {
        font-weight: bold;
        margin-top: 14px;
        margin-bottom: 6px;
    }

    #output {
        width: 100%;
        height: 230px;
        font-size: 15px;
        line-height: 1.5;
        border: 1px solid #ccc;
        border-radius: 10px;
        padding: 12px;
        box-sizing: border-box;
        white-space: pre-wrap;
    }

    #status {
        margin-top: 8px;
        font-size: 14px;
        color: #444;
    }

    .help {
        font-size: 14px;
        color: #555;
        margin-bottom: 10px;
    }
</style>
</head>

<body>

<div class="toolbar">
    <button class="primary" id="nonSinhalaBtn">Add &lt;sns&gt;...&lt;ens&gt;</button>
    <button class="primary" id="eosBtn">Add &lt;eos&gt; at end</button>
    <button class="primary" id="psiBtn">Add &lt;psi&gt; after selection</button>
    <button id="copyBtn">Copy final text</button>
    <button id="downloadBtn">Download .txt</button>
    <button class="danger" id="clearBtn">Clear</button>
</div>

<div class="help">
    Select text inside the editor. Then click a tag button.
    Example: selecting <b>ඉදානි,</b> and clicking sns/ens becomes
    <b>&lt;sns&gt;ඉදානි,&lt;ens&gt;</b>.
</div>

<div id="editor" contenteditable="true" spellcheck="false"></div>

<div id="status">Ready.</div>

<div class="label">Final tagged text</div>
<textarea id="output" readonly></textarea>

<script>
    const initialText = __DEFAULT_TEXT__;

    const editor = document.getElementById("editor");
    const output = document.getElementById("output");
    const statusBox = document.getElementById("status");

    editor.textContent = initialText;
    syncOutput();

    let savedSelection = null;

    function getText() {
        return editor.textContent || "";
    }

    function setText(newText) {
        editor.textContent = newText;
        syncOutput();
    }

    function syncOutput() {
        output.value = getText();
    }

    function setStatus(message) {
        statusBox.textContent = message;
    }

    function isInsideEditor(node) {
        return node === editor || editor.contains(node);
    }

    function getSelectionOffsets() {
        const selection = window.getSelection();

        if (!selection || selection.rangeCount === 0) {
            return null;
        }

        const range = selection.getRangeAt(0);

        if (!isInsideEditor(range.startContainer) || !isInsideEditor(range.endContainer)) {
            return null;
        }

        const preRange = range.cloneRange();
        preRange.selectNodeContents(editor);
        preRange.setEnd(range.startContainer, range.startOffset);

        const start = preRange.toString().length;
        const selectedText = range.toString();
        const end = start + selectedText.length;

        return {
            start: start,
            end: end
        };
    }

    function saveSelection() {
        const offsets = getSelectionOffsets();

        if (offsets !== null) {
            savedSelection = offsets;
            const selectedLength = offsets.end - offsets.start;

            if (selectedLength > 0) {
                setStatus("Selected " + selectedLength + " characters.");
            }
        }
    }

    function findTextPosition(root, offset) {
        const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
        let currentOffset = 0;
        let node;

        while ((node = walker.nextNode())) {
            const nextOffset = currentOffset + node.textContent.length;

            if (offset <= nextOffset) {
                return {
                    node: node,
                    offset: offset - currentOffset
                };
            }

            currentOffset = nextOffset;
        }

        if (!root.firstChild) {
            root.appendChild(document.createTextNode(""));
        }

        return {
            node: root.firstChild,
            offset: root.firstChild.textContent.length
        };
    }

    function setCursor(offset) {
        editor.focus();

        const textLength = getText().length;
        const safeOffset = Math.max(0, Math.min(offset, textLength));

        const position = findTextPosition(editor, safeOffset);
        const range = document.createRange();

        range.setStart(position.node, position.offset);
        range.collapse(true);

        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);

        savedSelection = {
            start: safeOffset,
            end: safeOffset
        };
    }

    function applyTag(transformFunction, requireSelection = true) {
        saveSelection();

        if (!savedSelection) {
            setStatus("Please select text inside the editor first.");
            return;
        }

        const text = getText();
        const start = savedSelection.start;
        const end = savedSelection.end;

        if (start < 0 || end > text.length || start > end) {
            setStatus("Invalid selection. Please select the text again.");
            return;
        }

        const selectedText = text.slice(start, end);

        if (requireSelection && selectedText.length === 0) {
            setStatus("Please select some text first.");
            return;
        }

        const replacement = transformFunction(selectedText);
        const newText = text.slice(0, start) + replacement + text.slice(end);

        setText(newText);

        const cursorPosition = start + replacement.length;
        setCursor(cursorPosition);

        setStatus("Tag added successfully.");
    }

    function insertAtCursorOrSelection(tag) {
        saveSelection();

        if (!savedSelection) {
            const text = getText();
            setText(text + tag);
            setCursor(text.length + tag.length);
            setStatus(tag + " added at the end.");
            return;
        }

        const text = getText();
        const start = savedSelection.start;
        const end = savedSelection.end;
        const selectedText = text.slice(start, end);

        const replacement = selectedText + tag;
        const newText = text.slice(0, start) + replacement + text.slice(end);

        setText(newText);
        setCursor(start + replacement.length);

        setStatus(tag + " added.");
    }

    document.addEventListener("selectionchange", function () {
        const selection = window.getSelection();

        if (
            selection &&
            selection.rangeCount > 0 &&
            isInsideEditor(selection.getRangeAt(0).startContainer)
        ) {
            saveSelection();
        }
    });

    editor.addEventListener("keyup", saveSelection);
    editor.addEventListener("mouseup", saveSelection);
    editor.addEventListener("input", function () {
        syncOutput();
    });

    document.querySelectorAll("button").forEach(function (button) {
        button.addEventListener("mousedown", function (event) {
            event.preventDefault();
        });
    });

    document.getElementById("nonSinhalaBtn").addEventListener("click", function () {
        applyTag(function (selectedText) {
            return "<sns>" + selectedText + "<ens>";
        });
    });

    document.getElementById("eosBtn").addEventListener("click", function () {
        applyTag(function (selectedText) {
            return selectedText + "<eos>";
        });
    });

    document.getElementById("psiBtn").addEventListener("click", function () {
        insertAtCursorOrSelection("<psi>");
    });

    document.getElementById("copyBtn").addEventListener("click", async function () {
        try {
            await navigator.clipboard.writeText(getText());
            setStatus("Final tagged text copied.");
        } catch (error) {
            output.select();
            document.execCommand("copy");
            setStatus("Final tagged text copied.");
        }
    });

    document.getElementById("downloadBtn").addEventListener("click", function () {
        const blob = new Blob([getText()], {
            type: "text/plain;charset=utf-8"
        });

        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");

        link.href = url;
        link.download = "tagged_text.txt";
        document.body.appendChild(link);
        link.click();

        document.body.removeChild(link);
        URL.revokeObjectURL(url);

        setStatus("Downloaded tagged_text.txt.");
    });

    document.getElementById("clearBtn").addEventListener("click", function () {
        setText("");
        savedSelection = null;
        setStatus("Editor cleared.");
    });
</script>

</body>
</html>
"""

editor_html = editor_html.replace(
    "__DEFAULT_TEXT__",
    json.dumps(DEFAULT_TEXT, ensure_ascii=False)
)

html(editor_html, height=850, scrolling=True)