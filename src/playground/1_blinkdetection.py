import numpy as np
from numpy.lib.stride_tricks import as_strided
import cv2

from metavision_sdk_core import BaseFrameGenerationAlgorithm
from metavision_core.event_io import EventsIterator
import metavision_sdk_cv


# Stride over an image with the speecified window and return  
# the arraay  with  the most events
    
def find_brightest_region_fast(image, window_size=(50, 50)):
    # Convert to grayscale if colored
    if len(image.shape) > 2:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    stride = image.strides + image.strides
    shape = (image.shape[0] - window_size[1] + 1, image.shape[1] - window_size[0] + 1) + window_size
    strided = as_strided(image, shape=shape, strides=stride)

    window_sums = np.sum(strided, axis=(2,3))
    max_pos = np.unravel_index(np.argmax(window_sums), window_sums.shape)

    return max_pos


def main():
    mv_it = EventsIterator(input_path="", delta_t=10000)
    height, width = mv_it.get_size()

    frequency_filter = metavision_sdk_cv.FrequencyAlgorithm(width=width, height=height, min_freq=10, max_freq=100)
    frequency_clustering_filter = metavision_sdk_cv.FrequencyClusteringAlgorithm(width=width, height=height, 
                                                                                min_cluster_size=1, max_frequency_diff=10000, max_time_diff=10000)

    freq_buffer = frequency_filter.get_empty_output_buffer()
    cluster_buffer = frequency_clustering_filter.get_empty_output_buffer()


    im = np.zeros((height, width, 3), dtype=np.uint8)

    for idx, ev in enumerate(mv_it):
        BaseFrameGenerationAlgorithm.generate_frame(ev, im)

        frequency_filter.process_events(ev, freq_buffer)
        frequency_clustering_filter.process_events(freq_buffer, cluster_buffer)


        for cluster in cluster_buffer.numpy():
            x0 = int(cluster["x"]) - 10
            y0 = int(cluster["y"]) - 10
            cv2.rectangle(im, (x0, y0), (x0+20, y0+20), color=(0, 255, 0))
            cv2.putText(im, "id_{}: {} Hz".format(cluster["id"], int(cluster["frequency"])), (x0, y0-10), cv2.FONT_HERSHEY_PLAIN,
                        1, (0, 255, 0), 1)

        cv2.imshow("Events", im[...,::-1])
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

if __name__ == "__main__":
	main()