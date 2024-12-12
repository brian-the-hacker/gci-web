const dragDropArea = document.getElementById('dragDropArea');
const imageInput = document.getElementById('image');
const imageLabel = document.getElementById('imageLabel');
const imageName = document.getElementById('imageName');
const fileName = document.getElementById('fileName');

dragDropArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    dragDropArea.classList.add('border-indigo-500', 'bg-indigo-50');
});

dragDropArea.addEventListener('dragleave', () => {
    dragDropArea.classList.remove('border-indigo-500', 'bg-indigo-50');
});

dragDropArea.addEventListener('drop', (e) => {
    e.preventDefault();
    dragDropArea.classList.remove('border-indigo-500', 'bg-indigo-50');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        imageInput.files = files;
        updateImageInfo();
    }
});

function updateImageInfo() {
    const file = imageInput.files[0];
    if (file) {
        imageName.classList.remove('hidden');
        fileName.textContent = file.name;
    } else {
        imageName.classList.add('hidden');
    }
}
