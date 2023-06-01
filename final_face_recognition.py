from sys import exit
import tkinter as tk
import cv2
from face_recognition import face_locations, face_encodings, face_distance, compare_faces
from PIL import Image, ImageTk
from tkinter import messagebox
import configparser
import mysql.connector

def new_function():
    return 'new_change'

def read_INI_database(file_name):
    # Read the existing configuration from file
    config = configparser.ConfigParser()
    config.read(file_name)

    host_ = config.get('Database_setting', 'host')
    user_ = config.get('Database_setting', 'user')
    password_ = config.get('Database_setting', 'password')
    database_ = config.get('Database_setting', 'database')
    table_ = config.get('Database_setting', 'table')

    return host_, user_, password_, database_, table_


# Read the information from .INI file
host, user, password, database, table = read_INI_database('db_setting.ini')

mydb = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
)


# For unknown person
def open_window1_face_encoder(person_id_, person_name_, user_):
    def send_data(id_num_, name_, user_code_, feature_vector_):
        try:
            # create a cursor object to interact with the database
            cursor = mydb.cursor()

            # define the data to be inserted as a Python tuple
            data = (id_num_, name_, user_code_, feature_vector_)

            # execute a query to insert the data into the table
            sql = "INSERT INTO " + table + " (id_num, person_name, user_code, feature_vector) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE person_name = VALUES(person_name), user_code = VALUES(user_code), feature_vector = VALUES(feature_vector)"
            val = data
            cursor.execute(sql, val)

            # commit the changes to the database
            mydb.commit()

            # check if the row was inserted
            if cursor.rowcount > 0:
                return True
            else:
                return False
        except:
            return False

    # Define a callback function for the click event
    def label_click(event):
        unknown_face_encoded = None
        finish_ = False
        # Get the index of the clicked label
        clicked_index = int(event.widget.winfo_name())

        try:
            unknown_face_encoded = face_encodings(latest_faces[clicked_index])[0]

            # Convert the feature vector to a comma-separated string
            unknown_face_encoded = "[" + ','.join(str(val) for val in unknown_face_encoded) + "]"
            # print(unknown_face_encoded)
        except:
            messagebox.showwarning('เกิดข้อผิดพลาดในการแปลงข้อมูลภาพ', 'เกิดข้อผิดพลาดในการแปลงข้อมูลภาพ กรุณาเลือกภาพอื่นหรือทำการถ่ายภาพใหม่')

        if mydb.is_connected() and unknown_face_encoded is not None:
            if send_data(id_num_=person_id_, name_=person_name_, user_code_=user_, feature_vector_=str(unknown_face_encoded)):
                messagebox.showinfo("การบันทึกสำเร็จ", "ข้อมูลได้รับการบันทึกแล้ว")
                finish_ = True
            else:
                messagebox.showwarning("เกิดข้้ผิดพลาดในการบันทึกข้อมูล", "ข้อมูลไม่ได้รับการบันทึก")

        if finish_:
            window1.destroy()
            exit()

    # Function to update the video canvas
    def update_video_canvas():
        global face_loc
        # Get the current frame
        ret, frame = video_capture.read()
        # Detect face locations
        face_loc = face_locations(frame)
        # Draw rectangle around each detected face
        if len(face_loc) > 0:
            save_button.pack(side=tk.LEFT)
            for top, right, bottom, left in face_loc:
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

            compare_button = tk.Button(face_canvas, text="บันทึกภาพใบหน้า", font=("Arial", 10), fg="#fff", bg="#555",
                                       command='', name=str(i))
            compare_button.pack(side=tk.LEFT, padx=3, pady=3, ipadx=3)
            compare_button.bind("<Button-1>", label_click)

    # Insert or Update to the database
    # def send_to_database(id_num_, name_, time_stamp_,user_code_,feature_vector_):

    # Function to save the face image
    def save_face():
        global face_loc
        global count
        # Get the current frame
        ret, frame = video_capture.read()
        # Detect face locations
        face_loc = face_locations(frame)
        # Save the face image
        if len(face_loc) > 0:
            top, right, bottom, left = face_loc[0]
            face_image = frame[top + 5:bottom - 5, left + 5:right - 5]

            latest_faces.append(face_image)

            if len(latest_faces) > 3:
                latest_faces.pop(0)  # Remove the oldest face from the list
                count = 0

            # print(len(latest_faces))

            # cv2.imwrite("face" + str(count) + ".jpg", face_image)
            count += 1

            # print("Face image saved to face.jpg", person_ID, person_name)
            update_face_canvas()

        else:
            messagebox.showwarning("Face not found", "ไม่พบใบหน้า จากกล้อง")
            # print("No face detected")

    global current_window
    if current_window:
        current_window.destroy()
    window1 = tk.Tk()
    window1.title("Face Encoder")

    window1.state('zoomed')

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

    window1.iconbitmap("face.ico")

    # Run the GUI loop
    try:
        while True:
            # Update the video canvas and handle events
            update_video_canvas()
            window1.update()
    except:
        pass


