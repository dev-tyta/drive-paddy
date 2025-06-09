# download_model.py
import os
from huggingface_hub import hf_hub_download

# --- Configuration ---
# Details from your Hugging Face repository screenshot.
REPO_ID = "Testys/drowsiness-detection-model"
FILENAME = "best_model_efficientnet_b7.pth"
LOCAL_DIR = "models"

def download_model():
    """
    Downloads the specified model file from Hugging Face Hub
    and saves it to the local models/ directory.
    """
    print(f"Downloading model '{FILENAME}' from repository '{REPO_ID}'...")

    # Ensure the local directory exists.
    if not os.path.exists(LOCAL_DIR):
        os.makedirs(LOCAL_DIR)
        print(f"Created directory: {LOCAL_DIR}")

    try:
        # Download the file.
        # local_dir_use_symlinks=False ensures the file is copied to your directory
        # instead of just pointing to the cache.
        model_path = hf_hub_download(
            repo_id=REPO_ID,
            filename=FILENAME,
            local_dir=LOCAL_DIR,
            local_dir_use_symlinks=False,
            # token=True # Use token for private repos, can be omitted for public ones
        )
        print(f"\nModel downloaded successfully!")
        print(f"Saved to: {model_path}")

    except Exception as e:
        print(f"\nAn error occurred during download: {e}")
        print("Please check the repository ID, filename, and your network connection.")

if __name__ == "__main__":
    download_model()
