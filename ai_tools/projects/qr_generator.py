import qrcode
import io
import base64
import os

class QRGenerator:
    def __init__(self):
        self.qr = None
        
    def generate_qr_code(self, text, size=10, border=4):
        """إنشاء رمز QR"""
        if not text:
            return {'status': 'error', 'message': 'النص فارغ'}
            
        try:
            # إنشاء رمز QR
            self.qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=size,
                border=border,
            )
        
            self.qr.add_data(text)
            self.qr.make(fit=True)
            
            # إنشاء الصورة
            img = self.qr.make_image(fill_color="black", back_color="white")
            
            # تحويل الصورة إلى base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return {
                'status': 'success', 
                'message': 'تم إنشاء رمز QR بنجاح',
                'image': image_base64
            }
            
        except Exception as e:
            return {'status': 'error', 'message': f'خطأ في إنشاء رمز QR: {str(e)}'}
    
    def save_qr_code(self, text, file_path, size=10, border=4):
        """حفظ رمز QR في ملف"""
        if not text:
            return {'status': 'error', 'message': 'النص فارغ'}
            
        try:
            # إنشاء رمز QR
            self.qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=size,
                border=border,
            )
            self.qr.add_data(text)
            self.qr.make(fit=True)
            
            # إنشاء الصورة
            img = self.qr.make_image(fill_color="black", back_color="white")
            
            # حفظ الصورة
            img.save(file_path)
            
            return {
                'status': 'success', 
                'message': f'تم حفظ رمز QR في {file_path}',
                'file_path': file_path
            }
            
        except Exception as e:
            return {'status': 'error', 'message': f'خطأ في حفظ رمز QR: {str(e)}'}
    
    def generate_qr_with_logo(self, text, logo_path=None, size=10, border=4):
        """إنشاء رمز QR مع شعار"""
        if not text:
            return {'status': 'error', 'message': 'النص فارغ'}
            
        try:
            # إنشاء رمز QR
            self.qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=size,
                border=border,
            )
            self.qr.add_data(text)
            self.qr.make(fit=True)
            
            # إنشاء الصورة
            img = self.qr.make_image(fill_color="black", back_color="white")
            
            # إضافة الشعار إذا كان متوفراً
            if logo_path and os.path.exists(logo_path):
                from PIL import Image
                logo = Image.open(logo_path)
                
                # تغيير حجم الشعار
                logo_width, logo_height = logo.size
                qr_width, qr_height = img.size
                
                # حساب الحجم المناسب للشعار
                logo_size = min(qr_width, qr_height) // 4
                logo = logo.resize((logo_size, logo_size))
                
                # وضع الشعار في وسط رمز QR
                logo_pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
                img.paste(logo, logo_pos)
            
            # تحويل الصورة إلى base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return {
                'status': 'success', 
                'message': 'تم إنشاء رمز QR مع الشعار بنجاح',
                'image': image_base64
            }
            
        except Exception as e:
            return {'status': 'error', 'message': f'خطأ في إنشاء رمز QR: {str(e)}'}

# إنشاء instance عام للاستخدام
qr_generator = QRGenerator()

def generate_qr_code(text, size=10, border=4):
    """دالة لإنشاء رمز QR"""
    return qr_generator.generate_qr_code(text, size, border)

def save_qr_code(text, file_path, size=10, border=4):
    """دالة لحفظ رمز QR في ملف"""
    return qr_generator.save_qr_code(text, file_path, size, border)

def generate_qr_with_logo(text, logo_path=None, size=10, border=4):
    """دالة لإنشاء رمز QR مع شعار"""
    return qr_generator.generate_qr_with_logo(text, logo_path, size, border)



