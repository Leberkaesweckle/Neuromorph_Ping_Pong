import numpy as np
from numpy.lib.stride_tricks import as_strided
import cv2


import metavision_sdk_cv
from metavision_core.event_io import EventsIterator
from metavision_core.event_io import LiveReplayEventsIterator, is_live_camera
from metavision_sdk_analytics import TrackingAlgorithm, TrackingConfig, draw_tracking_results
from metavision_sdk_core import BaseFrameGenerationAlgorithm, RollingEventBufferConfig, RollingEventCDBuffer
from metavision_sdk_cv import ActivityNoiseFilterAlgorithm, TrailFilterAlgorithm
from metavision_sdk_ui import EventLoop, BaseWindow, MTWindow, UIAction, UIKeyEvent


from sklearn.cluster import KMeans

display_led_frequency = 100 # 
player1_frequency = 160
player2_frequency = 70

points = []

def is_within_tolerance(value1, value2, tolerance = 0.10):
    max_difference = tolerance* max(value1, value2)
    actual_difference = abs(value1 - value2)    
    return actual_difference <= max_difference

def closest_point_on_line(top, bottom, point_x):
    top, bottom, point_x = np.array(top), np.array(bottom), np.array(point_x)
    
    line_vec = top - bottom
    point_vec = point_x - bottom
    
    projection = np.dot(point_vec, line_vec) / np.dot(line_vec, line_vec)
    projection = max(0, min(1, projection))

    closest_point = bottom + projection * line_vec    
    return projection, closest_point.tolist()


def get_corner_points(points):
        
    top_left = top_right = bottom_left = bottom_right = points[0]

    for x, y  in points:
        if x + y < top_left[0] + top_left[1]:
            top_left = (x, y)
        
        if y <= top_right[1] and x > top_right[0]:
            top_right = (x, y)
        
        if x <= bottom_left[0] and y > bottom_left[1]:
            bottom_left = (x, y)
        
        if x + y > bottom_right[0] + bottom_right[1]:
            bottom_right = (x, y)
    
    return top_left, top_right, bottom_right, bottom_left


