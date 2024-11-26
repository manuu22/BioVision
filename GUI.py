import tkinter as tk
from PIL import Image, ImageTk
import cv2
from ultralytics import YOLO
import random

class GarbageCollectorSim:
    def __init__(self, root):
        self.root = root
        self.root.title("BioVision")
        self.root.geometry("800x600")  # Dimensiones de la ventana
        self.root.configure(bg='white')
        self.video_mode = False
        self.captured_objects = []
        self.bounding_boxes = []
        self.selected_boxes = set()
        self.cap = None
        self.model = YOLO("yolo_models/best.pt")  
        self.confidence_threshold = 0.2
        self.main_menu()
        

    def main_menu(self):
      
        for widget in self.root.winfo_children():
            widget.destroy()
        self.menu_image = Image.open("bin/menu2.png") 
        self.menu_image = self.menu_image.resize((800, 600), Image.Resampling.LANCZOS)
        self.menu_tk = ImageTk.PhotoImage(self.menu_image)
        self.menu_label = tk.Label(self.root, image=self.menu_tk)
        self.menu_label.image = self.menu_tk  
        self.menu_label.pack(fill=tk.BOTH, expand=True)
        self.menu_label.bind("<Button-1>", self.handle_menu_click)

    def handle_menu_click(self, event):
        x, y = event.x, event.y
       

  
        if 281 <= x <= 517 and 238 <= y <= 296:
            self.start_camera_mode()


        elif 282 <= x <= 516 and 323 <= y <= 382:
            self.start_image_mode()

    def start_image_mode(self):
        self.video_mode = False
        self.show_simulator()

    def start_camera_mode(self):
        self.video_mode = True
        self.cap = cv2.VideoCapture(0) 
        self.show_simulator()

    def show_simulator(self):
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
    
        # Marco izquierdo para video/imágenes
        self.video_frame = tk.Label(self.root)
        self.video_frame.pack(side=tk.LEFT, padx=10, pady=10)
    
        # Marco derecho para botellas recolectadas
        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side=tk.RIGHT, padx=10, pady=10)
    
        tk.Label(self.right_frame, text="Collected bottles", font=("Helvetica", 14)).pack(pady=5)
        self.collected_items = tk.Listbox(self.right_frame, width=30, height=15)
        self.collected_items.pack(pady=5)
    
        # Botón para regresar al menú
        tk.Button(self.right_frame, text="Back to menu", command=self.main_menu, width=20).pack(pady=10)
    
        # Botón para cargar otra imagen
        tk.Button(self.right_frame, text="Load another image", command=self.load_image, width=20).pack(pady=10)
    
        # Botón para calcular gramos reciclados
        tk.Button(self.right_frame, text="Calculate recycled plastic", command=self.calculate_recycled_plastic, width=20).pack(pady=10)
    
        # Iniciar simulación
        if self.video_mode:
            self.process_video()
        else:
            self.load_image()



    def process_video(self):
        ret, frame = self.cap.read()
        if ret:
            self.detect_and_display(frame)

        self.root.after(10, self.process_video)  

    def load_image(self):
        # Limpiar detecciones previas, pero mantener el contador de objetos recolectados
        self.bounding_boxes = []
        self.selected_boxes = set()
    
        # Abrir diálogo para seleccionar una nueva imagen
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png")])
        if not file_path:
            return  # No se seleccionó ninguna imagen
    
        # Procesar la nueva imagen
        image = cv2.imread(file_path)
    
        # Redimensionar la imagen si es demasiado grande
        max_width, max_height = 500, 400  # Tamaño máximo permitido
        height, width = image.shape[:2]
        if width > max_width or height > max_height:
            scale = min(max_width / width, max_height / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
        self.detect_and_display(image)



    def detect_and_display(self, frame):
     
         results = self.model(frame)  
         detections = results[0].boxes  
    
        
         self.bounding_boxes = []
         for i, box in enumerate(detections):
             confidence = box.conf[0].item()  
             if confidence >= self.confidence_threshold:
                 x1, y1, x2, y2 = map(int, box.xyxy[0])  
                 self.bounding_boxes.append((x1, y1, x2, y2))
    
       
         for i, (x1, y1, x2, y2) in enumerate(self.bounding_boxes):
             color = (0, 255, 0) if i not in self.selected_boxes else (255, 0, 0)
             cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
             cv2.putText(frame, f"Bottle", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
     
         
         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
         img = Image.fromarray(frame)
         imgtk = ImageTk.PhotoImage(image=img)
         self.video_frame.imgtk = imgtk
         self.video_frame.configure(image=imgtk)
         self.video_frame.bind("<Button-1>", self.collect_item)


    def collect_item(self, event):
        # Obtener posición del clic
        x, y = event.x, event.y
    
        # Verificar si el clic está dentro de algún bounding box
        for i, (x1, y1, x2, y2) in enumerate(self.bounding_boxes):
            if x1 <= x <= x2 and y1 <= y <= y2 and i not in self.selected_boxes:
                self.selected_boxes.add(i)
                bottle_number = len(self.captured_objects) + 1  # Número único para la botella
                self.captured_objects.append(f"Bottle {bottle_number}")
                self.collected_items.insert(tk.END, f"Bottle {bottle_number}")
                break
        # Método para calcular gramos reciclados
    def calculate_recycled_plastic(self):
        total_bottles = len(self.captured_objects)
        if total_bottles == 0:
            tk.messagebox.showinfo("Plastic Calculation", "No bottles collected yet!")
            return
    
        # Calcular gramos reciclados
        total_grams = sum(random.randint(10, 20) for _ in range(total_bottles))
        tk.messagebox.showinfo("Plastic Calculation", f"Recycled plastic: {total_grams} grams")

    def close(self):
        if self.cap:
            self.cap.release()
        self.root.destroy()

root = tk.Tk()
app = GarbageCollectorSim(root)


root.protocol("WM_DELETE_WINDOW", app.close)
root.mainloop() 