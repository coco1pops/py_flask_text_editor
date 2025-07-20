document.getElementById('add-markdown').addEventListener('click', () => {
    // Create a container for the Markdown editor
    const editorContainer = document.createElement('div');
    editorContainer.style.marginBottom = '20px';

    // Create a textarea for Markdown input
    const textarea = document.createElement('textarea');
    textarea.placeholder = 'Write your Markdown here...';

    // Create a preview area
    const preview = document.createElement('div');
    preview.className = 'preview';
    preview.innerHTML = '<em>Preview will appear here...</em>';

    // Update preview on input
    textarea.addEventListener('input', () => {
      preview.innerHTML = marked.parse(textarea.value); // Using the `marked` library
    });

    // Append textarea and preview to the container
    editorContainer.appendChild(textarea);
    editorContainer.appendChild(preview);

    // Append the container to the main markdown container
    document.getElementById('markdown-container').appendChild(editorContainer);
});