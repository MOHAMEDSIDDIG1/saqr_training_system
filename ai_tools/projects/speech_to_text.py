import speech_recognition as sr
import arabic_reshaper
from bidi.algorithm import get_display
import threading
import time

class SpeechToTextConverter:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.is_listening = False
        self.thread = None
        self.last_text = ""
        
    def start_speech_to_text(self, language='ar-AR'):
        """بدء تحويل الكلام إلى نص"""
        if self.is_listening:
            return {'status': 'error', 'message': 'الأداة تعمل بالفعل'}
            
        try:
            self.is_listening = True
            self.language = language
            
            # تشغيل الأداة في thread منفصل
            self.thread = threading.Thread(target=self._listen_continuously)
            self.thread.daemon = True
            self.thread.start()
            
            return {'status': 'success', 'message': 'تم بدء تحويل الكلام إلى نص'}
        except Exception as e:
            return {'status': 'error', 'message': f'خطأ في بدء الأداة: {str(e)}'}
    
    def stop_speech_to_text(self):
        """إيقاف تحويل الكلام إلى نص"""
        self.is_listening = False
        return {'status': 'success', 'message': 'تم إيقاف تحويل الكلام إلى نص'}
    
    def get_last_text(self):
        """الحصول على آخر نص تم التعرف عليه"""
        return {'status': 'success', 'text': self.last_text}
    
    def recognize_speech_once(self, language='ar-AR'):
        """التعرف على الكلام مرة واحدة"""
        try:
            with sr.Microphone() as mic:
                self.recognizer.adjust_for_ambient_noise(mic, duration=0.2)
                audio = self.recognizer.listen(mic, timeout=5)
                text = self.recognizer.recognize_google(audio, language=language)
                
                # معالجة النص العربي
                if language == 'ar-AR':
                    reshaped_text = arabic_reshaper.reshape(text)
                    bidi_text = get_display(reshaped_text)
                    self.last_text = bidi_text
                else:
                    self.last_text = text
                
                return {'status': 'success', 'text': self.last_text}
        except sr.UnknownValueError:
            return {'status': 'error', 'message': 'لم يتم التعرف على الكلام'}
        except sr.RequestError:
            return {'status': 'error', 'message': 'لا يوجد اتصال بالإنترنت'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _listen_continuously(self):
        """الاستماع المستمر للكلام"""
        while self.is_listening:
            try:
                with sr.Microphone() as mic:
                    self.recognizer.adjust_for_ambient_noise(mic, duration=0.2)
                    audio = self.recognizer.listen(mic, timeout=1)
                    text = self.recognizer.recognize_google(audio, language=self.language)
                    
                    # معالجة النص العربي
                    if self.language == 'ar-AR':
                        reshaped_text = arabic_reshaper.reshape(text)
                        bidi_text = get_display(reshaped_text)
                        self.last_text = bidi_text
                    else:
                        self.last_text = text
                    
                    print(f"تم التعرف على: {self.last_text}")
                    
            except sr.UnknownValueError:
                # لا نفعل شيئاً إذا لم يتم التعرف على الكلام
                pass
            except sr.RequestError:
                print("خطأ في الاتصال بالإنترنت")
                break
            except Exception as e:
                print(f"خطأ في الاستماع: {e}")
                break
            
            time.sleep(0.1)  # تأخير قصير لتجنب الاستهلاك المفرط للمعالج

# إنشاء instance عام للاستخدام
speech_converter = SpeechToTextConverter()

def start_speech_to_text(language='ar-AR'):
    """دالة لبدء تحويل الكلام إلى نص"""
    return speech_converter.start_speech_to_text(language)

def stop_speech_to_text():
    """دالة لإيقاف تحويل الكلام إلى نص"""
    return speech_converter.stop_speech_to_text()

def recognize_speech_once(language='ar-AR'):
    """دالة للتعرف على الكلام مرة واحدة"""
    return speech_converter.recognize_speech_once(language)

def get_last_text():
    """دالة للحصول على آخر نص تم التعرف عليه"""
    return speech_converter.get_last_text()



