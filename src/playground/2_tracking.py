import cv2
import numpy as np

from metavision_core.event_io import EventsIterator
from metavision_core.event_io import LiveReplayEventsIterator, is_live_camera
from metavision_sdk_analytics import TrackingAlgorithm, TrackingConfig, draw_tracking_results
from metavision_sdk_core import BaseFrameGenerationAlgorithm, RollingEventBufferConfig, RollingEventCDBuffer
from metavision_sdk_cv import ActivityNoiseFilterAlgorithm, TrailFilterAlgorithm
from metavision_sdk_ui import EventLoop, BaseWindow, MTWindow, UIAction, UIKeyEvent

update_frequency_hz = 1000 # Update every X Hz
accumulation_time_us = 10000

# Trail and Noise filtering
activity_time_ths = 10000
activity_trail_ths = 1000

min_obj_size = 25
max_obj_size = 200

def main():

    buffer_config = RollingEventBufferConfig.make_n_us(accumulation_time_us)
    rolling_buffer = RollingEventCDBuffer(buffer_config)
  

    delta_t = int(1000000 / update_frequency_hz)
    mv_iterator = EventsIterator(input_path="", delta_t=delta_t, mode="delta_t")

    height, width = mv_iterator.get_size()

    # Noise + Trail filter that will be applied to events
    activity_noise_filter = ActivityNoiseFilterAlgorithm(width, height, activity_time_ths)
    trail_filter = TrailFilterAlgorithm(width, height, activity_trail_ths)


    # Tracking Algorithm
    tracking_config = TrackingConfig()  # Default configuration
    tracking_algo = TrackingAlgorithm(sensor_width=width, sensor_height=height, tracking_config=tracking_config)
    tracking_algo.min_size = min_obj_size
    tracking_algo.max_size = max_obj_size

    output_img = np.zeros((height, width, 3), np.uint8)

    events_buf = ActivityNoiseFilterAlgorithm.get_empty_output_buffer()
    tracking_results = tracking_algo.get_empty_output_buffer()


    def get_corner_points(tracking_results):
        
        top_left = top_right = bottom_left = bottom_right = (tracking_results[0][0], tracking_results[0][1])

        for bbox in tracking_results:

            x, y, time, xx, yy, b_width, b_height, id, ascending_order = bbox

            b_width = int(b_width)
            b_height = int(b_height)

            x = int(xx)
            y = int(yy)

            if x + y < top_left[0] + top_left[1]:
                top_left = (x - b_width, y - b_height)
            
            if y <= top_right[1] and x > top_right[0]:
                top_right = (x + b_width, y - b_height)
            
            if x <= bottom_left[0] and y > bottom_left[1]:
                bottom_left = (x - b_width, y + b_height)
            
            if x + y > bottom_right[0] + bottom_right[1]:
                bottom_right = (x + b_width, y + b_height)

        potential_ball = (0,0)

        for point in tracking_results:
            x, y, time, xx, yy, b_width, b_height, id, ascending_order = point

            # Check if the point is inside the defined rectangle
            if x >= top_left[0] and x <= top_right[0] and y >= top_left[1] and y <= bottom_left[1]:
                potential_ball = (x,y)
                break 
        

        return top_left, top_right, bottom_right, bottom_left, potential_ball

    
    def process_tracking(evs):
        if len(evs) != 0:
            rolling_buffer.insert_events(evs)
            tracking_algo.process_events(rolling_buffer, tracking_results)

            BaseFrameGenerationAlgorithm.generate_frame(rolling_buffer, output_img)
            draw_tracking_results(evs['t'][-1], tracking_results, output_img)


            if tracking_results.numpy().shape[0] >= 4:
                tl, tr, br, bl, pt_ball = get_corner_points(tracking_results.numpy())

                color=(0, 255, 0)
                thickness = 2

                cv2.circle(output_img, pt_ball, radius=10, color=color, thickness=thickness)

                cv2.putText(output_img, "tl", tl, cv2.FONT_HERSHEY_PLAIN, 10, (0, 255, 0), 1)
                cv2.putText(output_img, "tr", tr, cv2.FONT_HERSHEY_PLAIN, 10, (0, 255, 0), 1)
                cv2.putText(output_img, "br", br, cv2.FONT_HERSHEY_PLAIN, 10, (0, 255, 0), 1)
                cv2.putText(output_img, "bl", bl, cv2.FONT_HERSHEY_PLAIN, 10, (0, 255, 0), 1)

                cv2.line(output_img, tl, tr, color, thickness) 
                cv2.line(output_img, tr, br, color, thickness) 
                cv2.line(output_img, br, bl, color, thickness) 
                cv2.line(output_img, bl, tl, color, thickness) 

        

        window.show_async(output_img)


    # Window - Graphical User Interface (Display tracking results and process keyboard events)
    with MTWindow(title="Generic Tracking", width=width, height=height, mode=BaseWindow.RenderMode.BGR) as window:
        window.show_async(output_img)

        def keyboard_cb(key, scancode, action, mods):
            

            if action != UIAction.RELEASE:
                return
            if key == UIKeyEvent.KEY_ESCAPE or key == UIKeyEvent.KEY_Q:
                window.set_close_flag()
           

        window.set_keyboard_callback(keyboard_cb)
        print("Press 'q' to leave the program.\n")


        for evs in mv_iterator:
            EventLoop.poll_and_dispatch()  # Dispatch system events to the window


            # Process events
            if activity_time_ths > 0:
                activity_noise_filter.process_events(evs, events_buf)
                if activity_trail_ths > 0:
                    trail_filter.process_events_(events_buf)

                process_tracking(events_buf.numpy())

            elif activity_trail_ths > 0:
                trail_filter.process_events(evs, events_buf)

                process_tracking(events_buf.numpy())
            else:
                process_tracking(evs)


            if window.should_close():
                break
       


if __name__ == "__main__":
    main()