# For known person
def open_window2_face_comparison():
    def load_feature_vector():
        try:
            # For known person
            # create a cursor object to interact with the database
            cursor = mydb.cursor()

            # execute a query to select data from the table
            cursor.execute("SELECT * FROM " + table)

            # fetch the results and print them
            result_ = cursor.fetchall()

            return result_

        except:
            messagebox.showwarning('เกิอข้อผิดพลาดในการติดต่อฐานข้อมูล', 'เกิอข้อผิดพลาดในการติดต่อฐานข้อมูล')

    # Function to update the video canvas
    def update_video_canvas():
        global face_loc
        # Get the current frame
        ret, frame = video_capture.read()
        # Detect face locations
        face_loc = face_locations(frame)
        # Draw rectangle around each detected face
        if len(face_loc) > 0:
            save_button.pack(side=tk.LEFT)
            for top, right, bottom, left in face_loc:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            save_face()
            compare_face()

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
        face_loc = face_locations(frame)
        # Save the face image
        if len(face_loc) > 0:
            top, right, bottom, left = face_loc[0]
            face_image = frame[top + 5:bottom - 5, left + 5:right - 5]

            unknown_face = face_image

            # cv2.imwrite("face_unknown.jpg", face_image)

            # print("Face image saved to face.jpg")
            update_face_canvas()

    def convert_b_string_to_np_array(b_string):
        import numpy as np

        # convert bytes string to regular string
        str_value = str(b_string, 'utf-8')

        # remove square brackets and split on comma and whitespace
        str_list = str_value.strip('[]').split(',')

        # convert list of strings to list of floats
        float_list = [float(x) for x in str_list]

        # convert list of floats to NumPy ndarray
        ndarray = np.array(float_list)

        return ndarray

    converted = []
    result = load_feature_vector()
    for p in result:
        converted += [convert_b_string_to_np_array(p[5])]

    def compare_face():
        finish_ = False

        # Remove the previous labels
        for widget in face_frame.winfo_children():
            if "result" in widget.winfo_name():
                # print(widget.winfo_name())
                widget.pack_forget()

        show_label = {'name': [], 'id': [], 'similarity_score': [], 'match': []}
        if mydb.is_connected():
            try:
                unknown_encode = face_encodings(unknown_face)[0]
                count_for_feature = 0
                for row in result:
                    known_face = converted[count_for_feature]
                    same_person = compare_faces([unknown_encode], known_face)[0]
                    if same_person:
                        show_label['name'] += [row[2]]
                        show_label['id'] += [row[0]]
                        show_label['similarity_score'] += [face_distance([unknown_encode], known_face).tolist()[0]]
                        show_label['match'] += [same_person]
                    count_for_feature += 1

                if len(show_label['id']) > 0:
                    sorted_indices = sorted(range(len(show_label['similarity_score'])),key=lambda k: show_label['similarity_score'][k])
                    sorted_data = {key: [show_label[key][i] for i in sorted_indices] for key in show_label}

                    # Slice the top 3 results
                    top_3 = {k: v[:1] for k, v in sorted_data.items()}

                    messagebox.showinfo('ค้นพบบุคคลในฐานข้อมูล','ชื่อ: ' + top_3['name'][0] + "  เลขบัตรประชาชน: " + top_3['id'][0])
                    write_INI_result('face_id.ini', top_3['id'][0], top_3['name'][0])
                    finish_ = True
                else:
                    label_person_info = tk.Label(face_frame, text='ไม่พบบุคคลในฐานข้อมูล', name='result0', font=("Arial", 14))
                    label_person_info.pack(side=tk.BOTTOM, pady=10)

            except:
                pass
                #messagebox.showwarning('เกิดข้อผิดพลาดในการแปลงข้อมูลภาพ','เกิดข้อผิดพลาดในการแปลงข้อมูลภาพ กรุณาถ่ายรูปและเลือกรูปภาพใหม่')
        else:
            messagebox.showwarning('ไม่สามารถเชื่อมต่อฐานข้อมูลได้', 'ไม่สามารถเชื่อมต่อฐานข้อมูลได้')

        if finish_:
            window2.destroy()
            exit()

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
                # print(compare_button_exists)
                break

        # Create the compare button
        if not compare_button_exists:
            compare_button = tk.Button(face_canvas, text="ค้นหาจากใบหน้า", font=("Arial", 14), fg="#fff", bg="#555",
                                       command=compare_face, name="compare_button")
            compare_button.pack(side=tk.LEFT, padx=10, pady=10, ipadx=10)

    global current_window
    if current_window:
        current_window.destroy()
    window2 = tk.Tk()
    window2.title("Face Comparison")

    window2.state('zoomed')
    # Add widgets to window2 here...
    current_window = window2

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

    window2.iconbitmap("face.ico")

    # Run the GUI loop
    try:
        while True:
            # Update the video canvas and handle events
            update_video_canvas()
            window2.update()
    except:
        pass


