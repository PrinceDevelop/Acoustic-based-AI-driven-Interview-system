let mediaRecorder;
let chunks = [];

navigator.mediaDevices.getUserMedia({ video: true, audio: true })
.then(stream => {
    document.getElementById("video").srcObject = stream;
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = e => chunks.push(e.data);

    mediaRecorder.onstop = () => {
        let blob = new Blob(chunks, { type: 'video/webm' });
        let formData = new FormData();
        formData.append("video", blob);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(res => res.text())
        .then(data => document.body.innerHTML = data);
    };
});

function startRecording() {
    chunks = [];
    mediaRecorder.start();
}

function stopRecording() {
    mediaRecorder.stop();
}