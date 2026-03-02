#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
عداد الأصابع المستقل - نسخة مبسطة تعمل بدون Django
مقارنة مع الكود البسيط المقدم
"""

import cv2
import mediapipe as mp
import threading
import time

class StandaloneFingerCounter:
    def __init__(self):
        self.running = False
        self.thread = None
        self.tip_ids = [4, 8, 12, 16, 20]  # نقاط أطراف الأصابع
        self.finger_count = 0
        
        # إعداد MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = None
        self.mp_drawing = mp.solutions.drawing_utils
        
    def start(self):
        """بدء العد"""
        if self.running:
            return {'status': 'error', 'message': 'الأداة تعمل بالفعل'}
        
        try:
            # إعداد MediaPipe
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.4,
                min_tracking_confidence=0.4,
                model_complexity=1
            )
            
            self.running = True
            self.finger_count = 0
            
            # تشغيل في thread منفصل
            self.thread = threading.Thread(target=self._run_counter, daemon=True)
            self.thread.start()
            
            return {'status': 'success', 'message': 'تم بدء العد بنجاح'}
        except Exception as e:
            return {'status': 'error', 'message': f'خطأ في البدء: {str(e)}'}
    
    def stop(self):
        """إيقاف العد"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        if self.hands:
            self.hands.close()
        return {'status': 'success', 'message': 'تم إيقاف العد'}
    
    def get_count(self):
        """الحصول على عدد الأصابع"""
        return {'status': 'success', 'count': self.finger_count}
    
    def _run_counter(self):
        """تشغيل العد"""
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ لا يمكن فتح الكاميرا")
            return
        
        print("✅ تم فتح الكاميرا بنجاح")
        
        while self.running and cap.isOpened():
            success, img = cap.read()
            if not success:
                break
            
            # قلب الصورة
            img = cv2.flip(img, 1)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(img_rgb)
            
            # إعادة تعيين عدد الأصابع
            self.finger_count = 0
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # رسم نقاط اليد
                    self.mp_drawing.draw_landmarks(
                        img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=2),
                        self.mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2)
                    )
                    
                    # جمع نقاط اليد
                    lm_list = []
                    for id, lm in enumerate(hand_landmarks.landmark):
                        h, w, c = img.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        lm_list.append([id, cx, cy])
                        
                        # دائرة على الإصبع السبابة
                        if id == 8:
                            cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)
                    
                    # حساب عدد الأصابع
                    if len(lm_list) == 21:
                        fingers = []
                        
                        # الإبهام (مقارنة x)
                        if lm_list[self.tip_ids[0]][1] < lm_list[self.tip_ids[0] - 2][1]:
                            fingers.append(1)
                        else:
                            fingers.append(0)
                        
                        # باقي الأصابع (مقارنة y)
                        for tip in range(1, 5):
                            if lm_list[self.tip_ids[tip]][2] < lm_list[self.tip_ids[tip] - 2][2]:
                                fingers.append(1)
                            else:
                                fingers.append(0)
                        
                        self.finger_count = fingers.count(1)
                        print(f"🔢 عدد الأصابع: {self.finger_count}")
                        
                        # عرض النص على الصورة
                        cv2.putText(img, f'Fingers: {self.finger_count}', (40, 80),
                                    cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 6)
            
            # عرض الصورة
            cv2.imshow('Standalone Finger Counter', img)
            
            # التحقق من الضغط على ESC
            if cv2.waitKey(5) & 0xFF == 27:  # ESC
                self.running = False
                break
        
        # تنظيف الموارد
        cap.release()
        cv2.destroyAllWindows()
        if self.hands:
            self.hands.close()
        
        print("✅ تم إيقاف العد")

def main():
    """الدالة الرئيسية"""
    print("🧪 اختبار العد المستقل")
    print("=" * 40)
    
    counter = StandaloneFingerCounter()
    
    # اختبار البدء
    print("🚀 بدء العد...")
    result = counter.start()
    print(f"النتيجة: {result}")
    
    if result['status'] == 'success':
        print("✅ تم بدء العد بنجاح")
        print("📹 ستظهر نافذة الكاميرا")
        print("💡 اضغط ESC لإيقاف العد")
        print("💡 ضع يدك أمام الكاميرا لرؤية العد")
        
        # انتظار حتى يضغط المستخدم ESC
        try:
            while counter.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n⏹️ تم إيقاف العد بواسطة المستخدم")
        
        # إيقاف العد
        print("🛑 إيقاف العد...")
        result = counter.stop()
        print(f"النتيجة: {result}")
        
        if result['status'] == 'success':
            print("✅ تم إيقاف العد بنجاح")
        else:
            print(f"❌ خطأ في الإيقاف: {result['message']}")
    else:
        print(f"❌ فشل في البدء: {result['message']}")

if __name__ == "__main__":
    main()