def write_INI_result(file_name, id_, name_):
    # Read the existing configuration from file
    config = configparser.ConfigParser()
    config.read(file_name, encoding='utf-8')

    # Modify a value
    config.set('face_recognition', 'id_num', id_)
    config.set('face_recognition', 'name', name_)

    # Write the updated configuration back to file
    with open(file_name, 'w', encoding='utf-8') as configfile:
        config.write(configfile)


def read_INI_person(file_name):
    # Read the existing configuration from file
    config = configparser.ConfigParser()
    config.read(file_name, encoding='utf-8')

    person_ID_ = config.get('face_recognition', 'id_num')
    person_name_ = config.get('face_recognition', 'name')
    mode_ = config.get('face_recognition', 'mode')
    user_ = config.get('face_recognition', 'user')

    return person_ID_, person_name_, int(mode_), int(user_)


def clear_INI(file_name):
    # Read the existing configuration from file
    config = configparser.ConfigParser()
    config.read(file_name, encoding='utf-8')

    # Modify a value
    config.set('face_recognition', 'id_num', '')
    config.set('face_recognition', 'name', '')

    # Write the updated configuration back to file
    with open(file_name, 'w', encoding='utf-8') as configfile:
        config.write(configfile)


def database_connection():
    return True


# Read the information from .INI file
person_ID, person_name, mode, user = read_INI_person('face_id.ini')

video_capture = cv2.VideoCapture(0)
face_image = None
latest_faces = []
count = 0
unknown_face = None
face_loc = []

current_window = None

if database_connection():
    if mode == 1:
        open_window1_face_encoder(person_ID, person_name, user)
    elif mode == 2:
        open_window2_face_comparison()
