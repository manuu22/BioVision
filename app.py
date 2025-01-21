
import os
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
import sqlite3
import random
import pygame
import cv2
from PIL import Image, ImageTk
from ultralytics import YOLO

#USER DATABASE PATH
DB_DIR = "data"
DB_NAME = "app_data.db"
DB_PATH = os.path.join(DB_DIR, DB_NAME)
os.makedirs(DB_DIR, exist_ok=True)


def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            grams INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def register_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
    exists = cursor.fetchone()
    if exists:
        conn.close()
        return False
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()
    return True

def login_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    row = cursor.fetchone()
    conn.close()
    return True if row else False

def add_record(username, grams):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO records (username, grams) VALUES (?, ?)", (username, grams))
    conn.commit()
    conn.close()

def get_leaderboard():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT username, SUM(grams) as total_grams
        FROM records
        GROUP BY username
        ORDER BY total_grams DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_all_users_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT username, IFNULL(SUM(grams), 0) as total_grams
        FROM records
        GROUP BY username
        ORDER BY username ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

class InitWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Welcome")
        self.master.geometry("800x600")
        self.init_image = Image.open("bin/init.png")
        self.init_image = self.init_image.resize((800, 600), Image.Resampling.LANCZOS)
        self.init_tk = ImageTk.PhotoImage(self.init_image)
        self.label_bg = tk.Label(self.master, image=self.init_tk)
        self.label_bg.pack(fill=tk.BOTH, expand=True)
        self.master.bind("<Button-1>", self.init_click)

    def init_click(self, event):
        x, y = event.x, event.y
        #Login
        if 281 <= x <= 517 and 238 <= y <= 296:
            self.open_login_form()
        #Register
        elif 282 <= x <= 516 and 323 <= y <= 382:
            self.open_register_form()

    def open_login_form(self):
        login_win = Toplevel(self.master)
        login_win.title("Log in")
        login_win.geometry("300x200")

        tk.Label(login_win, text="User:").pack(pady=5)
        entry_user = tk.Entry(login_win)
        entry_user.pack()

        tk.Label(login_win, text="Password:").pack(pady=5)
        entry_pass = tk.Entry(login_win, show="*")
        entry_pass.pack()

        def do_login():
            username = entry_user.get()
            password = entry_pass.get()
            if login_user(username, password):
                messagebox.showinfo("Logged in", f"Welcome, {username}!")
                login_win.destroy()
                self.open_simulator(username)
            else:
                messagebox.showerror("Error", "Wrong user name or password")

        tk.Button(login_win, text="Log in", command=do_login).pack(pady=10)

    def open_register_form(self):
        reg_win = Toplevel(self.master)
        reg_win.title("Register")
        reg_win.geometry("300x200")

        tk.Label(reg_win, text="User:").pack(pady=5)
        entry_user = tk.Entry(reg_win)
        entry_user.pack()

        tk.Label(reg_win, text="Password:").pack(pady=5)
        entry_pass = tk.Entry(reg_win, show="*")
        entry_pass.pack()

        def do_register():
            username = entry_user.get()
            password = entry_pass.get()
            if not username or not password:
                messagebox.showwarning("Insert user name and password")
                return
            if register_user(username, password):
                messagebox.showinfo("Registered", 
                                    f"User {username} is now registered.")
                reg_win.destroy()
            else:
                messagebox.showerror("Error", "User name already taken")

        tk.Button(reg_win, text="Register", command=do_register).pack(pady=10)

    def open_simulator(self, username):
        self.master.destroy()
        main_root = tk.Tk()
        app = GarbageCollectorSim(main_root, username)
        main_root.protocol("WM_DELETE_WINDOW", app.close)
        main_root.mainloop()


