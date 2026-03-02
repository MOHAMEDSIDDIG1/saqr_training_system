
import cv2
import numpy as np
import winsound
import threading
import time

# Module-level controller for background detection
_thread = None
_stop_event = None
_motion_state = False
_state_lock = threading.Lock()
_alert_count = 0
_alert_lock = threading.Lock()

_cap = None
_cap_lock = threading.Lock()


def _set_motion_state(val: bool):
    global _motion_state
    with _state_lock:
        _motion_state = bool(val)


def _inc_alert_count():
    global _alert_count
    with _alert_lock:
        _alert_count += 1


def get_alert_count():
    """Return total number of alerts (detections)."""
    with _alert_lock:
        return int(_alert_count)


def reset_alert_count():
    global _alert_count
    with _alert_lock:
        _alert_count = 0


def get_motion_state():
    """Return current detected motion state (bool)."""
    with _state_lock:
        return bool(_motion_state)


def _detection_loop(camera_index=0, min_area=700, threshold_value=12, consec_required=2, no_motion_release=3, show=False):
    """
    Internal detection loop. Detects motion by frame-difference and requires
    `consec_required` consecutive positive frames to flip to motion state.
    Resets to no-motion after `no_motion_release` frames without detection.
    """
    global _stop_event, _cap
    cap = cv2.VideoCapture(camera_index)
    with _cap_lock:
        _cap = cap
    if not cap.isOpened():
        with _cap_lock:
            _cap = None
        return

    # initialize counters used in the loop
    consec_count = 0
    no_motion_count = 0

    reconnect_attempts = 0
    while True:
        try:
            if _stop_event is not None and _stop_event.is_set():
                break

            ret1, f1 = cap.read()
            ret2, f2 = cap.read()
            if not ret1 or not ret2:
                # try to reconnect the camera a few times instead of exiting
                reconnect_attempts += 1
                cap.release()
                time.sleep(0.2)
                cap = cv2.VideoCapture(camera_index)
                if reconnect_attempts > 10:
                    # give up after several tries
                    print("motion_detection: camera read failed repeatedly, stopping detection loop")
                    break
                continue
            reconnect_attempts = 0

            diff = cv2.absdiff(f1, f2)
            gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            motion_found = False
            for c in contours:
                if cv2.contourArea(c) >= min_area:
                    motion_found = True
                    break

            if motion_found:
                consec_count += 1
                no_motion_count = 0
            else:
                consec_count = 0
                no_motion_count += 1

            # Transition to motion only after stable consecutive detections
            if consec_count >= consec_required and not get_motion_state():
                _set_motion_state(True)
                # beep once on detection
                try:
                    winsound.Beep(900, 500)
                except Exception:
                    pass
                # increment alert counter
                try:
                    _inc_alert_count()
                except Exception:
                    pass

            # Transition back to no-motion after sustained silence
            if no_motion_count >= no_motion_release and get_motion_state():
                _set_motion_state(False)

            # Optional debug display (shows thermal-like overlay)
            if show:
                black = np.zeros_like(f1)
                for c in contours:
                    if cv2.contourArea(c) < min_area:
                        continue
                    x, y, w, h = cv2.boundingRect(c)
                    center = (int(x + w / 2), int(y + h / 2))
                    axes = (int(w / 2), int(h / 2))
                    cv2.ellipse(black, center, axes, 0, 0, 360, (0, 0, 255), 2)
                status_text = "حركة مكتشفة" if get_motion_state() else "لا يوجد حركة"
                color_text = (0, 0, 255) if get_motion_state() else (255, 255, 255)
                cv2.putText(black, status_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, color_text, 2)
                cv2.imshow('Motion Detection (debug)', black)
                if cv2.waitKey(1) == 27:
                    break

            time.sleep(0.03)
        except Exception as e:
            # log exception and continue; do not kill the thread silently
            print(f"motion_detection exception: {e}")
            try:
                time.sleep(0.2)
            except Exception:
                pass
            continue

    try:
        cap.release()
    except Exception:
        pass
    try:
        cv2.destroyAllWindows()
    except Exception:
        pass
    with _cap_lock:
        _cap = None


def start_detection(camera_index=0, min_area=700, show=False):
    """Start background detection thread. Returns True if started, False if already running."""
    global _thread, _stop_event
    if _thread is not None and _thread.is_alive():
        return False
    _stop_event = threading.Event()
    _thread = threading.Thread(target=_detection_loop, args=(camera_index, min_area, 12, 2, 3, show), daemon=True)
    _thread.start()
    return True


def stop_detection():
    """Stop background detection if running."""
    global _thread, _stop_event
    if _stop_event is None:
        return False
    _stop_event.set()
    # attempt to release camera immediately to unblock any blocking read
    try:
        with _cap_lock:
            if _cap is not None:
                try:
                    _cap.release()
                except Exception:
                    pass
    except Exception:
        pass

    if _thread is not None:
        _thread.join(timeout=5.0)
    _thread = None
    _stop_event = None
    _set_motion_state(False)
    return True


def is_running():
    """Return True if the background detection thread is running."""
    global _thread
    return _thread is not None and _thread.is_alive()


def check_camera(camera_index=0):
    """Quickly check if a camera can be opened. Returns True/False."""
    cap = cv2.VideoCapture(camera_index)
    ok = cap.isOpened()
    if ok:
        cap.release()
    return bool(ok)
