from django.urls import path
from . import views

app_name = 'ai_tools'

urlpatterns = [
    path('', views.home, name='home'),
    path('eye-mouse/', views.eye_mouse, name='eye_mouse'),
    path('hand-mouse/', views.hand_mouse, name='hand_mouse'),
    path('voice-control/', views.voice_control, name='voice_control'),
    path('finger-counter/', views.finger_counter, name='finger_counter'),
    path('virtual-mouse/', views.virtual_mouse, name='virtual_mouse'),
    path('speech-to-text/', views.speech_to_text, name='speech_to_text'),
    path('text-to-speech/', views.text_to_speech, name='text_to_speech'),
    path('object-detection/', views.object_detection, name='object_detection'),
    path('motion-detection/', views.motion_detection, name='motion_detection'),
    path('motion-detection/start/', views.start_motion_detection, name='start_motion_detection'),
    path('motion-detection/stop/', views.stop_motion_detection, name='stop_motion_detection'),
    path('motion-detection/status/', views.motion_status, name='motion_status'),
    path('motion-detection/reset-alerts/', views.reset_alerts, name='reset_alerts'),
    path('qr-generator/', views.qr_generator, name='qr_generator'),
    path('hand-game/', views.hand_game, name='hand_game'),
    path('camera-feed/', views.camera_feed, name='camera_feed'),
]
