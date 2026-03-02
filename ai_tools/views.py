
from django.shortcuts import render, redirect
from django.http import JsonResponse, StreamingHttpResponse
import json

# استيراد الدوال من ملفات المشاريع المنفصلة
from .projects.eye_mouse import start_eye_mouse, stop_eye_mouse, get_performance_stats, get_current_frame, adjust_sensitivity, reset_state, eye_mouse_controller
from .projects.hand_mouse import start_hand_mouse, stop_hand_mouse, get_performance_stats, adjust_sensitivity, reset_state, get_current_frame, hand_mouse_controller
from .projects.voice_control import start_voice_control, stop_voice_control, get_performance_stats, get_current_frame, reset_state, adjust_volume_stability, adjust_volume_precision, check_and_reset_state, test_volume_control, force_volume_change, voice_controller
from .projects.finger_counter import start_finger_counter, stop_finger_counter, get_finger_count, get_performance_stats, get_current_frame, reset_state, test_hand_detection, adjust_detection_settings, check_frame_status, force_start, reset_completely, diagnose_camera_issue, test_landmark_drawing, force_reset_and_start, finger_counter
from .projects.speech_to_text import start_speech_to_text, stop_speech_to_text, recognize_speech_once, get_last_text
from .projects.text_to_speech import start_text_to_speech, stop_text_to_speech, speak_text, speak_text_async, is_speaking_now
from .projects.object_detection import start_object_detection, stop_object_detection, get_detected_objects
# from .projects.motion_detection import start_motion_detection, stop_motion_detection, get_motion_status, set_sensitivity
from .projects.hand_game import start_hand_game, stop_hand_game, get_game_score, reset_game
from .projects.qr_generator import generate_qr_code, save_qr_code, generate_qr_with_logo
from .projects.motion_detection import start_detection, stop_detection, get_motion_state, is_running, check_camera, get_alert_count, reset_alert_count

def home(request):
    """الصفحة الرئيسية للموقع"""
    return render(request, 'ai_tools/home.html')


def motion_detection(request):
    """عرض صفحة كشف الحركة في الظلام"""
    return render(request, 'ai_tools/motion_detection.html')


def start_motion_detection(request):
    if request.method == 'POST':
        # refuse to start if camera cannot be opened
        if not check_camera(0):
            return JsonResponse({'status': 'error', 'message': 'camera_unavailable'}, status=400)
        ok = start_detection(show=False)
        if not ok:
            return JsonResponse({'status': 'error', 'message': 'already_running'}, status=400)
        return JsonResponse({'status': 'started'})
    return JsonResponse({'status': 'error'})


def stop_motion_detection(request):
    if request.method == 'POST':
        ok = stop_detection()
        return JsonResponse({'status': 'stopped' if ok else 'not_running'})
    return JsonResponse({'status': 'error'})


def motion_status(request):
    running = is_running()
    camera_ok = check_camera(0)
    return JsonResponse({'motion': bool(get_motion_state()), 'running': running, 'camera_ok': camera_ok, 'alerts': get_alert_count()})


def reset_alerts(request):
    if request.method == 'POST':
        reset_alert_count()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'})

def eye_mouse(request):
    """التحكم بالماوس بالعين"""
    if request.method == 'POST':
        action = request.POST.get('action', 'start')
        if action == 'start':
            result = start_eye_mouse()
        elif action == 'stop':
            result = stop_eye_mouse()
        elif action == 'get_stats':
            result = get_performance_stats()
        elif action == 'adjust_sensitivity':
            smoothing_factor = request.POST.get('smoothing_factor')
            click_threshold = request.POST.get('click_threshold')
            result = adjust_sensitivity(
                float(smoothing_factor) if smoothing_factor else None,
                float(click_threshold) if click_threshold else None
            )
        elif action == 'reset':
            result = reset_state()
        else:
            result = {'status': 'error', 'message': 'إجراء غير صحيح'}
        return JsonResponse(result)
    return render(request, 'ai_tools/eye_mouse.html')

