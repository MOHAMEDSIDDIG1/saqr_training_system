#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار عرض نظيف بدون نصوص
"""

import cv2
import mediapipe as mp

def test_clean_display():
    """اختبار عرض نظيف بدون نصوص"""
    print("🧪 اختبار عرض نظيف بدون نصوص")
    print("=" * 50)
    
    # إعداد MediaPipe
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.4,
        min_tracking_confidence=0.4,
        model_complexity=1
    )
    mp_drawing = mp.solutions.drawing_utils
    
    # فتح الكاميرا
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ لا يمكن فتح الكاميرا")
        return False
    
    print("✅ تم فتح الكاميرا بنجاح")
    print("💡 ضع يدك أمام الكاميرا")
    print("💡 ستظهر النقاط بدون أي نصوص")
    print("💡 اضغط ESC لإيقاف الاختبار")
    
    while True:
        success, img = cap.read()
        if not success:
            break
        
        # قلب الصورة
        img = cv2.flip(img, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)
        
        # رسم النقاط إذا تم اكتشاف اليد
        if results.multi_hand_landmarks:
            for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # رسم نقاط اليد
                mp_drawing.draw_landmarks(
                    img, 
                    hand_landmarks, 
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=3, circle_radius=5),
                    mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=3)
                )
                
                # رسم دائرة على الإصبع السبابة
                index_tip = hand_landmarks.landmark[8]
                index_x = int(index_tip.x * img.shape[1])
                index_y = int(index_tip.y * img.shape[0])
                cv2.circle(img, (index_x, index_y), 15, (0, 255, 0), cv2.FILLED)
                
                # رسم دائرة على الإبهام
                thumb_tip = hand_landmarks.landmark[4]
                thumb_x = int(thumb_tip.x * img.shape[1])
                thumb_y = int(thumb_tip.y * img.shape[0])
                cv2.circle(img, (thumb_x, thumb_y), 12, (255, 0, 0), cv2.FILLED)
        
        # عرض الصورة بدون أي نصوص
        cv2.imshow('Clean Hand Detection', img)
        
        # التحقق من الضغط على ESC
        if cv2.waitKey(5) & 0xFF == 27:  # ESC
            break
    
    # تنظيف الموارد
    cap.release()
    cv2.destroyAllWindows()
    hands.close()
    
    print("✅ تم إيقاف الاختبار")
    return True

if __name__ == "__main__":
    test_clean_display()

