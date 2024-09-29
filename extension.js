const vscode = require('vscode');

function activate(context) {
    let disposable = vscode.commands.registerCommand('extension.showSuggestions', () => {
        const activeEditor = vscode.window.activeTextEditor;

        if (!activeEditor) {
            vscode.window.showErrorMessage('No active text editor found.');
            return;
        }

        const document = activeEditor.document;
        const fileContent = document.getText();

        const panel = vscode.window.createWebviewPanel(
            'suggestions',
            'Helpful Suggestions',
            vscode.ViewColumn.Two,
            { enableScripts: true }
        );

        panel.webview.html = getWebviewContent(fileContent);

        panel.webview.onDidReceiveMessage(
            message => {
                switch (message.command) {
                    case 'askLLM':
                        vscode.window.showInformationMessage(`User's Question: ${message.question}`);
                        break;
                }
            },
            undefined,
            context.subscriptions
        );
    });

    context.subscriptions.push(disposable);
}

function getWebviewContent(fileContent) {
    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wolverine Code Companion!</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <style>
        /* Maize and Blue Color Theme */
        body {
            background-color: #00274C; /* Blue */
            color: #FFCB05; /* Maize */
            font-family: 'Fira Code', 'Consolas', 'Input', 'DejaVu Sans Mono', 'MonoLisa', monospace;
            padding: 20px;
        }
        h1 {
            color: #FFCB05; /* Maize */
            font-size: 2.5rem;
            text-align: center;
            margin-bottom: 30px;
        }
        .code-container {
            background-color: #041E42; /* Darker Blue */
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            margin-bottom: 30px;
        }
        pre {
            white-space: pre-wrap;
            word-wrap: break-word;
            color: #FFCB05; /* Maize */
            font-size: 0.95rem;
            line-height: 1.6;
        }
        .suggestion-card {
            background-color: #01213A; /* Even Darker Blue */
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }
        .suggestion-card h4 {
            color: #FFCB05; /* Maize */
            margin-bottom: 15px;
        }
        .chat-container {
            margin-top: 40px;
            background-color: #041E42; /* Darker Blue */
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }
        .chat-container h4 {
            color: #FFCB05; /* Maize */
            margin-bottom: 15px;
        }
        .chat-input {
            width: 100%;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
            border: 1px solid #555;
            background-color: #00274C; /* Blue */
            color: #FFCB05; /* Maize */
        }
        .btn-primary {
            background-color: #FFCB05; /* Maize */
            border-color: #FFCB05;
            color: #00274C; /* Blue */
        }
        .btn-primary:hover {
            background-color: #FFDB33; /* Lighter Maize */
            border-color: #FFDB33;
        }
    </style>
</head>
<body>
    <h1>Wolverine Code Companion</h1>

    <!-- Show the current file content -->
    <div class="code-container">
        <h4>Your Code: </h4>
        <pre>${fileContent.replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\n/g, '<br>')}</pre>
    </div>

    <!-- Placeholder for suggestions (can be integrated with LLM) -->
    <div class="suggestion-card">
        <h4>Suggestion:</h4>
        <p>Based on your code, consider refactoring this function to improve readability and performance.</p>
    </div>

    <!-- Chat Interface -->
    <div class="chat-container">
        <h4>Need More Help? Ask Here!</h4>
        <textarea id="chat-input" class="chat-input" rows="4" placeholder="Ask a question..."></textarea>
        <button id="ask-btn" class="btn btn-primary">Ask an expert!</button>
    </div>

    <script>
        const vscode = acquireVsCodeApi();

        document.getElementById('ask-btn').addEventListener('click', () => {
            const question = document.getElementById('chat-input').value;
            if (question.trim() !== "") {
                vscode.postMessage({ command: 'askLLM', question });
                document.getElementById('chat-input').value = ''; // Clear input after asking
            } else {
                alert('Please type a question before asking!');
            }
        });
    </script>
</body>
</html>
    `;
}

function deactivate() {}
module.exports = { activate, deactivate };