def hand_mouse(request):
    """التحكم بالماوس باليدين"""
    if request.method == 'POST':
        print(request.POST)
        action = request.POST.get('action', 'start')
        if action == 'start':
            result = start_hand_mouse()
        elif action == 'stop':
            result = stop_hand_mouse()
        elif action == 'get_stats':
            result = get_performance_stats()
        elif action == 'adjust_sensitivity':
            smoothing_factor = request.POST.get('smoothing_factor')
            click_threshold = request.POST.get('click_threshold')
            result = adjust_sensitivity(
                float(smoothing_factor) if smoothing_factor else None,
                float(click_threshold) if click_threshold else None
            )
        elif action == 'reset':
            result = reset_state()
        elif action == 'get_frame':
            frame = get_current_frame()
            if frame:
                result = {'status': 'success', 'frame': frame}
            else:
                result = {'status': 'error', 'message': 'لا يوجد إطار متاح'}
        else:
            result = {'status': 'error', 'message': 'إجراء غير صحيح'}
        return JsonResponse(result)
    return render(request, 'ai_tools/hand_mouse.html')

def voice_control(request):
    """التحكم في الصوت باليدين"""
    if request.method == 'POST':
        action = request.POST.get('action', 'start')
        if action == 'start':
            result = start_voice_control()
        elif action == 'stop':
            result = stop_voice_control()
        elif action == 'get_stats':
            result = get_performance_stats()
        elif action == 'reset':
            result = reset_state()
        elif action == 'adjust_stability':
            threshold = request.POST.get('threshold')
            stability_frames = request.POST.get('stability_frames')
            result = adjust_volume_stability(
                float(threshold) if threshold else None,
                int(stability_frames) if stability_frames else None
            )
        elif action == 'adjust_precision':
            min_distance = request.POST.get('min_distance')
            max_distance = request.POST.get('max_distance')
            start_threshold = request.POST.get('start_threshold')
            result = adjust_volume_precision(
                int(min_distance) if min_distance else None,
                int(max_distance) if max_distance else None,
                int(start_threshold) if start_threshold else None
            )
        elif action == 'check_state':
            result = check_and_reset_state()
        elif action == 'test_volume':
            result = test_volume_control()
        elif action == 'force_volume':
            percentage = request.POST.get('percentage')
            if percentage:
                result = force_volume_change(float(percentage))
            else:
                result = {'status': 'error', 'message': 'لم يتم تحديد النسبة المئوية'}
        else:
            result = {'status': 'error', 'message': 'إجراء غير صحيح'}
        return JsonResponse(result)
    return render(request, 'ai_tools/voice_control.html')

def finger_counter(request):
    """التعرف على عدد أصابع اليدين"""
    if request.method == 'POST':
        action = request.POST.get('action', 'start')
        if action == 'start':
            result = start_finger_counter()
        elif action == 'stop':
            result = stop_finger_counter()
        elif action == 'get_count':
            result = get_finger_count()
        elif action == 'get_stats':
            result = get_performance_stats()
        elif action == 'reset':
            result = reset_state()
        elif action == 'test_detection':
            result = test_hand_detection()
        elif action == 'adjust_settings':
            confidence = float(request.POST.get('confidence', 0.4))
            complexity = int(request.POST.get('complexity', 1))
            result = adjust_detection_settings(confidence, complexity)
        elif action == 'check_frame':
            result = check_frame_status()
        elif action == 'force_start':
            result = force_start()
        elif action == 'reset_completely':
            result = reset_completely()
        elif action == 'diagnose_camera':
            result = diagnose_camera_issue()
        elif action == 'test_landmarks':
            result = test_landmark_drawing()
        elif action == 'force_reset_start':
            result = force_reset_and_start()
        else:
            result = {'status': 'error', 'message': 'إجراء غير صحيح'}
        return JsonResponse(result)
    return render(request, 'ai_tools/finger_counter.html')

def virtual_mouse(request):
    """الماوس الافتراضي"""
    if request.method == 'POST':
        return JsonResponse({'status': 'started'})
    return render(request, 'ai_tools/virtual_mouse.html')

def speech_to_text(request):
    """تحويل الكلام إلى نص"""
    if request.method == 'POST':
        action = request.POST.get('action', 'recognize')
        language = request.POST.get('language', 'ar-AR')
        
        if action == 'start':
            result = start_speech_to_text(language)
        elif action == 'stop':
            result = stop_speech_to_text()
        elif action == 'recognize':
            result = recognize_speech_once(language)
        elif action == 'get_text':
            result = get_last_text()
        else:
            result = {'status': 'error', 'message': 'إجراء غير صحيح'}
        return JsonResponse(result)
    return render(request, 'ai_tools/speech_to_text.html')

