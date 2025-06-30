"""
    Unibot, an open-source colorbot.
    Copyright (C) 2025 vike256

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import cv2
import numpy as np
import time
import threading
from typing import Optional, Tuple
from windows_capture import WindowsCapture, Frame, InternalCaptureControl


class Screen:
    def __init__(self, config):
        self.offset = config.offset

        # Get screen resolution
        if config.auto_detect_resolution:
            # We'll detect resolution from the first frame
            self.screen = None
        else:
            self.screen = (config.resolution_x, config.resolution_y)

        self.screen_center = None
        self.screen_region = None
        self.fov = (config.fov_x, config.fov_y)
        self.fov_center = (self.fov[0] // 2, self.fov[1] // 2)
        self.fov_region = None
        self.detection_threshold = config.detection_threshold
        self.upper_color = config.upper_color
        self.lower_color = config.lower_color
        self.fps = config.fps
        self.aim_height = config.aim_height
        self.debug = config.debug
        self.thresh = None
        self.target = None
        self.closest_contour = None
        self.img = None
        self.trigger_threshold = config.trigger_threshold
        self.aim_fov = (config.aim_fov_x, config.aim_fov_y)
        
        # Clustering and filtering settings
        self.min_contour_area = config.min_contour_area
        self.density_threshold = config.density_threshold
        self.enable_clustering = config.enable_clustering
        self.cluster_distance = config.cluster_distance
        self.min_cluster_size = config.min_cluster_size
        self.max_cluster_size = config.max_cluster_size

        # Frame capture variables
        self.latest_frame = None
        self.latest_full_frame = None  # Store full frame for debug display
        self.frame_lock = threading.Lock()
        self.capture_active = False
        
        # FPS tracking for debug
        self.frame_times = []
        self.last_fps_update = time.time()
        self.current_fps = 0.0
        self.current_loop_fps = 0.0

        # Setup debug display
        if self.debug:
            self.display_mode = config.display_mode
            self.window_name = 'Python'
            self.window_resolution = None
            cv2.namedWindow(self.window_name)

        # Initialize Windows Capture
        # Note: monitor_index uses 1-based indexing (1 = primary monitor)
        # Try to capture without any artificial limitations
        # TODO: Could optimize by capturing specific window instead of full screen
        self.capture = WindowsCapture(
            cursor_capture=False,
            draw_border=False,
            monitor_index=1,  # Primary monitor (1-based indexing)
            window_name=None,  # Could specify game window name here
        )

        # Set up event handlers
        @self.capture.event
        def on_frame_arrived(frame: Frame, capture_control: InternalCaptureControl):
            with self.frame_lock:
                # Convert frame to BGR format for OpenCV
                bgr_frame = frame.convert_to_bgr()
                full_frame = bgr_frame.frame_buffer.copy()
                
                # Immediately crop to FOV region for better performance
                if self.fov_region is not None:
                    x1, y1, x2, y2 = self.fov_region
                    # Ensure coordinates are within bounds
                    x1 = max(0, min(x1, frame.width))
                    y1 = max(0, min(y1, frame.height))
                    x2 = max(0, min(x2, frame.width))
                    y2 = max(0, min(y2, frame.height))
                    
                    if x2 > x1 and y2 > y1:
                        # Store only the FOV region instead of full frame
                        self.latest_frame = full_frame[y1:y2, x1:x2].copy()
                        # Also store full frame for debug display
                        self.latest_full_frame = full_frame
                    else:
                        self.latest_frame = full_frame
                        self.latest_full_frame = full_frame
                else:
                    self.latest_frame = full_frame
                    self.latest_full_frame = full_frame
                
                # Track FPS for debug display
                current_time = time.time()
                self.frame_times.append(current_time)
                
                # Keep only last 30 frame times for rolling average
                if len(self.frame_times) > 30:
                    self.frame_times.pop(0)
                
                # Update FPS every 0.5 seconds
                if current_time - self.last_fps_update > 0.5 and len(self.frame_times) > 1:
                    time_span = self.frame_times[-1] - self.frame_times[0]
                    if time_span > 0:
                        self.current_fps = (len(self.frame_times) - 1) / time_span
                    self.last_fps_update = current_time
                
                # Initialize screen dimensions on first frame
                if self.screen is None:
                    self.screen = (frame.width, frame.height)
                    self._update_screen_regions()

        @self.capture.event
        def on_closed():
            print("Screen capture session closed")
            self.capture_active = False

        # Start capture in background
        self.capture_control = self.capture.start_free_threaded()
        self.capture_active = True
        
        # Wait for first frame to initialize dimensions
        timeout = 5.0
        start_time = time.time()
        while self.screen is None and time.time() - start_time < timeout:
            time.sleep(0.01)
        
        if self.screen is None:
            raise RuntimeError("Failed to capture initial frame within timeout")

    def _update_screen_regions(self):
        """Update screen regions after screen dimensions are known"""
        if self.screen is None:
            return
            
        self.screen_center = (self.screen[0] // 2, self.screen[1] // 2)
        self.screen_region = (0, 0, self.screen[0], self.screen[1])
        self.fov_region = (
            self.screen_center[0] - self.fov[0] // 2,
            self.screen_center[1] - self.fov[1] // 2 - self.offset,
            self.screen_center[0] + self.fov[0] // 2,
            self.screen_center[1] + self.fov[1] // 2 - self.offset
        )
        
        if self.debug and self.window_resolution is None:
            self.window_resolution = (self.screen[0] // 2, self.screen[1] // 2)

    def __del__(self):
        if hasattr(self, 'capture_control'):
            self.capture_control.stop()

    def screenshot(self, region):
        """Get a screenshot of the specified region"""
        # Try to minimize lock time
        latest_frame = None
        with self.frame_lock:
            if self.latest_frame is not None:
                latest_frame = self.latest_frame
        
        if latest_frame is None:
            return None
        
        # Validate region coordinates
        x1, y1, x2, y2 = region
        if x1 < 0 or y1 < 0 or x2 <= x1 or y2 <= y1:
            return None
        
        # Check if we have the full frame stored
        full_frame = None
        with self.frame_lock:
            if self.latest_full_frame is not None:
                full_frame = self.latest_full_frame
        
        if full_frame is None:
            return None
        
        # Use full frame for region extraction
        frame_height, frame_width = full_frame.shape[:2]
        x1 = max(0, min(x1, frame_width))
        y1 = max(0, min(y1, frame_height))
        x2 = max(0, min(x2, frame_width))
        y2 = max(0, min(y2, frame_height))
        
        if x2 <= x1 or y2 <= y1:
            return None
            
        # Extract region from full frame
        cropped = full_frame[y1:y2, x1:x2]
        return cropped.copy()

    def get_target(self, recoil_offset):
        """Get target position and trigger state"""
        if self.screen is None:
            return None, False
            
        # Convert the offset to an integer, since it is used to define the capture region
        recoil_offset = int(recoil_offset)

        # Reset variables
        self.target = None
        trigger = False
        self.closest_contour = None

        # Capture a screenshot
        capture_region = self.get_region(self.fov_region, recoil_offset)
        self.img = self.screenshot(capture_region)
        
        if self.img is None:
            if self.debug:
                print(f"Screenshot failed for region: {capture_region}")
            return None, False
            
        if self.img.size == 0:
            if self.debug:
                print(f"Empty screenshot for region: {capture_region}")
            return None, False

        # Check if image has valid dimensions
        if len(self.img.shape) != 3 or self.img.shape[0] == 0 or self.img.shape[1] == 0:
            if self.debug:
                print(f"Invalid image dimensions: {self.img.shape} for region: {capture_region}")
            return None, False

        # Convert the screenshot to HSV color space for color detection
        hsv = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)

        # Create a mask to identify pixels within the specified color range
        mask = cv2.inRange(hsv, self.lower_color, self.upper_color)

        # Apply morphological dilation to increase the size of the detected color blobs
        kernel = np.ones((self.detection_threshold[0], self.detection_threshold[1]), np.uint8)
        dilated = cv2.dilate(mask, kernel, iterations=5)

        # Apply thresholding to convert the mask into a binary image
        self.thresh = cv2.threshold(dilated, 60, 255, cv2.THRESH_BINARY)[1]

        # Find contours of the detected color blobs
        contours, _ = cv2.findContours(self.thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        # Filter and cluster contours
        filtered_contours = self.filter_and_cluster_contours(contours)

        # Identify the closest target contour
        if len(filtered_contours) != 0:
            min_distance = float('inf')
            for contour in filtered_contours:
                # Make a bounding rectangle for the target
                rect_x, rect_y, rect_w, rect_h = cv2.boundingRect(contour)

                # Calculate the coordinates of the center of the target
                x = rect_x + rect_w // 2 - self.fov_center[0]
                y = int(rect_y + rect_h * (1 - self.aim_height)) - self.fov_center[1]

                # Update the closest target if the current target is closer
                distance = np.sqrt(x**2 + y**2)
                if distance < min_distance:
                    min_distance = distance
                    self.closest_contour = contour
                    if (
                            -self.aim_fov[0] <= x <= self.aim_fov[0] and
                            -self.aim_fov[1] <= y <= self.aim_fov[1]
                    ):
                        self.target = (x, y)

            if self.closest_contour is not None and (
                # Check if crosshair is inside the closest target
                cv2.pointPolygonTest(
                    self.closest_contour, (self.fov_center[0], self.fov_center[1]), False) >= 0 and

                # Eliminate a lot of false positives by also checking pixels near the crosshair.
                cv2.pointPolygonTest(
                    self.closest_contour, (self.fov_center[0] + self.trigger_threshold, self.fov_center[1]), False) >= 0 and
                cv2.pointPolygonTest(
                    self.closest_contour, (self.fov_center[0] - self.trigger_threshold, self.fov_center[1]), False) >= 0 and
                cv2.pointPolygonTest(
                    self.closest_contour, (self.fov_center[0], self.fov_center[1] + self.trigger_threshold), False) >= 0 and
                cv2.pointPolygonTest(
                    self.closest_contour, (self.fov_center[0], self.fov_center[1] - self.trigger_threshold), False) >= 0
            ):
                trigger = True

        if self.debug:
            self.debug_display(recoil_offset)

        return self.target, trigger

    def filter_and_cluster_contours(self, contours):
        """Filter small contours and cluster nearby ones into single targets"""
        if not contours:
            return []
        
        # Step 1: Filter by minimum area
        filtered_contours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area >= self.min_contour_area:
                filtered_contours.append(contour)
        
        if not self.enable_clustering or not filtered_contours:
            return filtered_contours
        
        # Step 2: Cluster nearby contours
        # Get contour centers
        centers = []
        for contour in filtered_contours:
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                centers.append((cx, cy, contour))
        
        if not centers:
            return filtered_contours
        
        # Simple clustering based on distance
        clusters = []
        used = [False] * len(centers)
        
        for i, (cx1, cy1, contour1) in enumerate(centers):
            if used[i]:
                continue
                
            cluster = [contour1]
            used[i] = True
            
            # Find nearby contours
            for j, (cx2, cy2, contour2) in enumerate(centers):
                if used[j]:
                    continue
                    
                distance = np.sqrt((cx1 - cx2)**2 + (cy1 - cy2)**2)
                if distance <= self.cluster_distance:
                    cluster.append(contour2)
                    used[j] = True
            
            clusters.append(cluster)
        
        # Step 3: Merge clusters into single contours
        merged_contours = []
        for cluster in clusters:
            if len(cluster) == 1:
                # Single contour, check if it meets size requirements
                area = cv2.contourArea(cluster[0])
                if self.min_cluster_size <= area <= self.max_cluster_size:
                    merged_contours.append(cluster[0])
            else:
                # Multiple contours, merge them
                merged_contour = self.merge_contours(cluster)
                if merged_contour is not None:
                    area = cv2.contourArea(merged_contour)
                    if self.min_cluster_size <= area <= self.max_cluster_size:
                        merged_contours.append(merged_contour)
        
        return merged_contours
    
    def merge_contours(self, contours):
        """Merge multiple contours into a single contour using convex hull"""
        if not contours:
            return None
        
        # Combine all points from all contours
        all_points = []
        for contour in contours:
            all_points.extend(contour.reshape(-1, 2))
        
        if len(all_points) < 3:
            return None
        
        # Create convex hull
        all_points = np.array(all_points)
        hull = cv2.convexHull(all_points)
        
        return hull

    @staticmethod
    def get_region(region, recoil_offset):
        """Adjust region based on recoil offset"""
        region = (
            region[0],
            region[1] - recoil_offset,
            region[2],
            region[3] - recoil_offset
        )
        return region

    def debug_display(self, recoil_offset):
        """Display debug information"""
        if not self.debug or self.screen is None:
            return
            
        if self.display_mode == 'game':
            debug_img = self.img
        else:
            debug_img = self.thresh
            if debug_img is not None:
                debug_img = cv2.cvtColor(debug_img, cv2.COLOR_GRAY2BGR)

        if debug_img is None:
            return

        # Use full frame for debug display
        with self.frame_lock:
            full_img = self.latest_full_frame.copy() if self.latest_full_frame is not None else None
        if full_img is None:
            return

        # Draw line to the closest target
        if self.target is not None:
            debug_img = cv2.line(
                debug_img,
                self.fov_center,
                (self.target[0] + self.fov_center[0], self.target[1] + self.fov_center[1]),
                (0, 255, 0),
                2
            )

        # Draw rectangle around closest target
        if self.closest_contour is not None:
            x, y, w, h = cv2.boundingRect(self.closest_contour)
            debug_img = cv2.rectangle(
                debug_img,
                (x, y),
                (x + w, y + h),
                (0, 0, 255),
                2
            )

        # Draw FOV, a green rectangle
        debug_img = cv2.rectangle(
            debug_img,
            (0, 0),
            (self.fov[0], self.fov[1]),
            (0, 255, 0),
            2
        )

        # Draw Aim FOV, a yellow rectangle
        debug_img = cv2.rectangle(
            debug_img,
            (
                self.fov[0] // 2 - self.aim_fov[0] // 2,
                self.fov[1] // 2 - self.aim_fov[1] // 2
            ),
            (
                self.fov[0] // 2 + self.aim_fov[0] // 2,
                self.fov[1] // 2 + self.aim_fov[1] // 2
            ),
            (0, 255, 255),
            2
        )

        # Overlay debug image on full screen
        if self.screen:
            offset_x = (self.screen[0] - self.fov[0]) // 2
            offset_y = (self.screen[1] - self.fov[1]) // 2 - self.offset - recoil_offset
            
            # Ensure overlay coordinates are within bounds
            if (full_img is not None and debug_img is not None and
                0 <= offset_y < full_img.shape[0] and 
                0 <= offset_x < full_img.shape[1] and
                offset_y + debug_img.shape[0] <= full_img.shape[0] and
                offset_x + debug_img.shape[1] <= full_img.shape[1]):
                
                full_img[offset_y:offset_y+debug_img.shape[0], offset_x:offset_x+debug_img.shape[1]] = debug_img
            
            # Draw a rectangle crosshair
            if self.screen_center:
                full_img = cv2.rectangle(
                    full_img,
                    (self.screen_center[0] - 5, self.screen_center[1] - 5),
                    (self.screen_center[0] + 5, self.screen_center[1] + 5),
                    (255, 255, 255),
                    1
                )
            
            # Add FPS display in debug mode
            fps_text = f"Capture FPS: {self.current_fps:.1f}"
            cv2.putText(full_img, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            # Add loop FPS display
            loop_fps_text = f"Loop FPS: {self.current_loop_fps:.1f}"
            cv2.putText(full_img, loop_fps_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            
            # Add target info if available
            if self.target is not None:
                target_text = f"Target: ({self.target[0]}, {self.target[1]})"
                cv2.putText(full_img, target_text, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            else:
                no_target_text = "No Target"
                cv2.putText(full_img, no_target_text, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            if self.window_resolution:
                full_img = cv2.resize(full_img, self.window_resolution)
                cv2.imshow(self.window_name, full_img)
                cv2.waitKey(1) 