def main():
    mv_it = EventsIterator(input_path="", delta_t=50000)
    height, width = mv_it.get_size()


    # Frequency of led for calibration
    frequency_filter = metavision_sdk_cv.FrequencyAlgorithm(width=width, height=height, min_freq=90, max_freq=110, diff_thresh_us=10000)
    frequency_clustering_filter = metavision_sdk_cv.FrequencyClusteringAlgorithm(width=width, height=height, min_cluster_size=20, max_frequency_diff=5, max_time_diff=10000)

    freq_buffer = frequency_filter.get_empty_output_buffer()
    cluster_buffer = frequency_clustering_filter.get_empty_output_buffer()    


    im = np.zeros((height, width, 3), dtype=np.uint8)

    state_calibrating_display = 0
    state_tracking_ball = 1
    current_state = state_calibrating_display

    calibrated = False
    tl = tr = br = bl = (0,0)
    
    for idx, evs in enumerate(mv_it):
        
        if evs.size == 0: 
            continue

        max_t = evs['t'][-1]

        if max_t > 1000000 and calibrated == False:  
            
            if len(points) >= 4:
                data = np.array(points)
                kmeans = KMeans(n_clusters=4, n_init="auto")
                kmeans.fit(data)

                centroids = kmeans.cluster_centers_
                tl, tr, br, bl = get_corner_points(centroids.astype(int))  
                              
            
            print("Finished calibration")
            current_state = state_tracking_ball
            calibrated = True

        BaseFrameGenerationAlgorithm.generate_frame(evs, im)
        
        if current_state == state_calibrating_display:
            calibration(frequency_filter, frequency_clustering_filter, freq_buffer, cluster_buffer, im, evs)

        elif current_state == state_tracking_ball: 
            frequency_filter.set_max_freq(190)
            frequency_filter.set_min_freq(60)

            frequency_filter.process_events(evs, freq_buffer)
            frequency_clustering_filter.process_events(freq_buffer, cluster_buffer)

            data = cluster_buffer.numpy()
            tolerance = 0.1

            if data.size > 0:
                player1_points =  np.array([[point["x"], point["y"]] for point in data if is_within_tolerance(point["frequency"], player1_frequency, tolerance)])
                player2_points = np.array([[point["x"], point["y"]] for point in data if is_within_tolerance(point["frequency"], player2_frequency, tolerance)])

                # Calculate central point for each cluster
                player1_centroid = np.mean(player1_points, axis=0) if player1_points.size > 0 else None
                player2_centroid = np.mean(player2_points, axis=0) if player2_points.size > 0 else None

                if player1_centroid is not None:   
                    
                    center_p1 =tuple(np.round(player1_centroid).astype(int))
                    cv2.circle(im, center_p1, 5, (255,0,0), 4)


                    percentage, line_point = closest_point_on_line(tl, bl, player1_centroid)
                    paddle_pos = tuple(np.round(line_point).astype(int))
                    cv2.circle(im, paddle_pos, 5, (0,0,255), 4)
                    cv2.putText(im, f"Player1: {percentage}", paddle_pos, cv2.FONT_HERSHEY_PLAIN,
                            1, (0,0,255), 1)


                if player2_centroid is not None:
                    center_p2 =tuple(np.round(player2_centroid).astype(int))
                    cv2.circle(im, center_p2, 5, (255,0,0), 4)

                    percentage, line_point = closest_point_on_line(tr, br, player2_centroid)
                    paddle_pos = tuple(np.round(line_point).astype(int))
                    cv2.circle(im, paddle_pos, 5, (0,0,255), 4)
                    cv2.putText(im, f"Player2: {percentage}", paddle_pos, cv2.FONT_HERSHEY_PLAIN,
                            1, (0,0,255), 1)


            for cluster in cluster_buffer.numpy():
                print(cluster)
                x0 = int(cluster["x"]) - 10
                y0 = int(cluster["y"]) - 10
                cv2.rectangle(im, (x0, y0), (x0+20, y0+20), color=(0, 255, 0))
                cv2.putText(im, "id_{}: {} Hz".format(cluster["id"], int(cluster["frequency"])), (x0 -10, y0-10), cv2.FONT_HERSHEY_PLAIN,
                            1, (0, 255, 0), 1)

            cv2.line(im, tl, tr, (0, 255, 0), 3) 
            cv2.line(im, tr, br, (0, 255, 0), 3) 
            cv2.line(im, br, bl, (0, 255, 0), 3) 
            cv2.line(im, bl, tl, (0, 255, 0), 3) 

            cv2.putText(im, "tl", tl, cv2.FONT_HERSHEY_PLAIN, 10, (0, 255, 0), 1)
            cv2.putText(im, "tr", tr, cv2.FONT_HERSHEY_PLAIN, 10, (0, 255, 0), 1)
            cv2.putText(im, "br", br, cv2.FONT_HERSHEY_PLAIN, 10, (0, 255, 0), 1)
            cv2.putText(im, "bl", bl, cv2.FONT_HERSHEY_PLAIN, 10, (0, 255, 0), 1)
            

        cv2.imshow("Events", im[...,::-1])
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    cv2.destroyAllWindows()



def calibration(frequency_filter, frequency_clustering_filter, freq_buffer, cluster_buffer, im, ev):
    frequency_filter.process_events(ev, freq_buffer)
    frequency_clustering_filter.process_events(freq_buffer, cluster_buffer)
    
    for cluster in cluster_buffer.numpy():
        x0 = int(cluster["x"]) 
        y0 = int(cluster["y"])
        frequency = int(cluster["frequency"])

        if is_within_tolerance(frequency, display_led_frequency):
            points.append([x0,y0])
        cv2.circle(im, (x0,y0), 5, (255,0,0), 4)

if __name__ == "__main__":
	main()