from flask import Flask, render_template, Response
import cv2
import numpy as np
import random
import time
import math

app = Flask(__name__)

class ImprovedPalmCatch:
    def __init__(self):
        self.use_mediapipe = False
        print("Using basic motion detection")
        
        # Game parameters
        self.width, self.height = 640, 480
        
        # Web parameters
        self.web_radius = 50
        self.web_center_x = self.width // 2
        self.web_center_y = self.height - 80
        
        # Ball parameters
        self.ball_radius = 15
        self.ball_speed = 3
        
        # Celebration effects
        self.poppers = []
        self.balloons = []
        
        self.reset_game()
    
    def reset_game(self):
        """Reset game to initial state"""
        self.balls = []
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.showing_score = False
        self.score_display_time = 0
        self.last_ball_time = time.time()
        self.ball_spawn_rate = 1.5
        self.hand_detected = False
        
        # Clear celebration effects
        self.poppers = []
        self.balloons = []
    
    def detect_hand_basic(self, frame):
        """Simplified basic hand detection"""
        if not hasattr(self, 'prev_frame'):
            self.prev_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return self.web_center_x, self.web_center_y, None
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (15, 15), 0)
        
        # Calculate frame difference
        frame_diff = cv2.absdiff(self.prev_frame, gray)
        _, thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)
        
        self.prev_frame = gray
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Find largest contour in lower screen area
        largest_contour = None
        max_area = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 300 < area < 5000:  # Reasonable hand size
                x, y, w, h = cv2.boundingRect(contour)
                # Focus on lower part of screen where hands usually are
                if y > self.height // 3:
                    if area > max_area:
                        max_area = area
                        largest_contour = contour
        
        if largest_contour is not None:
            x, y, w, h = cv2.boundingRect(largest_contour)
            cx = x + w // 2
            cy = y + h // 2
            
            # Keep within bounds
            cx = max(self.web_radius, min(cx, self.width - self.web_radius))
            cy = max(self.web_radius, min(cy, self.height - self.web_radius))
            
            return cx, cy, largest_contour
        
        return self.web_center_x, self.web_center_y, None
    
    def draw_simple_web(self, frame, center_x, center_y, hand_detected):
        """Draw a simple web"""
        if not hand_detected:
            cv2.putText(frame, "Show your HAND to play!", 
                       (self.width//2 - 140, self.height//2),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            return
        
        # Web circle
        cv2.circle(frame, (center_x, center_y), self.web_radius, (0, 255, 255), 2)
        
        # Spider
        cv2.circle(frame, (center_x, center_y), 8, (0, 0, 0), -1)
        cv2.circle(frame, (center_x, center_y), 6, (255, 0, 0), -1)
    
    def spawn_ball(self):
        """Spawn balls"""
        current_time = time.time()
        if (len(self.balls) < 3 and 
            current_time - self.last_ball_time > self.ball_spawn_rate):
            
            ball_types = ['normal', 'bonus', 'bomb']
            ball_type = random.choice(ball_types)
            
            if ball_type == 'normal':
                color = (255, 0, 0)  # Red
                speed = self.ball_speed
                points = 10
            elif ball_type == 'bonus':
                color = (255, 255, 0)  # Yellow
                speed = self.ball_speed * 0.7
                points = 25
            else:  # bomb
                color = (100, 100, 100)  # Gray
                speed = self.ball_speed * 1.1
                points = -1
            
            self.balls.append({
                'x': random.randint(self.ball_radius, self.width - self.ball_radius),
                'y': -self.ball_radius,
                'type': ball_type,
                'color': color,
                'speed': speed,
                'points': points,
                'size': self.ball_radius
            })
            
            self.last_ball_time = current_time
    
    def update_balls(self, web_x, web_y, hand_detected):
        """Update ball positions"""
        if not hand_detected:
            return
            
        balls_to_remove = []
        
        for i, ball in enumerate(self.balls):
            ball['y'] += ball['speed']
            
            # Collision detection
            distance = math.sqrt((ball['x'] - web_x)**2 + (ball['y'] - web_y)**2)
            if distance < self.web_radius + ball['size']:
                balls_to_remove.append(i)
                
                if ball['type'] == 'bomb':
                    self.lives = max(0, self.lives - 1)
                else:
                    self.score += ball['points']
                    self.create_catch_effect(web_x, web_y, ball['color'])
                
                if self.lives <= 0:
                    self.game_over = True
            
            # Remove balls that fall off screen
            if ball['y'] - ball['size'] > self.height:
                balls_to_remove.append(i)
                if ball['type'] != 'bomb':
                    self.lives = max(0, self.lives - 1)
                    if self.lives <= 0:
                        self.game_over = True
        
        # Remove balls
        for i in sorted(balls_to_remove, reverse=True):
            if i < len(self.balls):
                self.balls.pop(i)
    
    def create_catch_effect(self, x, y, color):
        """Create catch effect"""
        for _ in range(5):
            self.poppers.append({
                'x': x,
                'y': y,
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-4, -1),
                'color': color,
                'life': 1.0
            })
    
    def create_score_celebration(self):
        """Create celebration"""
        for _ in range(8):
            self.balloons.append({
                'x': random.randint(0, self.width),
                'y': self.height + 30,
                'vy': random.uniform(-1.5, -0.5),
                'color': (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)),
                'radius': random.randint(20, 30)
            })
    
    def update_effects(self):
        """Update effects"""
        # Update poppers
        i = 0
        while i < len(self.poppers):
            popper = self.poppers[i]
            popper['x'] += popper['vx']
            popper['y'] += popper['vy']
            popper['vy'] += 0.1
            popper['life'] -= 0.03
            
            if popper['life'] <= 0:
                self.poppers.pop(i)
            else:
                i += 1
        
        # Update balloons
        i = 0
        while i < len(self.balloons):
            balloon = self.balloons[i]
            balloon['y'] += balloon['vy']
            
            if balloon['y'] < -50:
                self.balloons.pop(i)
            else:
                i += 1
    
    def draw_balls(self, frame):
        """Draw balls"""
        for ball in self.balls:
            cv2.circle(frame, (int(ball['x']), int(ball['y'])), 
                      ball['size'], ball['color'], -1)
            cv2.circle(frame, (int(ball['x']), int(ball['y'])), 
                      ball['size'], (255, 255, 255), 1)
            
            if ball['type'] == 'bonus':
                cv2.putText(frame, "+", (int(ball['x'])-5, int(ball['y'])+5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
            elif ball['type'] == 'bomb':
                cv2.putText(frame, "!", (int(ball['x'])-3, int(ball['y'])+3),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 1)
    
    def draw_effects(self, frame):
        """Draw effects"""
        for popper in self.poppers:
            alpha = popper['life']
            color = [int(c * alpha) for c in popper['color']]
            size = int(3 * alpha)
            if size > 0:
                cv2.circle(frame, (int(popper['x']), int(popper['y'])), size, color, -1)
        
        for balloon in self.balloons:
            cv2.circle(frame, (int(balloon['x']), int(balloon['y'])), 
                      balloon['radius'], balloon['color'], -1)
            cv2.circle(frame, (int(balloon['x']), int(balloon['y'])), 
                      balloon['radius'], (255, 255, 255), 1)
    
    def draw_game(self, frame, web_x, web_y, hand_detected):
        """Draw all game elements"""
        # Draw web
        self.draw_simple_web(frame, web_x, web_y, hand_detected)
        
        # Draw balls
        self.draw_balls(frame)
        
        # Draw effects
        self.draw_effects(frame)
        
        # UI
        cv2.putText(frame, f"SCORE: {self.score}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        lives_text = f"LIVES: {self.lives}"
        cv2.putText(frame, lives_text, (self.width - 120, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        
        # Game over
        if self.game_over and not self.showing_score:
            self.showing_score = True
            self.score_display_time = time.time()
            self.create_score_celebration()
        
        if self.showing_score:
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (self.width, self.height), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
            
            cv2.putText(frame, "GAME OVER", 
                       (self.width//2 - 100, self.height//2 - 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            
            cv2.putText(frame, f"Score: {self.score}", 
                       (self.width//2 - 60, self.height//2),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            
            cv2.putText(frame, "Press R to Restart", 
                       (self.width//2 - 80, self.height//2 + 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            self.update_effects()

# Global game instance
game_instance = ImprovedPalmCatch()

def generate_frames():
    cap = None
    try:
        # Try different camera indices
        for camera_index in [0, 1, 2]:
            cap = cv2.VideoCapture(camera_index)
            if cap.isOpened():
                print(f"🎥 Camera found at index {camera_index}")
                break
            else:
                if cap:
                    cap.release()
        
        if not cap or not cap.isOpened():
            print("📷 No camera found - using test mode")
            # Create test frames with better design
            while True:
                # Create a more attractive test frame
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                frame[:] = [40, 40, 60]  # Dark blue background
                
                # Add some visual elements
                cv2.circle(frame, (320, 200), 80, (0, 255, 136), 3)
                cv2.circle(frame, (320, 200), 60, (0, 204, 255), 2)
                
                # Add text
                cv2.putText(frame, "PALM CATCH GAME", 
                           (640//2 - 180, 120),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 136), 2)
                cv2.putText(frame, "Camera Not Detected", 
                           (640//2 - 140, 240),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, "Please connect a webcam", 
                           (640//2 - 150, 280),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                cv2.putText(frame, "Then refresh the page", 
                           (640//2 - 120, 310),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                
                # Add some animated elements
                current_time = time.time()
                pulse = int(50 + 20 * math.sin(current_time * 3))
                cv2.circle(frame, (320, 200), pulse, (0, 204, 255), 2)
                
                ret, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            while True:
                success, frame = cap.read()
                if not success:
                    break
                else:
                    frame = cv2.flip(frame, 1)
                    
                    # Detect hand
                    web_x, web_y, hand_contour = game_instance.detect_hand_basic(frame)
                    game_instance.hand_detected = hand_contour is not None
                    
                    if not game_instance.game_over:
                        game_instance.spawn_ball()
                        game_instance.update_balls(web_x, web_y, game_instance.hand_detected)
                        game_instance.update_effects()
                    
                    game_instance.draw_game(frame, web_x, web_y, game_instance.hand_detected)
                    
                    ret, buffer = cv2.imencode('.jpg', frame)
                    frame_bytes = buffer.tobytes()
                    
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    except Exception as e:
        print(f"❌ Error in generate_frames: {e}")
        # Return error frame
        while True:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            frame[:] = [60, 40, 40]  # Dark red background for error
            
            cv2.putText(frame, "ERROR", 
                       (640//2 - 60, 200),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(frame, "Check console for details", 
                       (640//2 - 140, 250),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        if cap:
            cap.release()
            
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/game')
def game():
    return render_template('game.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/reset_game')
def reset_game():
    game_instance.reset_game()
    return "Game reset"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)