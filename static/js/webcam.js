// DOM elements
const video = document.getElementById('webcam');
const canvas = document.getElementById('canvas');
const captureBtn = document.getElementById('capture-btn');
const webcamResult = document.getElementById('webcam-result');
const bubblesContainer = document.getElementById('bubbles'); // Added for bubbles

// Set up canvas
const ctx = canvas.getContext('2d');

// Track which camera is in use (front or back)
let usingFrontCamera = true;
let currentStream = null;

// Initialize webcam
async function initWebcam(useBackCamera = false) {
  if (currentStream) {
    currentStream.getTracks().forEach(track => track.stop());
  }

  try {
    const constraints = {
      video: {
        width: { ideal: 480 },
        height: { ideal: 360 },
        facingMode: useBackCamera ? "environment" : "user"
      }
    };

    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    video.srcObject = stream;
    currentStream = stream;

    video.onloadedmetadata = () => {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
    };

    captureBtn.disabled = false;
    usingFrontCamera = !useBackCamera;
  } catch (err) {
    console.error("Error accessing webcam:", err);
    webcamResult.style.display = 'block';
    webcamResult.innerHTML = `
      <div class="error-message">
        Could not access camera. Please make sure you've allowed camera access.
      </div>
    `;
    captureBtn.disabled = true;
  }
}

// Capture image and send for prediction
function captureAndSend() {
  captureBtn.disabled = true;
  captureBtn.textContent = 'Analyzing...';

  webcamResult.style.display = 'block';
  webcamResult.innerHTML = `
    <div class="loading"><div></div><div></div></div>
    <p>Analyzing image...</p>
  `;

  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  canvas.toBlob((blob) => {
    const formData = new FormData();
    formData.append('file', blob, 'webcam.jpg');

    fetch('/predict', {
      method: 'POST',
      body: formData
    })
    .then(response => {
      if (!response.ok) throw new Error('Server error');
      return response.json();
    })
    .then(data => {
      if (data.error) {
        webcamResult.innerHTML = `
          <div class="error-message">
            ${data.error}
          </div>
        `;
        return;
      }

      // Show full prediction + message
      const isGrass = data.prediction.toLowerCase().includes('grass');
      webcamResult.innerHTML = `
        <h3 class="result-title">Result:</h3>
        <div class="result ${isGrass ? '' : 'not-grass'}">
          <p class="prediction">${data.prediction}</p>
          <p class="message" style="font-weight: bold; margin-top: 0.5rem;">${data.message}</p>
        </div>
      `;
    })
    .catch(err => {
      console.error("Error during prediction:", err);
      webcamResult.innerHTML = `
        <div class="error-message">
          Error during prediction. Please try again.
        </div>
      `;
    })
    .finally(() => {
      captureBtn.disabled = false;
      captureBtn.textContent = 'Capture & Identify';
    });
  }, 'image/jpeg', 0.9);
}

// BUBBLE EFFECT CODE
function createBubble() {
  const bubble = document.createElement('div');
  const size = Math.random() * 40 + 10; // 10px to 50px
  bubble.classList.add('bubble');
  bubble.style.width = `${size}px`;
  bubble.style.height = `${size}px`;
  bubble.style.left = `${Math.random() * 100}%`;
  bubble.style.animationDuration = `${8 + Math.random() * 4}s`;
  bubble.style.backgroundColor = `rgba(255, 255, 255, ${Math.random() * 0.2 + 0.05})`;

  bubblesContainer.appendChild(bubble);

  // Remove bubble after animation duration to keep DOM clean
  setTimeout(() => {
    bubble.remove();
  }, 12000);
}

// Generate bubbles at intervals
setInterval(createBubble, 500);

// Attach events
captureBtn.addEventListener('click', captureAndSend);

// Init on load
document.addEventListener('DOMContentLoaded', () => {
  initWebcam();
});
