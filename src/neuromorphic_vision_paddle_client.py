import numpy as np
from numpy.lib.stride_tricks import as_strided
import cv2
import socket

import threading

import metavision_sdk_cv
from metavision_core.event_io import EventsIterator
from metavision_core.event_io import LiveReplayEventsIterator, is_live_camera
from metavision_sdk_analytics import TrackingAlgorithm, TrackingConfig, draw_tracking_results
from metavision_sdk_core import BaseFrameGenerationAlgorithm, RollingEventBufferConfig, RollingEventCDBuffer
from metavision_sdk_cv import ActivityNoiseFilterAlgorithm, TrailFilterAlgorithm
from metavision_sdk_ui import EventLoop, BaseWindow, MTWindow, UIAction, UIKeyEvent


from sklearn.cluster import KMeans

display_led_frequency = 100 
player1_frequency = 160
player2_frequency = 70

points = []

### NETWORKING
def send_player_paddle_position(player, value):
    def send_message():
        host = 'localhost'
        port = 12345
        with socket.socket() as client_socket:
            client_socket.connect((host, port))
            message = f"{player},{value}"
            client_socket.sendall(message.encode())

    thread = threading.Thread(target=send_message)
    thread.start()

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

# Match corners  (topleft, topright, bottomright, bottomleft) to the leds
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

    # The application has two states. At first we track the corner points to get the playing field.
    # After that we switch to the playmode where the player paddles are tracked.
    state_calibrating_display = 0
    state_tracking_ball = 1
    current_state = state_calibrating_display

    calibrated = False
    tl = tr = br = bl = (0,0)
    
    for idx, evs in enumerate(mv_it):
        # Skip empy frames
        if evs.size == 0: 
            continue
        
        # Max timestamp of the curreent event frame. Events up to this point have been processed
        max_t = evs['t'][-1] 

        # Use the first few seconds to accumulate the position of the leds
        # After the required time is reached we build 4 clusters using kmeans
        # The four clusters get than asssigned to their corresponding position  (topleft, topright and so on)
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
        
        # Initial accumulation during calibration
        if current_state == state_calibrating_display:
            calibration_state(frequency_filter, frequency_clustering_filter, freq_buffer, cluster_buffer, im, evs)

        # Tracking of the players
        elif current_state == state_tracking_ball: 
            player_tracking_state(frequency_filter, frequency_clustering_filter, freq_buffer, cluster_buffer, im, bl, br, tr, tl, evs)
            

        cv2.imshow("Events", im[...,::-1])
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    cv2.destroyAllWindows()

def player_tracking_state(frequency_filter, frequency_clustering_filter, freq_buffer, cluster_buffer, im, bl, br, tr, tl, evs):
    # Find frequencies corresponding to player one and two    
    frequency_filter.set_max_freq(190)
    frequency_filter.set_min_freq(60)


    frequency_filter.process_events(evs, freq_buffer)
    frequency_clustering_filter.process_events(freq_buffer, cluster_buffer)

    data = cluster_buffer.numpy()
    tolerance = 0.1


    if data.size > 0:
        # Assign each found pixel to the corresponding player.
        player1_points =  np.array([[point["x"], point["y"]] for point in data if is_within_tolerance(point["frequency"], player1_frequency, tolerance)])
        player2_points = np.array([[point["x"], point["y"]] for point in data if is_within_tolerance(point["frequency"], player2_frequency, tolerance)])

        # Calculate central point for each cluster/player
        player1_centroid = np.mean(player1_points, axis=0) if player1_points.size > 0 else None
        player2_centroid = np.mean(player2_points, axis=0) if player2_points.size > 0 else None

        # Find the closest possible position of the paddle on the players side to the tracked led
        # and send that position to the server
        if player1_centroid is not None:   
            center_p1 =tuple(np.round(player1_centroid).astype(int))
            cv2.circle(im, center_p1, 5, (255,0,0), 4)


            percentage, line_point = closest_point_on_line(tl, bl, player1_centroid)
            paddle_pos = tuple(np.round(line_point).astype(int))
            cv2.circle(im, paddle_pos, 5, (0,0,255), 4)
            cv2.putText(im, f"Player1: {percentage}", paddle_pos, cv2.FONT_HERSHEY_PLAIN,
                            1, (0,0,255), 1)
                    
            send_player_paddle_position(1, percentage)

        # Find the closest possible position of the paddle on the players side to the tracked led
        # and send that position to the server
        if player2_centroid is not None:
            center_p2 =tuple(np.round(player2_centroid).astype(int))
            cv2.circle(im, center_p2, 5, (255,0,0), 4)

            percentage, line_point = closest_point_on_line(tr, br, player2_centroid)
            paddle_pos = tuple(np.round(line_point).astype(int))
            cv2.circle(im, paddle_pos, 5, (0,0,255), 4)
            cv2.putText(im, f"Player2: {percentage}", paddle_pos, cv2.FONT_HERSHEY_PLAIN,
                            1, (0,0,255), 1)
                    
            send_player_paddle_position(2, percentage)


            # for cluster in cluster_buffer.numpy():
            #     print(cluster)
            #     x0 = int(cluster["x"]) - 10
            #     y0 = int(cluster["y"]) - 10
            #     cv2.rectangle(im, (x0, y0), (x0+20, y0+20), color=(0, 255, 0))qq
            #     cv2.putText(im, "id_{}: {} Hz".format(cluster["id"], int(cluster["frequency"])), (x0 -10, y0-10), cv2.FONT_HERSHEY_PLAIN,
            #                 1, (0, 255, 0), 1)

    cv2.line(im, tl, tr, (0, 255, 0), 3) 
    cv2.line(im, tr, br, (0, 255, 0), 3) 
    cv2.line(im, br, bl, (0, 255, 0), 3) 
    cv2.line(im, bl, tl, (0, 255, 0), 3) 

    cv2.putText(im, "tl", tl, cv2.FONT_HERSHEY_PLAIN, 10, (0, 255, 0), 1)
    cv2.putText(im, "tr", tr, cv2.FONT_HERSHEY_PLAIN, 10, (0, 255, 0), 1)
    cv2.putText(im, "br", br, cv2.FONT_HERSHEY_PLAIN, 10, (0, 255, 0), 1)
    cv2.putText(im, "bl", bl, cv2.FONT_HERSHEY_PLAIN, 10, (0, 255, 0), 1)

def calibration_state(frequency_filter, frequency_clustering_filter, freq_buffer, cluster_buffer, im, ev):
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