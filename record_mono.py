# version:1.0.1905.9051
import gxipy as gx

import numpy
import cv2

from datetime import datetime

def get_output_vid_name():
    now = datetime.now()
    pre_str = "outputs/"
    dt_string = now.strftime("%d_%m_%Y-%H_%M_%S")
    post_str = ".avi"

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

    # set continuous acquisition
    cam.TriggerMode.set(gx.GxSwitchEntry.OFF)

    # set auto exposure         Off: 0, Continuous: 1, Once: 2
    cam.ExposureAuto.set(1)
    cam.AutoExposureTimeMax.set(76923.0)

    # set auto gain             Off: 0, Continuous: 1, Once: 2
    cam.GainAuto.set(1)

    # set target FPS            Off: 0, On: 1
    cam.AcquisitionFrameRateMode.set(1)
    cam.AcquisitionFrameRate.set(13.0)

    # get height, width & FPS
    height = cam.Height.get()
    width = cam.Width.get()
    fps = cam.CurrentAcquisitionFrameRate.get()


    # open output video
    output_vid_name = get_output_vid_name()
    out = cv2.VideoWriter(output_vid_name,cv2.VideoWriter_fourcc(*'DIVX'), fps, (916, 612))

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

        # convert color format
        image = cv2.cvtColor(numpy.asarray(numpy_image),cv2.COLOR_GRAY2BGR)
        # resize image
        image = cv2.resize(image, (916, 612), cv2.INTER_NEAREST)

        # Write video to file
        out.write(image)

        cv2.imshow("Image", image)

        # Press Q on keyboard to stop recording
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        # print height, width, and frame ID of the acquisition image
        print("Frame ID: %d\tHeight: %d\tWidth: %d\tFPS: %.2f"
              % (raw_image.get_frame_id(), raw_image.get_height(), raw_image.get_width(), cam.CurrentAcquisitionFrameRate.get()))

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