def text_to_speech(request):
    """تحويل النص إلى كلام"""
    if request.method == 'POST':
        action = request.POST.get('action', 'speak')
        text = request.POST.get('text', '')
        language = request.POST.get('language', 'en')

        if action == 'start':
            result = start_text_to_speech()
        elif action == 'stop':
            result = stop_text_to_speech()
        elif action == 'speak':
            result = speak_text(text, language)
        elif action == 'speak_async':
            result = speak_text_async(text, language)
        elif action == 'is_speaking':
            result = is_speaking_now()
        else:
            result = {'status': 'error', 'message': 'إجراء غير صحيح'}
        return JsonResponse(result)
    return render(request, 'ai_tools/text_to_speech.html')

def object_detection(request):
    """التعرف على الأشياء"""
    if request.method == 'POST':
        action = request.POST.get('action', 'start')
        if action == 'start':
            result = start_object_detection()
        elif action == 'stop':
            result = stop_object_detection()
        elif action == 'get_objects':
            result = get_detected_objects()
        else:
            result = {'status': 'error', 'message': 'إجراء غير صحيح'}
        return JsonResponse(result)
    return render(request, 'ai_tools/object_detection.html')

# def motion_detection(request):
#     """التعرف على الحركة في الظلام"""
#     if request.method == 'POST':
#         action = request.POST.get('action', 'start')
#         if action == 'start':
#             result = start_motion_detection()
#         elif action == 'stop':
#             result = stop_motion_detection()
#         elif action == 'get_status':
#             result = get_motion_status()
#         elif action == 'set_sensitivity':
#             sensitivity = int(request.POST.get('sensitivity', 5000))
#             result = set_sensitivity(sensitivity)
#         else:
#             result = {'status': 'error', 'message': 'إجراء غير صحيح'}
#         return JsonResponse(result)
#     return render(request, 'ai_tools/motion_detection.html')

def qr_generator(request):
    """مولد QR Code"""
    if request.method == 'POST':
        action = request.POST.get('action', 'generate')
        text = request.POST.get('text', '')
        size = int(request.POST.get('size', 10))
        border = int(request.POST.get('border', 4))
        
        if action == 'generate':


            result = generate_qr_code(text, size, border)
        elif action == 'save':
            file_path = request.POST.get('file_path', 'qr_code.png')
            result = save_qr_code(text, file_path, size, border)
        elif action == 'generate_with_logo':
            logo_path = request.POST.get('logo_path', None)
            result = generate_qr_with_logo(text, logo_path, size, border)
        else:
            result = {'status': 'error', 'message': 'إجراء غير صحيح'}
        return JsonResponse(result)
    return render(request, 'ai_tools/qr_generator.html')

def hand_game(request):
    """لعبة تحكم باليدين"""
    if request.method == 'POST':
        action = request.POST.get('action', 'start')
        if action == 'start':
            result = start_hand_game()
        elif action == 'stop':
            result = stop_hand_game()
        elif action == 'get_score':
            result = get_game_score()
        elif action == 'reset':
            result = reset_game()
        else:
            result = {'status': 'error', 'message': 'إجراء غير صحيح'}
        return JsonResponse(result)
    return render(request, 'ai_tools/hand_game.html')

