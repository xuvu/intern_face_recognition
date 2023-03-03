# import face_recognition
#
# unknown_image = face_recognition.load_image_file("face1.jpg")
# known_image = face_recognition.load_image_file("face0.jpg")
#
#
# unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
# known_encoding = face_recognition.face_encodings(known_image)[0]
#
# print(unknown_image, known_encoding)
#
# results = face_recognition.compare_faces([known_encoding], unknown_encoding)
#
# print(results[0])

import cv2
import face_recognition
import tkinter as tk
from PIL import Image, ImageTk
import time
video_capture = cv2.VideoCapture(0)
latest_faces = []

count = 0

known_faces = [

    face_recognition.face_encodings(face_recognition.load_image_file("face0.jpg"))[0],
    face_recognition.face_encodings(face_recognition.load_image_file("face1.jpg"))[0],
    face_recognition.face_encodings(face_recognition.load_image_file("face2.jpg"))[0]

]


# Function to update the video canvas
def update_video_canvas():
    # Get the current frame
    ret, frame = video_capture.read()
    # Detect face locations
    face_locations = face_recognition.face_locations(frame)
    # Draw rectangle around each detected face
    if len(face_locations) > 0:
        for top, right, bottom, left in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

    # Display the resulting frame in the canvas
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(image)
    image = ImageTk.PhotoImage(image)
    video_canvas.image = image
    video_canvas.create_image(0, 0, anchor='nw', image=image)


# Function to save the face image
def save_face():
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

        if len(latest_faces) > 1:
            latest_faces.pop(0)  # Remove the oldest face from the list
            count = 0

        print(len(latest_faces))

        cv2.imwrite("face_unknown.jpg", face_image)
        count += 1

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
    load_click_image = face_recognition.load_image_file("face_unknown.jpg")
    print(face_recognition.face_encodings(load_click_image)[0])

    # Convert the numpy array to a PIL image
    # clicked_image = cv2.cvtColor(clicked_face, cv2.COLOR_BGR2RGB)

    # clicked_image = Image.fromarray(clicked_image)

    # Do something with the clicked image, such as display it in a new window
    # clicked_image.show()


def compare_face():
    # Record the start time
    start_time = time.time()

    unknown_encode = face_recognition.face_encodings(latest_faces[0])[0]

    for anchor_face in known_faces:
        result = face_recognition.compare_faces([anchor_face], unknown_encode)
        print(result)

    # Record the end time
    end_time = time.time()

    # Calculate the elapsed time
    elapsed_time = end_time - start_time

    print(f"Elapsed time: {elapsed_time:.5f} seconds")


# Function to update the face canvas
def update_face_canvas():
    face_canvas.delete("all")  # Clear the face canvas

    # Remove the previous labels
    for widget in face_canvas.winfo_children():
        widget.pack_forget()

    # Display the last 3 faces
    for i in range(len(latest_faces)):
        face_image = cv2.cvtColor(latest_faces[i], cv2.COLOR_BGR2RGB)
        face_image = Image.fromarray(face_image)
        face_image = ImageTk.PhotoImage(face_image)

        label = tk.Label(face_canvas, image=face_image, name=str(i))
        label.image = face_image
        label.pack(side=tk.LEFT, padx=10)
        label.bind("<Button-1>", label_click)

        # Check if compare_button widget exists
        compare_button_exists = False
        for widget in root.winfo_children():
            if widget.winfo_name() == "compare_button":
                compare_button_exists = True
                print(compare_button_exists)
                break

        # Create the compare button
        if not compare_button_exists:
            compare_button = tk.Button(face_canvas, text="Compare Face", font=("Arial", 14), fg="#fff", bg="#555",
                                       command=compare_face, name="compare_button")
            compare_button.pack(side=tk.LEFT, padx=10, pady=10, ipadx=10)


# Create a GUI window
root = tk.Tk()
root.title("Face Detection")

# Create a title label
title_label = tk.Label(root, text="Face Recognition", font=("Arial", 16, "bold"), fg="#555", pady=10)
title_label.pack()

# Create a frame for the video canvas and the save button
frame = tk.Frame(root)
frame.pack(pady=10)

# Create the video canvas
video_canvas = tk.Canvas(frame, width=640, height=480)
video_canvas.pack(side=tk.LEFT, padx=10)

# Create the save button
save_button = tk.Button(frame, text="Save Face", font=("Arial", 14), fg="#fff", bg="#555", command=save_face)
save_button.pack(side=tk.LEFT)

# Create a frame for the face image
face_frame = tk.Frame(root)
face_frame.pack(pady=10)

# Create a label for the face image
face_label = tk.Label(face_frame, text="Face Image", font=("Arial", 14, "bold"), fg="#555", pady=10)
face_label.pack()

# Create the face canvas
face_canvas = tk.Canvas(face_frame, width=200, height=200)
face_canvas.pack()

# Run the GUI loop
while True:
    # Update the video canvas and handle events
    update_video_canvas()
    root.update()

    # Exit when the window is closed
    if not root.winfo_exists():
        break
