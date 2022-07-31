from src.cli.args import DetectionArgs
from src.opencv.finger import INDEX_FINGER
from src.opencv.record import HandRecorder


def run(args: DetectionArgs):
    handRecorder = HandRecorder("Right", INDEX_FINGER, args.camera)

    print("Starting recording. Press 'p' to stop.")

    if args.timeout:
        handRecorder.start_record_hand_during(seconds=args.timeout)
    else:
        handRecorder.start_record_hand()

    handRecorder.display_hand_angles_recorded()
    handRecorder.export_hand_angles_recorded_to_csv()
