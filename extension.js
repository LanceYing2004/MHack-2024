const vscode = require('vscode');

// Create a custom output channel for your extension
const outputChannel = vscode.window.createOutputChannel("Wolverine Code Companion");

// Function to handle fetching code from the active editor
const handleCodeAnalysis = () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showInformationMessage("No active editor found.");
        return;
    }

    const document = editor.document;
    const codeContent = document.getText(); // Fetch all the text from the active file

    if (codeContent) {
        outputChannel.appendLine("Captured code:");
        outputChannel.appendLine(codeContent); // Write the captured code to the output channel
        outputChannel.show(); // Show the output channel in the UI
        vscode.window.showInformationMessage("Code captured successfully! Check the 'Wolverine Code Companion' output channel.");
    } else {
        vscode.window.showInformationMessage("No code found in the active file.");
    }
};

function activate(context) {
    let disposable = vscode.commands.registerCommand('extension.analyzeCode', handleCodeAnalysis);
    context.subscriptions.push(disposable);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
