import cv2
import os
import threading
import time

class ObjectDetector:
    def __init__(self):
        self.cap = None
        self.is_running = False
        self.thread = None
        self.net = None
        self.class_names = []
        self.detected_objects = []
        
    def start_object_detection(self):
        """بدء التعرف على الأشياء"""
        if self.is_running:
            return {'status': 'error', 'message': 'الأداة تعمل بالفعل'}
            
        try:
            # تحميل ملفات النموذج
            self._load_model()
            
            self.cap = cv2.VideoCapture(0)
            self.cap.set(3, 740)
            self.cap.set(4, 580)
            self.is_running = True
            self.detected_objects = []
            
            # تشغيل الأداة في thread منفصل
            self.thread = threading.Thread(target=self._run_object_detection)
            self.thread.daemon = True
            self.thread.start()
            
            return {'status': 'success', 'message': 'تم بدء التعرف على الأشياء'}
        except Exception as e:
            return {'status': 'error', 'message': f'خطأ في بدء الأداة: {str(e)}'}
    
    def stop_object_detection(self):
        """إيقاف التعرف على الأشياء"""
        self.is_running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        return {'status': 'success', 'message': 'تم إيقاف التعرف على الأشياء'}
    
    def get_detected_objects(self):
        """الحصول على الأشياء المكتشفة"""
        return {'status': 'success', 'objects': self.detected_objects}
    
    def _load_model(self):
        """تحميل نموذج التعرف على الأشياء"""
        try:
            # تحميل أسماء الفئات
            class_file = 'ai_tools/projects/تعرف على الاشياء/coco.names'
            if os.path.exists(class_file):
                with open(class_file, 'rt') as f:
                    self.class_names = f.read().rstrip('\n').split('\n')
            else:
                # قائمة افتراضية للأشياء الشائعة
                self.class_names = [
                    'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train',
                    'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign',
                    'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep',
                    'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella'
                ]
            
            # تحميل النموذج
            config_path = 'ai_tools/projects/تعرف على الاشياء/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
            weights_path = 'ai_tools/projects/تعرف على الاشياء/frozen_inference_graph.pb'
            
            if os.path.exists(config_path) and os.path.exists(weights_path):
                self.net = cv2.dnn_DetectionModel(weights_path, config_path)
                self.net.setInputSize(320, 230)
                self.net.setInputScale(1.0 / 127.5)
                self.net.setInputMean((127.5, 127.5, 127.5))
                self.net.setInputSwapRB(True)
            else:
                # استخدام نموذج افتراضي
                self.net = cv2.dnn_DetectionModel(
                    'ai_tools/projects/تعرف على الاشياء/frozen_inference_graph.pb',
                    'ai_tools/projects/تعرف على الاشياء/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
                )
                self.net.setInputSize(320, 230)
                self.net.setInputScale(1.0 / 127.5)
                self.net.setInputMean((127.5, 127.5, 127.5))
                self.net.setInputSwapRB(True)
                
        except Exception as e:
            print(f"خطأ في تحميل النموذج: {e}")
            # استخدام نموذج افتراضي
            self.net = None
    
    def _run_object_detection(self):
        """تشغيل منطق التعرف على الأشياء"""
        while self.is_running and self.cap and self.cap.isOpened():
            try:
                success, img = self.cap.read()
                if not success:
                    break
                
                if self.net:
                    class_ids, confs, bbox = self.net.detect(img, confThreshold=0.5)
                    self.detected_objects = []
                    
                    if len(class_ids) != 0:
                        for class_id, confidence, box in zip(class_ids.flatten(), confs.flatten(), bbox):
                            if class_id - 1 < len(self.class_names):
                                object_name = self.class_names[class_id - 1]
                                self.detected_objects.append({
                                    'name': object_name,
                                    'confidence': float(confidence),
                                    'bbox': box.tolist()
                                })
                                
                                # رسم المستطيل والنص
                                cv2.rectangle(img, box, color=(0, 255, 0), thickness=2)
                                cv2.putText(img, object_name, (box[0] + 10, box[1] + 20),
                                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), thickness=2)
                
                # لا نعرض نافذة خارجية - كل شيء داخل الموقع
                # استخدام cv2.waitKey() مع timeout قصير لتجنب تجميد الكاميرا
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                time.sleep(0.01)  # تأخير قصير لتجنب الاستهلاك المفرط للمعالج
                    
            except Exception as e:
                print(f"خطأ في تشغيل الأداة: {e}")
                break
        
        # تنظيف الموارد
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

# إنشاء instance عام للاستخدام
object_detector = ObjectDetector()

def start_object_detection():
    """دالة لبدء التعرف على الأشياء"""
    return object_detector.start_object_detection()

def stop_object_detection():
    """دالة لإيقاف التعرف على الأشياء"""
    return object_detector.stop_object_detection()

def get_detected_objects():
    """دالة للحصول على الأشياء المكتشفة"""
    return object_detector.get_detected_objects()


