import cv2
import threading
import mysql.connector
import face_recognition
import numpy as np
from datetime import datetime, timedelta

class camThread(threading.Thread):
    def __init__(self, previewName, camID,picencode,readname):
        threading.Thread.__init__(self)
        self.previewName = previewName
        self.camID = camID
        self.picencode = picencode
        self.readname = readname
    def run(self):
        print ("Starting " + self.previewName)
        camPreview(self.previewName, self.camID,self.picencode,self.readname)

def camPreview(previewName, camID,picencode,readname):
    cv2.namedWindow(previewName)
    video_capture = cv2.VideoCapture(camID)
    
    # Create arrays of known face encodings and their names
    known_face_encodings = picencode
    known_face_names = readname

    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding,tolerance=0.5)
                name = "Unknown"

                # # If a match was found in known_face_encodings, just use the first one.
                # if True in matches:
                #     first_match_index = matches.index(True)
                #     name = known_face_names[first_match_index]

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    updateMySqlTable(name)

                print ('this is : '+ str(name))
                face_names.append(name)

        process_this_frame = not process_this_frame


        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Display the resulting image
        cv2.imshow(previewName, frame)

        # Hit 'q' on the keyboard to quit!
        key = cv2.waitKey(20)
        if key == 27:  # exit on ESC
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()

            
    cv2.destroyWindow(previewName)

def picencode(dep_ID):

    mydb = mysql.connector.connect(
            host = 'localhost',
            user='root',
            passwd='',
            database='test'
        )
    mycursor = mydb.cursor()

    sql = 'SELECT cin_number,picture FROM employee WHERE department_id=%s'
    value=[dep_ID]
    mycursor.execute(sql,value)

    emp_pics = mycursor.fetchall()
    emp_photos = []
    for emp_pic in emp_pics:
        photo_emp = open(str(emp_pic[0])+'.jpg', 'wb').write(emp_pic[1])
        encode = face_recognition.load_image_file(str(emp_pic[0]) + ".jpg")
        face_encoding = face_recognition.face_encodings(encode)[0]
        emp_photos.append(face_encoding)
    return emp_photos

def readname(dep_ID):

    mydb = mysql.connector.connect(
            host = 'localhost',
            user='root',
            passwd='',
            database='test'
        )
    mycursor = mydb.cursor()

    sql = 'SELECT cin_number FROM employee WHERE department_id=%s'
    value=[dep_ID]
    mycursor.execute(sql,value)

    emp_cins = mycursor.fetchall()
    emp_names = []
    for emp_cin in emp_cins:
        print (emp_cin[0])
        emp_names.append(emp_cin[0])
    return emp_names

def updateMySqlTable(name):
    
    mydb = mysql.connector.connect(
        host = 'localhost',
        user='root',
        passwd='',
        database='test'
    )
    mycursor = mydb.cursor()

    print("Connected to MySQL")
    presence = 'present'
    MySQL_update_query = 'Update presence set state = %s where cin_number = %s'
    columnValues = [presence, name]
    mycursor.execute(MySQL_update_query,columnValues)
    mydb.commit()
                
    print("Record Updated successfully ") 