import os
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'

import sys
sys.path.append(os.path.abspath('../poors_man_rekognition'))

# Import pipeline elements
from rekognition.pipeline.pipeline import Pipeline
# Data Handlers
from rekognition.pipeline.input_handlers.preprocessors import ResizeImage
from rekognition.pipeline.input_handlers.video_handler import VideoHandlerElem
from rekognition.pipeline.input_handlers.image_handler import ImageHandlerElem

# Computer Vision
from rekognition.pipeline.similar_frames.similar_frames_finder import SimilarFramesFinder
from rekognition.pipeline.similar_frames.comp_hist_kernel import CompHist
from rekognition.pipeline.similar_frames.ssim_kernel import SSIM

from rekognition.pipeline.face_detectors.face_detector import FaceDetectorElem
from rekognition.pipeline.face_detectors.mobilenets_ssd import MobileNetsSSDFaceDetector
from rekognition.pipeline.face_detectors.yolov3_face_detector import YOLOv3FaceDetector
from rekognition.pipeline.face_detectors.mtcnn import MTCNNFaceDetector
from rekognition.pipeline.face_detectors.dsfd import DSFDFaceDetector

from rekognition.pipeline.recognizers.face_recognizer import FaceRecognizerElem
from rekognition.pipeline.recognizers.facenet_recognizer import FacenetRecognizer
from rekognition.pipeline.recognizers.arcface_recognizer import ArcFaceRecognizer

# Output
from rekognition.pipeline.output_handlers.videooutput_handler import VideoOutputHandler
from rekognition.pipeline.output_handlers.imageoutput_handler import ImageOutputHandler

absFilePath = os.path.abspath(__file__)
fileDir = os.path.dirname(os.path.abspath(__file__))
parentDir = os.path.dirname(fileDir)

def createPipeline(input_path, progress_callback = None, isImage = False, useYolo = True, max_frames = None):
	filename = os.path.basename(input_path)
	filename_wo_ext = os.path.splitext(filename)[0]

	resizer = ResizeImage(640, 480)

	# Data handlers
	if isImage:
		datahandler = ImageHandlerElem()
	else:
		datahandler = VideoHandlerElem()

	datahandler.max_frames = max_frames

	# Group similar frames
	simframes = SimilarFramesFinder(CompHist())

	# Face Detector
	if useYolo:
		face_detector = YOLOv3FaceDetector()
	else:
		face_detector = MobileNetsSSDFaceDetector()

	face_detector = FaceDetectorElem(face_detector)
	datahandler = VideoHandlerElem()

	# Face Recognizer
	# face_recognizer = FaceRecognizerElem(ArcFaceRecognizer(fileDir + "/../poors_man_rekognition/rekognition/model/arcface/classifiers/arcface_first_evals_scikit_aug.pkl"))
	face_recognizer = FaceRecognizerElem(FacenetRecognizer(fileDir + "/../poors_man_rekognition/rekognition/model/facenet/classifiers/facenet_first_evals_scikit_aug.pkl"))
	output_hand = VideoOutputHandler()

	pipeline = Pipeline([datahandler,
						 simframes,
						 face_detector,
						 face_recognizer,
						 output_hand
						 ])

	print(pipeline)

	# Benchmarks stuff
	out_name = "{}_{}_{}".format(filename_wo_ext, face_detector, face_recognizer)
	try:
		# JSON_data = await ioloop.run_in_executor(None, pipeline.run, {datahandler: {"input_path" : input_path, "preprocessors": [resizer]},
		# 		  simframes: {"sim_threshold": 0.99, "max_jobs": 10},
		# 		  face_detector: {"min_score": 0.6},
		# 		  face_recognizer: {"backend":"SciKit", "n_ngbr": 10},
		# 		  pipeline: {"out_name": "output/" + out_name}}, True, progress_callback)

		JSON_data = pipeline.run({datahandler: {"input_path" : input_path, "preprocessors": [resizer]},
				  simframes: {"sim_threshold": 0.99, "max_jobs": 10},
				  face_detector: {"min_score": 0.6},
				  face_recognizer: {"backend":"SciKit", "n_ngbr": 10},
				  output_hand: {"output_name": out_name},
				  pipeline: {"out_name": os.path.join("output/", out_name)}}, benchmark=True, progress_callback=progress_callback)

		return JSON_data
	except Exception as e:
		print(e)
		return False