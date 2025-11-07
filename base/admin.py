from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile


# เพิ่มแท็บ Profile ให้แสดงในหน้า User ของ admin
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    extra = 0


# แก้ไขหน้า User ใน admin ให้มีข้อมูล Profile แสดงร่วมด้วย
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'get_role',
        'is_staff', 'is_active'
    )
    list_select_related = ('profile',)

    def get_role(self, obj):
        # แสดงบทบาทของผู้ใช้ตาม Profile
        if obj.is_superuser or obj.is_staff:
            return "แอดมิน"
        prof = getattr(obj, "profile", None)
        return prof.get_role_display() if prof else "-"
    get_role.short_description = "Role"


# ลงทะเบียน User ใหม่ให้ใช้ CustomUserAdmin
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, CustomUserAdmin)

