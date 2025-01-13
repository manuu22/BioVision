# 🌍 BioVision: Virtual Simulator for Plastic Bottle Detection  

We’ve developed an **interactive virtual simulator** for our **Plastic Bottle Detector**, allowing you to test the system in real time using your **webcam** or by uploading an image. As you interact with the simulator, you can **detect plastic bottles**, track your detections, and measure the total amount of plastic you’ve "recycled." 🚀  

**Try it out and see how much plastic you can collect!** ♻️  

![lettering](https://github.com/user-attachments/assets/aa7167bc-5ca3-4446-b23c-7b19841ced94)  

---

## 📌 Installation & Setup  

Ensure you have **Python 3.8 or later** installed and added to the system path.  

1️⃣ **Install the required dependencies:**  
```bash
pip install opencv-python ultralytics
```
2️⃣ **Run the simulator:**  
```bash
python plastic_bottle_detector.py
```

---

## 🔑 Login & Registration  
Before using the simulator, you’ll need to **log in or register** to start detecting plastic bottles. This will allow you to track your recycled plastic score over time.  

![imagen_reducida](https://github.com/user-attachments/assets/6e758983-8ebf-4ddc-9032-558f3c946334)


---

## 🎮 Detection Modes  
Choose between two detection modes:  

- **📷 Image Mode**: Upload an image, and the system will detect plastic bottles within it.  
- **🎥 Live Camera Mode**: Use your webcam for real-time plastic bottle detection.  

![imagen_reducida](https://github.com/user-attachments/assets/db191391-91af-440b-aa59-fabbc06a2e56)


To start live detection, run:  
```bash
python plastic_bottle_detector.py --live
```

---

## ♻️ Waste Collection & Recycling Score  
Every plastic bottle detected is **added to your recycling score**, allowing you to track how much plastic you've "recycled" while using the simulator.  

🌱 **Challenge yourself to collect as much plastic as possible and make a difference!**  

---

### 💡 Contribute & Support  
If you encounter any issues or have suggestions for improvement, feel free to **open an issue** or contribute to the project! 🚀  
