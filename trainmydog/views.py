# trainmydog/views.py
# from django.shortcuts import render
# ถ้าจะใช้คอร์สจริงในภายหลัง ค่อยเปิด import เหล่านี้
# from .models import Course
# from base.models import Profile

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST

from .models import TrainerApplication, TrainerCertificate
from .forms import (
    TrainerApplicationForm
)


def home_view(request):
    """
    หน้าแรก (Landing/Home) — ตอนนี้ยังไม่ดึงคอร์สจริง
    ถ้าพร้อมแล้วค่อยเอา query ส่วนล่างออกจากคอมเมนต์
    """
    # TODO: เปิดใช้เมื่อทำโมเดลและข้อมูลคอร์สเรียบร้อย
    # courses = (
    #     Course.objects
    #     .filter(
    #         is_published=True,
    #         trainer__profile__role=Profile.Role.TRAINER
    #     )
    #     .select_related('trainer', 'trainer__profile')
    #     .order_by('-created_at')
    # )

    courses = []  # ชั่วคราว: ให้หน้าแสดง layout ได้โดยไม่ error

    return render(request, 'home.html', {'courses': courses})



@login_required
def apply_trainer_view(request):
    latest = TrainerApplication.objects.filter(user=request.user).order_by('-created_at').first()
    block_resubmit = False
    block_message = None

    if latest:
        if latest.status == TrainerApplication.Status.PENDING:
            block_resubmit = True
            block_message = "คุณมีคำร้องที่รอดำเนินการอยู่ จึงไม่สามารถส่งคำร้องอีกได้"
        elif latest.status == TrainerApplication.Status.APPROVED:
            block_resubmit = True
            block_message = "คุณได้รับการอนุมัติแล้ว ไม่สามารถส่งคำร้องใหม่ได้"

    if request.method == 'POST':
        if block_resubmit:
            messages.warning(request, block_message)
            return redirect('trainmydog:home')

        form = TrainerApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            app = form.save(commit=False)
            app.user = request.user
            app.email_snapshot = form.cleaned_data.get("email_snapshot") or request.user.email
            app.save()

            cert_file = form.cleaned_data.get("certificate")
            if cert_file:
                TrainerCertificate.objects.create(application=app, file=cert_file)

            messages.success(request, "ส่งคำขอเรียบร้อย รอแอดมินตรวจสอบ")
            return redirect('trainmydog:home')
        else:
            messages.error(request, "กรุณาตรวจสอบข้อมูลที่กรอก")
    else:
        initial = {
            "full_name": f"{request.user.first_name} {request.user.last_name}".strip(),
            "email_snapshot": request.user.email,
        }
        prof = getattr(request.user, "profile", None)
        if prof and prof.phone:
            initial["phone"] = prof.phone
        form = TrainerApplicationForm(initial=initial)

    return render(request, 'apply_trainer.html', {
        'form': form,
        'latest': latest,
        'block_resubmit': block_resubmit,
        'block_message': block_message,
    })