# دوال مساعدة للكاميرا (يمكن إزالتها إذا لم تعد مطلوبة)
def get_camera_feed():
    """توليد فيديو من الكاميرا"""
    import cv2
    import time
    import mediapipe as mp
    
    # فتح كاميرا للعرض
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        cap = cv2.VideoCapture(1)
    
    # فحص إذا كانت الكاميرا تعمل
    if not cap.isOpened():
        print("خطأ: لا يمكن فتح الكاميرا")
        # إرجاع صورة فارغة
        import numpy as np
        empty_frame = np.zeros((360, 480, 3), dtype=np.uint8)
        cv2.putText(empty_frame, "Camera Not Available", (50, 180), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        ret, buffer = cv2.imencode('.jpg', empty_frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
    cap.set(cv2.CAP_PROP_FPS, 60)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    # إعداد MediaPipe للعرض
    mp_hands = mp.solutions.hands
    mp_face_mesh = mp.solutions.face_mesh
    mp_drawing = mp.solutions.drawing_utils
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6,
        model_complexity=0
    )
    face_mesh = mp_face_mesh.FaceMesh(
        refine_landmarks=True,
        max_num_faces=1,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6
    )
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("خطأ في قراءة الإطار من الكاميرا")
                # إعادة محاولة فتح الكاميرا
                cap.release()
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    cap = cv2.VideoCapture(1)
                if not cap.isOpened():
                    print("لا يمكن فتح أي كاميرا")
                    break
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
                cap.set(cv2.CAP_PROP_FPS, 60)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                continue
            
            # معالجة اليدين والوجه على الإطار دائماً
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            hand_results = hands.process(image_rgb)
            face_results = face_mesh.process(image_rgb)
            
            # إرسال الإطار إلى hand_mouse إذا كانت تعمل
            if (hasattr(hand_mouse_controller, 'is_running') and hand_mouse_controller.is_running):
                with hand_mouse_controller.frame_lock:
                    hand_mouse_controller.current_frame = frame.copy()
            
            # إرسال الإطار إلى eye_mouse إذا كانت تعمل
            if (hasattr(eye_mouse_controller, 'is_running') and eye_mouse_controller.is_running):
                with eye_mouse_controller.frame_lock:
                    eye_mouse_controller.current_frame = frame.copy()
            
            # إرسال الإطار إلى voice_control إذا كانت تعمل
            if (hasattr(voice_controller, 'is_running') and voice_controller.is_running):
                with voice_controller.frame_lock:
                    voice_controller.current_frame = frame.copy()
            
            # إرسال الإطار إلى finger_counter إذا كانت تعمل
            finger_running = (hasattr(finger_counter, 'is_running') and finger_counter.is_running)
            if finger_running:
                try:
                    with finger_counter.frame_lock:
                        finger_counter.current_frame = frame.copy()
                    # طباعة رسالة التشخيص فقط عند الحاجة
                    if hasattr(finger_counter, '_last_frame_sent') and not finger_counter._last_frame_sent:
                        print(f"📤 تم إرسال الإطار إلى finger_counter - is_running: {finger_counter.is_running}")
                        print(f"📸 حجم الإطار المرسل: {frame.shape}")
                        finger_counter._last_frame_sent = True
                except Exception as e:
                    print(f"❌ خطأ في إرسال الإطار إلى finger_counter: {e}")
            else:
                # طباعة رسالة التشخيص فقط عند الحاجة
                if not hasattr(finger_counter, '_last_not_running_logged') or not finger_counter._last_not_running_logged:
                    print(f"❌ finger_counter not running - is_running: {getattr(finger_counter, 'is_running', False)}")
                    finger_counter._last_not_running_logged = True
                
                # محاولة إعادة تعيين الحالة إذا كانت معطلة
                if hasattr(finger_counter, 'is_running') and finger_counter.is_running and not (finger_counter.thread and finger_counter.thread.is_alive()):
                    print("🔄 إعادة تعيين finger_counter - Thread معطل")
                    finger_counter.is_running = False
                    finger_counter.thread = None
                    finger_counter._last_not_running_logged = False
            
            # رسم نقاط اليد فقط إذا كانت hand_mouse تعمل
            if (hasattr(hand_mouse_controller, 'is_running') and hand_mouse_controller.is_running and 
                hand_results.multi_hand_landmarks):
                for hand_landmarks in hand_results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame, 
                        hand_landmarks, 
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
                        mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
                    )
            
            # رسم نقاط العين فقط إذا كانت eye_mouse تعمل
            if (hasattr(eye_mouse_controller, 'is_running') and eye_mouse_controller.is_running and 
                face_results.multi_face_landmarks):
                landmarks = face_results.multi_face_landmarks[0].landmark
                frame_h, frame_w, _ = frame.shape
                
                # نقاط العين اليمنى
                right_eye_landmarks = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
                
                # رسم نقاط العين
                for idx in right_eye_landmarks:
                    if idx < len(landmarks):
                        landmark = landmarks[idx]
                        x = int(landmark.x * frame_w)
                        y = int(landmark.y * frame_h)
                        cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
                
                # رسم نقطة مركز العين
                if len(landmarks) > 468:
                    center_landmark = landmarks[468]
                    center_x = int(center_landmark.x * frame_w)
                    center_y = int(center_landmark.y * frame_h)
                    cv2.circle(frame, (center_x, center_y), 5, (255, 0, 0), -1)
                
                # رسم نقاط الجفن
                if len(landmarks) > 159:
                    upper_lid = landmarks[159]
                    lower_lid = landmarks[145]
                    
                    upper_x = int(upper_lid.x * frame_w)
                    upper_y = int(upper_lid.y * frame_h)
                    lower_x = int(lower_lid.x * frame_w)
                    lower_y = int(lower_lid.y * frame_h)
                    
                    cv2.circle(frame, (upper_x, upper_y), 3, (0, 255, 255), -1)
                    cv2.circle(frame, (lower_x, lower_y), 3, (0, 255, 255), -1)
            
            # رسم نقاط اليد فقط إذا كانت voice_control تعمل
            if (hasattr(voice_controller, 'is_running') and voice_controller.is_running and 
                hand_results.multi_hand_landmarks):
                for hand_landmarks in hand_results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame, 
                        hand_landmarks, 
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(255, 0, 255), thickness=2, circle_radius=4),
                        mp_drawing.DrawingSpec(color=(255, 0, 255), thickness=2)
                    )
                    
                    # رسم خط بين الإبهام والسبابة للتحكم في الصوت
                    thumb_tip = hand_landmarks.landmark[4]
                    index_tip = hand_landmarks.landmark[8]
                    
                    thumb_x = int(thumb_tip.x * frame.shape[1])
                    thumb_y = int(thumb_tip.y * frame.shape[0])
                    index_x = int(index_tip.x * frame.shape[1])
                    index_y = int(index_tip.y * frame.shape[0])
                    
                    # رسم خط ودائرتين للتحكم في الصوت
                    cv2.line(frame, (thumb_x, thumb_y), (index_x, index_y), (255, 0, 255), 3)
                    cv2.circle(frame, (thumb_x, thumb_y), 10, (255, 0, 255), cv2.FILLED)
                    cv2.circle(frame, (index_x, index_y), 10, (255, 0, 255), cv2.FILLED)
            
            # رسم نقاط اليد دائماً إذا تم اكتشاف اليد
            if hand_results.multi_hand_landmarks:
                # طباعة رسالة التشخيص فقط عند الحاجة
                if not hasattr(finger_counter, '_last_hand_detected') or not finger_counter._last_hand_detected:
                    print(f"✅ تم اكتشاف {len(hand_results.multi_hand_landmarks)} يد في camera_feed")
                    finger_counter._last_hand_detected = True
                
                for i, hand_landmarks in enumerate(hand_results.multi_hand_landmarks):
                    # رسم نقاط اليد دائماً
                    mp_drawing.draw_landmarks(
                        frame, 
                        hand_landmarks, 
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=3, circle_radius=5),
                        mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=3)
                    )
                    
                    # رسم دائرة على الإصبع السبابة
                    index_tip = hand_landmarks.landmark[8]
                    index_x = int(index_tip.x * frame.shape[1])
                    index_y = int(index_tip.y * frame.shape[0])
                    cv2.circle(frame, (index_x, index_y), 15, (0, 255, 0), cv2.FILLED)
                    
                    # رسم دائرة على الإبهام
                    thumb_tip = hand_landmarks.landmark[4]
                    thumb_x = int(thumb_tip.x * frame.shape[1])
                    thumb_y = int(thumb_tip.y * frame.shape[0])
                    cv2.circle(frame, (thumb_x, thumb_y), 12, (255, 0, 0), cv2.FILLED)
                    
                    # عرض عدد الأصابع فقط إذا كانت finger_counter تعمل
                    if (hasattr(finger_counter, 'is_running') and finger_counter.is_running and 
                        hasattr(finger_counter, 'finger_count')):
                        cv2.putText(frame, f'Fingers: {finger_counter.finger_count}', (40, 80),
                                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
                        print(f"🔢 عدد الأصابع: {finger_counter.finger_count}")
                    # لا نعرض أي نص إذا كانت الأداة معطلة
            else:
                # إعادة تعيين علامة اكتشاف اليد
                if hasattr(finger_counter, '_last_hand_detected'):
                    finger_counter._last_hand_detected = False
                # لا نطبع رسالة "لم يتم اكتشاف أي يد" لتجنب الإزعاج
            
            # إخفاء جميع النصوص على الكاميرا للحصول على عرض نظيف
            # يمكن إزالة هذا التعليق إذا كنت تريد إخفاء جميع النصوص
            
            # تحويل الإطار إلى JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                frame_bytes = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            else:
                print("خطأ في تحويل الإطار إلى JPEG")
            
            time.sleep(0.016)  # 60 FPS
    finally:
        cap.release()
        hands.close()

def camera_feed(request):
    """إرسال فيديو الكاميرا"""
    return StreamingHttpResponse(get_camera_feed(), content_type='multipart/x-mixed-replace; boundary=frame')
