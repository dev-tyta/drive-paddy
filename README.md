---
title: Drive Paddy - Drowsiness Detection
emoji: 🚗
colorFrom: green
colorTo: blue
sdk: streamlit
app_file: drive_paddy/main.py
pinned: false
---

<div align="center">
  <img src="https://em-content.zobj.net/source/samsung/380/automobile_1f697.png" alt="Car Emoji" width="100"/>
  <h1>Drive Paddy</h1>
  <p><strong>Your AI-Powered Drowsiness Detection Assistant</strong></p>
  
  <p>
    <a href="#"><img alt="License" src="https://img.shields.io/badge/License-MIT-yellow.svg"/></a>
    <a href="#"><img alt="Python" src="https://img.shields.io/badge/Python-3.9+-blue.svg"/></a>
    <a href="#"><img alt="Streamlit" src="https://img.shields.io/badge/Streamlit-1.35.0-red.svg"/></a>
  </p>

  <p>A real-time system to enhance driver safety by detecting signs of drowsiness using advanced computer vision and deep learning techniques.</p>

  <!-- *A GIF of the application running would be highly effective here.*
  
  **[GIF of Drive Paddy in Action]** -->
</div>

---

## 🌟 Features

Drive Paddy employs a sophisticated, multi-faceted approach to ensure robust and reliable drowsiness detection.

-   **Hybrid Detection Strategy**: Combines traditional computer vision techniques with deep learning for superior accuracy.
-   **Multi-Signal Analysis**:
    -   **👀 Eye Closure Detection**: Measures Eye Aspect Ratio (EAR) to detect prolonged blinks and microsleeps.
    -   **🥱 Yawn Detection**: Measures Mouth Aspect Ratio (MAR) to identify driver fatigue.
    -   **😴 Head Pose Estimation**: Tracks head pitch and yaw to detect nodding off or inattentiveness.
    -   **🧠 Deep Learning Inference**: Utilizes a pre-trained `EfficientNet-B7` model for an additional layer of analysis.
-   **Dynamic AI-Powered Alerts**: Leverages the Gemini API and gTTS for clear, context-aware voice alerts that are played directly in the user's browser.
-   **Low-Light Warning**: Automatically detects poor lighting conditions that could affect detection accuracy and notifies the user.
-   **Web-Based Interface**: Built with Streamlit for a user-friendly and accessible experience.
-   **Configurable**: All detection thresholds and model weights can be easily tuned via a central `config.yaml` file.

---

## 🛠️ How It Works

The system processes a live video feed from the user's webcam and calculates a weighted "drowsiness score" based on the configured detection strategy.

1.  **Video Processing**: The `streamlit-webrtc` component captures the camera feed.
2.  **Concurrent Detection**: The `HybridProcessor` runs two pipelines in parallel for maximum efficiency:
    -   **Geometric Analysis (`geometric.py`)**: Uses `MediaPipe` to detect facial landmarks and calculate EAR, MAR, and head position in real-time.
    -   **Deep Learning Inference (`cnn_model.py`)**: Uses a `dlib` face detector and a `PyTorch` model to classify the driver's state. This is run on a set interval to optimize performance.
3.  **Scoring & Alerting**: The results are weighted and combined. If the score exceeds a set threshold, an alert is triggered.
4.  **AI Voice Generation**: The `GeminiAlertSystem` sends a prompt to the Gemini API, generates a unique voice message using `gTTS`, and sends the audio data to the browser for playback.

---

## 🚀 Setup and Installation

Follow these steps to set up and run Drive Paddy on your local machine.

### 1. Clone the Repository

```bash
git clone https://github.com/<dev-tyta>/drive-paddy.git
cd drive-paddy
```

### 2. Set Up a Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 3. Install Dependencies

Install all required Python packages from the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 4. Download the CNN Model

Run the provided script to download the pre-trained model from Hugging Face Hub.

```bash
python download_model.py
```

### 5. Configure Environment Variables

Create a `.env` file by copying the example file.

```bash
cp .env.example .env
```

Now, open the `.env` file and add your Gemini API key:

```
GEMINI_API_KEY="YOUR_GEMINI_API_KEY_GOES_HERE"
```

---

## ⚙️ Configuration

The application's behavior can be fine-tuned via the `config.yaml` file. You can adjust detection thresholds, change the detection strategy (`geometric`, `cnn_model`, or `hybrid`), and modify the weights for the hybrid scoring system without touching the source code.

---

## ▶️ Usage

To run the application, execute the following command from the root directory of the project:

```bash
streamlit run drive_paddy/main.py
```

Open your web browser and navigate to the local URL provided by Streamlit (usually `http://localhost:8501`).

---