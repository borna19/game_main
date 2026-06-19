# 🎮 Palm Catch Game

## Project Overview

Palm Catch Game is an interactive web-based game that uses computer vision and hand-motion detection to control gameplay. Players catch falling objects using palm movements detected through a webcam. The project combines Flask, OpenCV, and MediaPipe-based motion detection to create a fun and engaging gaming experience directly in the browser.

The game tracks scores, detects collisions, manages game states, and provides a real-time interactive environment using webcam input.

---

## Features

* Real-Time Palm Motion Detection
* Webcam-Based Gameplay
* Object Catching Mechanics
* Live Score Tracking
* Collision Detection
* Game Reset Functionality
* Responsive User Interface
* Browser-Based Access
* Flask Backend Integration
* Computer Vision Processing

---

## Technologies Used

* Python
* Flask
* OpenCV
* MediaPipe
* HTML5
* CSS3
* JavaScript
* NumPy

---

## Project Structure

Palm-Catch-Game/

├── game/

│   ├── game_logic.py

│   ├── collision.py

│   └── scoring.py

├── static/

│   ├── css/

│   ├── js/

│   └── images/

├── templates/

│   └── index.html

├── app.py

├── requirements.txt

├── .gitattributes

└── README.md

---

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/palm-catch-game.git

cd palm-catch-game
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Application

```bash
python app.py
```

### 6. Open Browser

```text
http://127.0.0.1:5000
```

---

## Gameplay

### Player Controls

* Allow webcam access.
* Move your palm left or right.
* Catch falling objects using hand movements.
* Earn points for successful catches.
* Avoid missing objects to achieve a higher score.

### Game Mechanics

* Real-time hand tracking.
* Falling object generation.
* Collision detection between palm and objects.
* Dynamic score updates.
* Restart and reset options.

---

## Core Modules

### Motion Detection Module

* Webcam Access
* Hand Tracking
* Palm Position Detection
* Motion Analysis

### Game Engine Module

* Object Generation
* Collision Detection
* Score Calculation
* Game State Management

### User Interface Module

* Score Display
* Game Screen Rendering
* Responsive Layout
* Game Controls

---

## Requirements

```text
Flask
OpenCV-Python
MediaPipe
NumPy
Werkzeug
```

Install all requirements using:

```bash
pip install -r requirements.txt
```

---

## Future Enhancements

* Multiple Difficulty Levels
* High Score Leaderboard
* Multiplayer Mode
* Sound Effects and Music
* Power-Ups and Bonuses
* Mobile Device Support
* User Authentication
* Online Score Storage

---

## Author

Developed by: Barnali Bhowmik

---

## License

This project is created for educational and learning purposes. Feel free to modify and improve it as needed.

⭐ If you find this project useful, please give it a star.
