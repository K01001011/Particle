# Particle

What does one do after getting up in the morning? Look in the mirror of course. How about a mirror which not only faithfully reflects your face but also shares the useful information that you need to start the day. Presenting  - Particle! Particle gives the user all the vital information which they need to start their day including the weather, reminders, tasks, calendars, emails, music, and more, alongside their reflection. Additionally, it also calculates their vital parameters such as heartbeat in real time. The visual assistant uses the face as the identity to unlock the application.

It comprises a Python application running on a Raspberry Pi, which in turn is linked to a mobile Android application. The Raspberry Pi is used as it is extremely portable and can be plugged into any external monitor. The Android application is used to customize the layout of the app running on the Pi. A web camera connected to the Pi allows for unique identification of different users via their face, and also fulfills the purpose of the display acting as a pseudo mirror. It also scans the face of the user, specifically their forehead, and calculates their heartbeat in real time using a Python application with OpenCV. 
  
  
face_datasets - capture images for face recognition  
train_encode - train images for face recognition  
recognize_faces - face recognition  
get_pulse - measure heart rate from webcam

backend - firebase

