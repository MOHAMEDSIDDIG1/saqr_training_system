#!/usr/bin/env python3
"""
فحص جميع المكتبات المطلوبة للتأكد من تثبيتها
"""

import sys

def check_library(library_name, import_name=None):
    """فحص مكتبة واحدة"""
    if import_name is None:
        import_name = library_name
    
    try:
        module = __import__(import_name)
        version = getattr(module, '__version__', 'غير محدد')
        print(f"✅ {library_name}: {version}")
        return True
    except ImportError as e:
        print(f"❌ {library_name}: غير مثبت - {e}")
        return False

def main():
    print("🔍 فحص المكتبات المطلوبة...")
    print("=" * 50)
    
    # قائمة المكتبات المطلوبة
    libraries = [
        ("Django", "django"),
        ("OpenCV", "cv2"),
        ("MediaPipe", "mediapipe"),
        ("PyAutoGUI", "pyautogui"),
        ("NumPy", "numpy"),
        ("SpeechRecognition", "speech_recognition"),
        ("pyttsx3", "pyttsx3"),
        ("QRCode", "qrcode"),
        ("Pillow", "PIL"),
        ("pycaw", "pycaw"),
        ("comtypes", "comtypes"),
        ("arabic-reshaper", "arabic_reshaper"),
        ("python-bidi", "bidi"),
        ("pyperclip", "pyperclip"),
        ("autopy", "autopy"),
    ]
    
    # فحص المكتبات المدمجة
    builtin_libraries = [
        ("winsound", "winsound"),
        ("threading", "threading"),
        ("time", "time"),
        ("math", "math"),
        ("random", "random"),
        ("json", "json"),
        ("io", "io"),
        ("base64", "base64"),
        ("os", "os"),
    ]
    
    missing_libraries = []
    
    print("📦 المكتبات الخارجية:")
    for name, import_name in libraries:
        if not check_library(name, import_name):
            missing_libraries.append(name)
    
    print("\n🔧 المكتبات المدمجة:")
    for name, import_name in builtin_libraries:
        if not check_library(name, import_name):
            missing_libraries.append(name)
    
    print("\n" + "=" * 50)
    if missing_libraries:
        print(f"❌ المكتبات المفقودة: {', '.join(missing_libraries)}")
        print("\n💡 لتثبيت المكتبات المفقودة:")
        print("pip install " + " ".join(missing_libraries))
    else:
        print("✅ جميع المكتبات مثبتة بنجاح!")
    
    print(f"\n🐍 إصدار Python: {sys.version}")
    print(f"📁 مسار Python: {sys.executable}")

if __name__ == "__main__":
    main()