class GarbageCollectorSim:
    def __init__(self, root, username):
        self.root = root
        self.root.title("BioVision")
        self.root.geometry("800x600")
        self.root.configure(bg='white')
        
        self.username = username
        self.video_mode = False
        self.custom_image_mode = False
        self.cap = None

        self.bounding_boxes = []
        self.selected_boxes = set()  
        self.bottle_counter = 0
        
        # YOLO model path
        self.model = YOLO("yolo_models/final.pt")
        
        # Confidence thresholds
        self.image_confidence_threshold = 0.4
        self.video_confidence_threshold = 0.5
   
        # Images and sounds paths
        self.background_image_path = "bin/images.png"
        self.camera_image_path = "bin/camera.png"
        self.collect_sound = "bin/collect.mp3"
        
        pygame.mixer.init()
        
        self.main_menu()

    def main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.update()
        self.menu_image = Image.open("bin/menu3.png")
        self.menu_image = self.menu_image.resize((800, 600), Image.Resampling.LANCZOS)
        self.menu_tk = ImageTk.PhotoImage(self.menu_image)
        self.menu_label = tk.Label(self.root, image=self.menu_tk)
        self.menu_label.pack(fill=tk.BOTH, expand=True)
        self.root.unbind("<Button-1>")
        self.root.bind("<Button-1>", self.menu_click)

    def menu_click(self, event):
        x, y = event.x, event.y

        # Camera mode
        if 281 <= x <= 517 and 238 <= y <= 296:
            self.camera_mode()
        # Custom image mode
        elif 282 <= x <= 516 and 323 <= y <= 382:
            self.image_mode()
        # Stats button
        elif 337 <= x <= 467 and 413 <= y <= 436:
            self.show_all_users_stats()

   #CUSTOM IMAGE MODE
    def image_mode(self):
        self.close_camera()
        self.video_mode = False
        self.custom_image_mode = True
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.png")]
        )
        if not file_path:
            self.main_menu()
            return

        self.current_frame = cv2.imread(file_path)

        self.selected_boxes.clear()
        self.show_simulator(image_path=file_path)

    #CAMERA MODE
    def camera_mode(self):
        self.close_camera()
        self.video_mode = True
        self.custom_image_mode = False
        self.cap = cv2.VideoCapture(0)
        self.show_simulator()

    def show_simulator(self, image_path=None):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.update()
        self.display_background()
        leaderboard_btn = tk.Button(self.root, text="Leaderboard", command=self.show_leaderboard)
        leaderboard_btn.place(x=20, y=20)
        if self.video_mode:
            self.process_video()
        elif self.custom_image_mode and image_path:
            self.detect_and_display(self.current_frame)

      # Count bottles
        if self.custom_image_mode or self.video_mode:
            self.counter_label = tk.Label(self.root, text=f"{self.bottle_counter}",
                                          font=("Helvetica", 14), bg="white", fg="black")
            self.counter_label.place(x=655, y=198)

        if self.custom_image_mode:
            self.root.bind("<Button-1>", self.handle_custom_click)
        elif self.video_mode:
            self.root.bind("<Button-1>", self.camera_click)
        else:
            self.root.unbind("<Button-1>")

    def display_background(self):
        if self.video_mode:
            bg_image = Image.open(self.camera_image_path)
        else:
            bg_image = Image.open(self.background_image_path)
        bg_image = bg_image.resize((800, 600), Image.Resampling.LANCZOS)
        bg_tk = ImageTk.PhotoImage(bg_image)
        self.background_label = tk.Label(self.root, image=bg_tk)
        self.background_label.image = bg_tk
        self.background_label.place(x=0, y=0)

    #BACK TO MENU
    def return_to_menu(self):
        self.close_camera()
        self.current_frame = None
        self.bounding_boxes = []
        self.selected_boxes.clear()
        self.bottle_counter = 0
        self.main_menu()

    def handle_custom_click(self, event):
        x, y = event.x, event.y
        # Botón "volver"
        if 566 <= x <= 754 and 271 <= y <= 317:
            self.return_to_menu()
        # Botón "cargar otra imagen"
        elif 568 <= x <= 753 and 338 <= y <= 382:
            self.image_mode()
        # Botón "calcular plástico"
        elif 570 <= x <= 754 and 404 <= y <= 469:
            self.calculate_recycled_plastic()

        self.bottle_collection(x, y)


    def camera_click(self, event):
        x, y = event.x, event.y
        #Menu button
        if 567 <= x <= 756 and 271 <= y <= 317:
            self.return_to_menu()
        #Calculate button
        elif 567 <= x <= 756 and 341 <= y <= 409:
            self.calculate_recycled_plastic()
        self.bottle_collection(x, y)

    def bottle_collection(self, x, y):
        for i, (bx1, by1, bx2, by2) in enumerate(self.bounding_boxes):
            if bx1 <= x <= bx2 and by1 <= y <= by2:
                if i not in self.selected_boxes:
                    self.selected_boxes.add(i)
                    self.bottle_counter += 1
                    if hasattr(self, "counter_label"):
                        self.counter_label.config(text=f"{self.bottle_counter}")
                    pygame.mixer.Sound(self.collect_sound).play()
        if self.custom_image_mode:
            self.detect_and_display(self.current_frame)

    def process_video(self):
        if not self.video_mode or self.cap is None:
            return
        ret, frame = self.cap.read()
        if ret:
            self.detect_and_display(frame)
        self.video_loop = self.root.after(10, self.process_video)

    def detect_and_display(self, frame):
        frame = self.resize_images(frame, 104, 166, 450, 425)
        if self.video_mode:
            current_threshold = self.video_confidence_threshold
        else:
            current_threshold = self.image_confidence_threshold
            
        results = self.model(frame)
        detections = results[0].boxes
        self.bounding_boxes = []

        for i, box in enumerate(detections):
            confidence = box.conf[0].item()
            if confidence >= current_threshold:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                self.bounding_boxes.append((x1, y1, x2, y2))

        for i, (x1, y1, x2, y2) in enumerate(self.bounding_boxes):
            color = (0, 255, 0) if i not in self.selected_boxes else (255, 0, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, "Bottle", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imgtk = ImageTk.PhotoImage(Image.fromarray(frame))
        self.video_frame = tk.Label(self.root, image=imgtk, bg="white")
        self.video_frame.imgtk = imgtk
        self.video_frame.place(x=104, y=166)

    def resize_images(self, image, x1, y1, x2, y2):
        target_width = x2 - x1
        target_height = y2 - y1
        h, w = image.shape[:2]
        scale = min(target_width / w, target_height / h)
        new_width = int(w * scale)
        new_height = int(h * scale)
        return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

    def calculate_recycled_plastic(self):
        if self.bottle_counter == 0:
            messagebox.showinfo("Plastic Calculation", "No bottles collected yet!")
            return
        total_grams = sum(random.randint(10, 20) for _ in range(self.bottle_counter))
        add_record(self.username, total_grams)
        messagebox.showinfo("Plastic Calculation",
                            f"Recycled plastic: {total_grams} grams\n")
        self.bottle_counter = 0
        if hasattr(self, "counter_label"):
            self.counter_label.config(text="0")

    def show_leaderboard(self):
        records = get_leaderboard()
        leaderboard_window = tk.Toplevel(self.root)
        leaderboard_window.title("Leaderboard")
        leaderboard_window.geometry("300x300")
        tk.Label(leaderboard_window, text="--- Leaderbord ---",
                 font=("Helvetica", 12, "bold")).pack(pady=5)
        for i, (user, grams) in enumerate(records, start=1):
            tk.Label(leaderboard_window,
                     text=f"{i}. {user} - {grams} g").pack(anchor="w", padx=20)

    def show_all_users_stats(self):
        rows = get_all_users_stats()
        stats_window = tk.Toplevel(self.root)
        stats_window.title("User stats")
        stats_window.geometry("400x300")
        tk.Label(stats_window, text="--- User stats ---",
                 font=("Helvetica", 12, "bold")).pack(pady=5)
        for user, total_grams in rows:
            tk.Label(stats_window,
                     text=f"{user}: {total_grams} g").pack(anchor="w", padx=20)

    def close(self):
        self.close_camera()
        self.root.destroy()

    def close_camera(self):
        if self.cap:
            self.cap.release()
            self.cap = None
        if hasattr(self, "video_loop"):
            self.root.after_cancel(self.video_loop)
            del self.video_loop

if __name__ == "__main__":
    create_database()
    root = tk.Tk()
    app = InitWindow(root)
    root.mainloop()
