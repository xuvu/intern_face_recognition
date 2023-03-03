import time
import tkinter as tk
from tkinter import ttk
import cv2
import face_recognition
from PIL import Image, ImageTk
from tkinter import messagebox

video_capture = cv2.VideoCapture(0)
face_image = None
latest_faces = []
count = 0
unknown_face = None
face_loc = []

# For unknown person
# -------------------------------------------
# Person ID
person_ID = None
# Person name
person_name = None
# -------------------------------------------


# For known person
# -------------------------------------------
# Person face feature vector
known_faces = [

    face_recognition.face_encodings(face_recognition.load_image_file("face0.jpg"))[0],
    face_recognition.face_encodings(face_recognition.load_image_file("face1.jpg"))[0],
    face_recognition.face_encodings(face_recognition.load_image_file("face2.jpg"))[0]

]
# Person ID
known_ID = [

    10,
    11,
    12

]

# Person name
know_name = [

    'Korawit01',
    'Korawit02',
    'Korawit03'

]
# -------------------------------------------


def map_person_name(n):
    return know_name[n]


def map_person_ID(n):
    return known_ID[n]


current_window = None


def open_window1_face_encoder():
    # Define a callback function for the click event
    def label_click(event):
        # Get the index of the clicked label
        clicked_index = int(event.widget.winfo_name())

        # Get the corresponding numpy array from latest_faces
        # clicked_face = latest_faces[clicked_index]
        try:
            print(face_recognition.face_encodings(latest_faces[clicked_index]))
        except:
            messagebox.showwarning('Error from face encoder', 'เกิดข้อผิดพลาดในการแปลงข้อมูลภาพ')
        # Convert the numpy array to a PIL image
        # clicked_image = cv2.cvtColor(clicked_face, cv2.COLOR_BGR2RGB)

        # clicked_image = Image.fromarray(clicked_image)

        # Do something with the clicked image, such as display it in a new window
        # clicked_image.show()

    # Function to update the video canvas
    def update_video_canvas():
        global face_loc
        # Get the current frame
        ret, frame = video_capture.read()
        # Detect face locations
        face_locations = face_recognition.face_locations(frame)
        # Draw rectangle around each detected face
        if len(face_locations) > 0:
            save_button.pack(side=tk.LEFT)
            for top, right, bottom, left in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        else:
            save_button.pack_forget()

        # Display the resulting frame in the canvas
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = ImageTk.PhotoImage(image)
        video_canvas.image = image
        video_canvas.create_image(0, 0, anchor='nw', image=image)

    # Function to update the face canvas
    def update_face_canvas():
        global face_image
        face_canvas.delete("all")  # Clear the face canvas

        # Remove the previous labels
        for widget in face_canvas.winfo_children():
            widget.pack_forget()

        # Display the last 3 faces
        for i in range(len(latest_faces)):
            face_image = cv2.cvtColor(latest_faces[i], cv2.COLOR_BGR2RGB)
            face_image = Image.fromarray(face_image)
            face_image = ImageTk.PhotoImage(face_image)

            label = tk.Label(face_canvas, image=face_image)
            label.image = face_image
            label.pack(side=tk.LEFT, padx=10)

            # label.bind("<Button-1>", label_click)
            # Create the compare button

            compare_button = tk.Button(face_canvas, text="บันทึกภาพใบหน้า", font=("Arial", 10), fg="#fff", bg="#555", command='', name=str(i))
            compare_button.pack(side=tk.LEFT, padx=3, pady=3, ipadx=3)
            compare_button.bind("<Button-1>", label_click)

    # Function to save the face image
    def save_face():
        global face_loc
        global count

        # Get the current frame
        ret, frame = video_capture.read()

        # Detect face locations
        face_locations = face_recognition.face_locations(frame)

        # Save the face image
        if len(face_locations) > 0:
            top, right, bottom, left = face_locations[0]
            face_image = frame[top + 5:bottom - 5, left + 5:right - 5]

            latest_faces.append(face_image)

            if len(latest_faces) > 3:
                latest_faces.pop(0)  # Remove the oldest face from the list
                count = 0

            print(len(latest_faces))

            cv2.imwrite("face" + str(count) + ".jpg", face_image)
            count += 1

            print("Face image saved to face.jpg", person_ID, person_name)
            update_face_canvas()

        else:
            messagebox.showwarning("Face not found", "ไม่พบใบหน้า จากกล้อง")
            print("No face detected")

    global current_window
    if current_window:
        current_window.destroy()
    window1 = tk.Toplevel(root)
    window1.title("Face Encoder")
    # window1.geometry("300x200+200+200")  # Set window size and position
    # Add widgets to window1 here...
    current_window = window1

    # Create a title label
    title_label = tk.Label(window1, text="บันทึกภาพใบหน้า", font=("Arial", 16, "bold"), fg="#555", pady=10)
    title_label.pack()

    # Create a frame for the video canvas and the save button
    frame = tk.Frame(window1)
    frame.pack(pady=10)

    # Create the video canvas
    video_canvas = tk.Canvas(frame, width=640, height=480)
    video_canvas.pack(side=tk.LEFT, padx=10)

    # Create the save button
    save_button = tk.Button(frame, text="บันทึกภาพใบหน้า", font=("Arial", 14), fg="#fff", bg="#555", command=save_face)
    # save_button.pack(side=tk.LEFT)

    # Create a frame for the face image
    face_frame = tk.Frame(window1)
    face_frame.pack(pady=10)

    # Create a label for the face image
    face_label = tk.Label(face_frame, text="ภาพใบหน้าที่บันทึกได้", font=("Arial", 14, "bold"), fg="#555", pady=10)
    face_label.pack()

    # Create the face canvas
    face_canvas = tk.Canvas(face_frame, width=200, height=200)
    face_canvas.pack()

    window1.iconphoto(False, p1)

    # Run the GUI loop
    while True:
        # Update the video canvas and handle events
        update_video_canvas()
        window1.update()

        # Exit when the window is closed
        if not window1.winfo_exists():
            global latest_faces
            latest_faces = []
            break


