import pyttsx3
import threading
import time

class TextToSpeechConverter:
    def __init__(self):
        self.engine = None
        self.is_speaking = False
        self.thread = None
        
    def start_text_to_speech(self):
        """بدء تحويل النص إلى كلام"""
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)  # سرعة الكلام
            self.engine.setProperty('volume', 0.9)  # مستوى الصوت
            # حاول اختيار صوت إنجليزي افتراضي إن كان متاحًا
            try:
                voices = self.engine.getProperty('voices')
                for voice in voices:
                    if 'english' in voice.name.lower() or 'en' in voice.id.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
            except Exception:
                pass

            return {'status': 'success', 'message': 'تم بدء تحويل النص إلى كلام (English only)'}
        except Exception as e:
            return {'status': 'error', 'message': f'خطأ في بدء الأداة: {str(e)}'}
    
    def stop_text_to_speech(self):
        """إيقاف تحويل النص إلى كلام"""
        if self.engine:
            self.engine.stop()
        self.is_speaking = False
        return {'status': 'success', 'message': 'تم إيقاف تحويل النص إلى كلام'}
    
    def speak_text(self, text, language='en'):
        """تحويل النص إلى كلام"""
        if not text:
            return {'status': 'error', 'message': 'النص فارغ'}
            
        try:
            if self.engine:
                voices = self.engine.getProperty('voices')
                selected_voice = None
                if language in ['ar', 'ar-SA', 'ar-SA-female']:
                    # البحث عن صوت عربي
                    for voice in voices:
                        if 'arabic' in voice.name.lower() or 'ar' in voice.id.lower():
                            selected_voice = voice.id
                            break
                    if not selected_voice:
                        return {'status': 'error', 'message': 'لا يوجد صوت عربي مثبت في النظام. الرجاء تثبيت صوت عربي في إعدادات النظام.'}
                else:
                    # البحث عن صوت إنجليزي
                    for voice in voices:
                        if 'english' in voice.name.lower() or 'en' in voice.id.lower():
                            selected_voice = voice.id
                            break
                    if not selected_voice:
                        return {'status': 'error', 'message': 'No English voice found on system.'}
                try:
                    self.engine.setProperty('voice', selected_voice)
                except Exception:
                    pass
                self.engine.say(text)
                self.engine.runAndWait()
                return {'status': 'success', 'message': 'تم تحويل النص إلى كلام'}
            else:
                return {'status': 'error', 'message': 'المحرك غير مهيأ'}
        except Exception as e:
            return {'status': 'error', 'message': f'خطأ في تحويل النص: {str(e)}'}
    
    def speak_text_async(self, text, language='en'):
        """تحويل النص إلى كلام بشكل غير متزامن"""
        if not text:
            return {'status': 'error', 'message': 'النص فارغ'}
            
        try:
            if self.engine:
                self.is_speaking = True
                self.thread = threading.Thread(
                    target=self._speak_text_thread,
                    args=(text, language)
                )
                self.thread.daemon = True
                self.thread.start()
                return {'status': 'success', 'message': 'تم بدء تحويل النص إلى كلام'}
            else:
                return {'status': 'error', 'message': 'المحرك غير مهيأ'}
        except Exception as e:
            return {'status': 'error', 'message': f'خطأ في تحويل النص: {str(e)}'}
    
    def _speak_text_thread(self, text, language):
        """تشغيل الكلام في thread منفصل"""
        try:
            voices = self.engine.getProperty('voices')
            selected_voice = None
            if language in ['ar', 'ar-SA', 'ar-SA-female']:
                for voice in voices:
                    if 'arabic' in voice.name.lower() or 'ar' in voice.id.lower():
                        selected_voice = voice.id
                        break
                if not selected_voice:
                    print("لا يوجد صوت عربي مثبت في النظام. الرجاء تثبيت صوت عربي في إعدادات النظام.")
                    self.is_speaking = False
                    return
            else:
                for voice in voices:
                    if 'english' in voice.name.lower() or 'en' in voice.id.lower():
                        selected_voice = voice.id
                        break
                if not selected_voice:
                    print("No English voice found on system.")
                    self.is_speaking = False
                    return
            try:
                self.engine.setProperty('voice', selected_voice)
            except Exception:
                pass
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"خطأ في تحويل النص: {e}")
        finally:
            self.is_speaking = False
    
    def is_speaking_now(self):
        """فحص إذا كان المحرك يتكلم حالياً"""
        return {'status': 'success', 'speaking': self.is_speaking}

# إنشاء instance عام للاستخدام
tts_converter = TextToSpeechConverter()

def start_text_to_speech():
    """دالة لبدء تحويل النص إلى كلام"""
    return tts_converter.start_text_to_speech()

def stop_text_to_speech():
    """دالة لإيقاف تحويل النص إلى كلام"""
    return tts_converter.stop_text_to_speech()

def speak_text(text, language='ar'):
    """دالة لتحويل النص إلى كلام"""
    return tts_converter.speak_text(text, language)

def speak_text_async(text, language='ar'):
    """دالة لتحويل النص إلى كلام بشكل غير متزامن"""
    return tts_converter.speak_text_async(text, language)

def is_speaking_now():
    """دالة لفحص إذا كان المحرك يتكلم حالياً"""
    return tts_converter.is_speaking_now()



