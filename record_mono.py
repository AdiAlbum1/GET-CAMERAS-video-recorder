# version:1.0.1905.9051
import gxipy as gx

import numpy
import cv2

from datetime import datetime

from parameters import *

def get_output_vid_name():
    now = datetime.now()
    pre_str = "outputs/"
    dt_string = now.strftime("%d/%m/%Y_%H:%M:%S")
    post_str = ".mp4"

    return pre_str + dt_string + post_str

def main():
    print("")
    print("Initializing......")
    print("")

    # create a device manager
    device_manager = gx.DeviceManager()
    dev_num, dev_info_list = device_manager.update_device_list()
    if dev_num is 0:
        print("Number of enumerated devices is 0")
        return

    # open the first device
    cam = device_manager.open_device_by_index(1)

    # exit when the camera is a color camera
    if cam.PixelColorFilter.is_implemented() is True:
        print("This sample does not support color camera.")
        cam.close_device()
        return

    # Get height, width & FPS
    height = cam.Height.get()
    width = cam.Width.get()
    fps = FPS

    # set continuous acquisition
    cam.TriggerMode.set(gx.GxSwitchEntry.OFF)

    # set exposure
    cam.ExposureTime.set(EXPOSURE_TIME)

    # set gain
    cam.Gain.set(GAIN)

    # set FPS
    cam.AcquisitionFrameRate.set(FPS)

    # open output video
    output_vid_name = get_output_vid_name()
    out = cv2.VideoWriter(output_vid_name,cv2.VideoWriter_fourcc(*'MP4V'), fps, (width,height))

    # set the acq buffer count
    cam.data_stream[0].set_acquisition_buffer_number(1)
    # start data acquisition
    cam.stream_on()

    while True:
        # get raw image
        raw_image = cam.data_stream[0].get_image()
        if raw_image is None:
            print("Image aquistion failed.")
            continue

        # create numpy array with data from raw image
        numpy_image = raw_image.get_numpy_array()
        if numpy_image is None:
            continue

        # Write video to file
        out.write(pimg)

        # display image with opencv
        pimg = cv2.cvtColor(numpy.asarray(numpy_image),cv2.COLOR_GRAY2BGR)
        cv2.imshow("Image",pimg)

        # Press Q on keyboard to stop recording
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        # print height, width, and frame ID of the acquisition image
        print("Frame ID: %d   Height: %d   Width: %d"
              % (raw_image.get_frame_id(), raw_image.get_height(), raw_image.get_width()))

    # When everything done, release the video write objects
    out.release()

    # Closes all the frames
    cv2.destroyAllWindows()

    # stop data acquisition
    cam.stream_off()

    # close device
    cam.close_device()

if __name__ == "__main__":
    main()
