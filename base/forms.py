from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import transaction
from .models import Profile


# -----------------------------
# 🔹 ฟอร์มสมัครสมาชิก
# -----------------------------
class RegisterForm(UserCreationForm):
    first_name = forms.CharField(label='ชื่อ', max_length=30, required=True)
    last_name  = forms.CharField(label='นามสกุล', max_length=150, required=True)
    email      = forms.EmailField(label='อีเมล', required=True)

    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base = "w-full border border-slate-300 rounded-lg bg-white px-3 py-2.5"
        self.fields['first_name'].widget.attrs.update({'class': base, 'placeholder': 'ชื่อ'})
        self.fields['last_name'].widget.attrs.update({'class': base, 'placeholder': 'นามสกุล'})
        self.fields['email'].widget.attrs.update({'class': base, 'placeholder': 'name@example.com'})
        self.fields['password1'].widget.attrs.update({'class': base, 'placeholder': 'อย่างน้อย 8 ตัวอักษร'})
        self.fields['password2'].widget.attrs.update({'class': base, 'placeholder': 'ยืนยันรหัสผ่านอีกครั้ง'})

    def clean_email(self):
        email = (self.cleaned_data['email'] or '').lower()
        # ป้องกันเคสซ้ำ เช่น USER@GMAIL กับ user@gmail
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('อีเมลนี้ถูกใช้แล้ว')
        return email

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data['email'].lower()
        user.username = email
        user.email = email
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # สร้างโปรไฟล์เริ่มต้นอัตโนมัติ
            Profile.objects.get_or_create(user=user, defaults={'role': Profile.Role.MEMBER})
        return user


# -----------------------------
# 🔹 ฟอร์มเข้าสู่ระบบ
# -----------------------------
class EmailAuthForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields['username'].label = 'อีเมล'
        self.fields['username'].widget = forms.EmailInput(
            attrs={
                'placeholder': 'กรอกอีเมล',
                'class': 'w-full border border-slate-300 rounded-lg bg-white px-3 py-2.5'
            }
        )
        self.fields['password'].label = 'รหัสผ่าน'
        self.fields['password'].widget.attrs.update({
            'placeholder': 'กรอกรหัสผ่าน',
            'class': 'w-full border border-slate-300 rounded-lg bg-white px-3 py-2.5 pr-10'
        })


# -----------------------------
# 🔹 ฟอร์มอัปเดตข้อมูลผู้ใช้
# -----------------------------
class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(label='ชื่อ', max_length=30, required=False)
    last_name  = forms.CharField(label='นามสกุล', max_length=150, required=False)
    email      = forms.EmailField(label='อีเมล', required=True)

    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['email'].disabled = True
        self.fields['email'].widget.attrs.update({
            'class': 'w-full rounded-xl border border-slate-200 bg-slate-100 text-slate-500 cursor-not-allowed',
            'title': 'อีเมลไม่สามารถเปลี่ยนได้',
            'tabindex': '-1',
            'aria-disabled': 'true',
        })

    def clean_email(self):
        return (self.instance.email or '').lower()

    def save(self, commit=True):
        obj = super().save(commit=False)
        current = (self.instance.email or '').lower()
        obj.email = current
        obj.username = current
        if commit:
            obj.save()
        return obj


# -----------------------------
# 🔹 ฟอร์มอัปเดตโปรไฟล์ (Profile Model)
# -----------------------------
class ProfileUpdateForm(forms.ModelForm):
    phone  = forms.CharField(label='เบอร์โทร', max_length=20, required=False)
    avatar = forms.ImageField(label='รูปโปรไฟล์', required=False)

    class Meta:
        model  = Profile
        fields = ['phone', 'avatar', 'bio']
        labels = {'bio': 'คำอธิบายสั้น ๆ'}
        widgets = {'bio': forms.Textarea(attrs={'rows': 3, 'class': 'w-full border border-slate-300 rounded-lg p-2'})}
