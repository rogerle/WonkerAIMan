import face_recognition
import cv2
import scipy, cv2, os, sys, argparse, audio
from tqdm import tqdm

if sys.version_info[0] < 3 and sys.version_info[1] < 2:
	raise Exception("Must be using >= Python 3.2")

parser = argparse.ArgumentParser()

parser.add_argument('--ngpu', help='Number of GPUs across which to run in parallel', default=1, type=int)
parser.add_argument('--face', help='The face picture in video', required=True)
parser.add_argument("--data_root", help="Root folder of the processed dataset", required=True)
parser.add_argument("--output", help="folder of the preprocessed dataset", required=True)

args = parser.parse_args()

def capture_videoToimg(vfile, args):
	video_stream = cv2.VideoCapture(vfile)
	frames = []

	image = face_recognition.load_image_file(args.face)

	while 1:
		still_reading, frame = video_stream.read()
		if not still_reading:
			video_stream.release()
			break
		frames.append(frame)

	face_locations = face_recognition.face_locations(frames)
	face_encodings = face_locations.face_encodings(frames,face_locations)

	face_name

