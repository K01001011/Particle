
#Install dlib and face recognition in virtual environment

#https://www.pyimagesearch.com/2018/06/25/raspberry-pi-face-recognition/


from imutils import paths
import face_recognition
import argparse
import pickle
import cv2
import os

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--dataset", required=True,                                           #input
	help="path to input directory of faces + images")
ap.add_argument("-e", "--encodings", required=True,                                         #output
	help="path to serialized db of facial encodings")
ap.add_argument("-d", "--detection-method", type=str, default="hog",                        #detection method
	help="face detection model to use: either `hog` or `cnn`")
args = vars(ap.parse_args())

print("[INFO] quantifying faces...")
imagePaths = list(paths.list_images(args["dataset"]))
 
knownEncodings = []
knownNames = []


for (i, imagePath) in enumerate(imagePaths):
	# extract the person name from the image path
	print("[INFO] processing image {}/{}".format(i + 1,
		len(imagePaths)))
	name = imagePath.split(os.path.sep)[-2]                                                 #name of the subdirectory should be the persons name
 
	# load the input image and convert it from BGR (OpenCV ordering)
	# to dlib ordering (RGB)
	image = cv2.imread(imagePath)
	rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # detect the (x, y)-coordinates of the bounding boxes
	# corresponding to each face in the input image
	boxes = face_recognition.face_locations(rgb,                                            #draws boxes around faces
		model=args["detection_method"])                                                     #CNN method is more accurate but slower. HOG is faster but less accurate.
 
	# compute the facial embedding for the face
	encodings = face_recognition.face_encodings(rgb, boxes)                                 #convert to 128d vectors
 
	# loop over the encodings
	for encoding in encodings:
		# add each encoding + name to our set of known names and
		# encodings
		knownEncodings.append(encoding)
		knownNames.append(name)

# dump the facial encodings + names to disk
print("[INFO] serializing encodings...")
data = {"encodings": knownEncodings, "names": knownNames}
f = open(args["encodings"], "wb")
f.write(pickle.dumps(data))
f.close()


#python encode_faces.py --dataset dataset --encodings encodings.pickle                      in terminal (will take long time)