def open_window2_face_comparison():
    global current_window
    if current_window:
        current_window.destroy()
    window2 = tk.Toplevel(root)
    window2.title("Face Comparison")
    # window2.geometry("300x200+200+200")  # Set window size and position
    # Add widgets to window2 here...
    current_window = window2

    # Function to update the video canvas
    def update_video_canvas():
        global face_loc
        # Get the current frame
        ret, frame = video_capture.read()
        # Detect face locations
        face_locations = face_recognition.face_locations(frame)
        # Draw rectangle around each detected face
        if len(face_locations) > 0:
            save_button.pack(side=tk.LEFT)
            for top, right, bottom, left in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        else:
            save_button.pack_forget()

        # Display the resulting frame in the canvas
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = ImageTk.PhotoImage(image)
        video_canvas.image = image
        video_canvas.create_image(0, 0, anchor='nw', image=image)

    # Function to save the face image
    def save_face():
        global unknown_face
        global face_image
        global face_loc
        # Get the current frame
        ret, frame = video_capture.read()
        # Detect face locations
        face_locations = face_recognition.face_locations(frame)
        # Save the face image
        if len(face_locations) > 0:
            top, right, bottom, left = face_locations[0]
            face_image = frame[top + 5:bottom - 5, left + 5:right - 5]

            unknown_face = face_image

            cv2.imwrite("face_unknown.jpg", face_image)

            print("Face image saved to face.jpg")
            update_face_canvas()

        else:
            print("No face detected")

    # Define a callback function for the click event
    def label_click(event):
        # Get the index of the clicked label
        # clicked_index = int(event.widget.winfo_name())

        # Get the corresponding numpy array from latest_faces
        # clicked_face = latest_faces[clicked_index]
        load_click_image = face_recognition.load_image_file(unknown_face)
        print(face_recognition.face_encodings(load_click_image)[0])

        # Convert the numpy array to a PIL image
        # clicked_image = cv2.cvtColor(clicked_face, cv2.COLOR_BGR2RGB)

        # clicked_image = Image.fromarray(clicked_image)

        # Do something with the clicked image, such as display it in a new window
        # clicked_image.show()

    def compare_face():
        # Record the start time
        start_time = time.time()
        try:

            unknown_encode = face_recognition.face_encodings(unknown_face)[0]

            for index_anchor_face in range(len(known_faces)):
                result = face_recognition.compare_faces([known_faces[index_anchor_face]], unknown_encode)
                if result[0]:
                    print(map_person_ID(index_anchor_face), map_person_name(index_anchor_face), result[0])
                    label_person_info = tk.Label(face_frame, text="Person information")
                    label_person_info.pack(side=tk.BOTTOM, pady=10)
                else:
                    print(result[0])



        except:
            messagebox.showwarning('Error from face encoder', 'เกิดข้อผิดพลาดในการแปลงข้อมูลภาพ')
        # Record the end time
        end_time = time.time()

        # Calculate the elapsed time
        elapsed_time = end_time - start_time

        print(f"Elapsed time: {elapsed_time:.5f} seconds")

    # Function to update the face canvas
    def update_face_canvas():
        global face_image
        face_canvas.delete("all")  # Clear the face canvas

        # Remove the previous labels
        for widget in face_canvas.winfo_children():
            widget.pack_forget()

        face_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
        face_image = Image.fromarray(face_image)
        face_image = ImageTk.PhotoImage(face_image)

        label = tk.Label(face_canvas, image=face_image, name='')
        label.image = face_image
        label.pack(side=tk.LEFT, padx=10)
        # label.bind("<Button-1>", label_click)

        # Check if compare_button widget exists
        compare_button_exists = False
        for widget in window2.winfo_children():
            if widget.winfo_name() == "compare_button":
                compare_button_exists = True
                print(compare_button_exists)
                break

        # Create the compare button
        if not compare_button_exists:
            compare_button = tk.Button(face_canvas, text="ค้นหาจากใบหน้า", font=("Arial", 14), fg="#fff", bg="#555",
                                       command=compare_face, name="compare_button")
            compare_button.pack(side=tk.LEFT, padx=10, pady=10, ipadx=10)

    # Create a title label
    title_label = tk.Label(window2, text="ค้นหาบุคคลจากใบหน้า", font=("Arial", 16, "bold"), fg="#555", pady=10)
    title_label.pack()

    # Create a frame for the video canvas and the save button
    frame = tk.Frame(window2)
    frame.pack(pady=10)

    # Create the video canvas
    video_canvas = tk.Canvas(frame, width=640, height=480)
    video_canvas.pack(side=tk.LEFT, padx=10)

    # Create the save button
    save_button = tk.Button(frame, text="บันทึกภาพใบหน้า", font=("Arial", 14), fg="#fff", bg="#555", command=save_face)

    # Create a frame for the face image
    face_frame = tk.Frame(window2)
    face_frame.pack(pady=10)

    # Create a label for the face image
    face_label = tk.Label(face_frame, text="ภาพใบหน้าที่บันทึกได้", font=("Arial", 14, "bold"), fg="#555", pady=10)
    face_label.pack()

    # Create the face canvas
    face_canvas = tk.Canvas(face_frame, width=200, height=200)
    face_canvas.pack()

    window2.iconphoto(False, p1)
    # Run the GUI loop
    while True:
        # Update the video canvas and handle events
        update_video_canvas()
        root.update()

        # Exit when the window is closed
        if not window2.winfo_exists():
            break


root = tk.Tk()
root.title("โปรแกรมจดจำใบหน้า")

p1 = tk.PhotoImage(file='face.png')
# Setting icon of master window
root.iconphoto(False, p1)

# Set window size and position to center the UI
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = 400
window_height = 300
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Add some styling to the buttons
style = ttk.Style()
style.configure("TButton", font=("Arial", 12), padding=10)

button1 = ttk.Button(root, text="บันทึกภาพใบหน้า", command=open_window1_face_encoder)
button1.pack(pady=20)

button2 = ttk.Button(root, text="ระบุตัวตนด้วยใบหน้า", command=open_window2_face_comparison)
button2.pack()

root.mainloop()
