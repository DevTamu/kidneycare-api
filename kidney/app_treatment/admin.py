from django.contrib import admin
from .models import (
    AccessType,
    Treatment,
    TreatmentDetail,
    Prescription,
    PreDialysis,
    PostDialysis
)

@admin.register(Treatment)
class AdminTreatment(admin.ModelAdmin):
    pass

@admin.register(Prescription)
class AdminPrescription(admin.ModelAdmin):
    pass

@admin.register(AccessType)
class AdminAccessType(admin.ModelAdmin):
    pass

@admin.register(TreatmentDetail)
class AdminTreatmentDetails(admin.ModelAdmin):
    pass

@admin.register(PreDialysis)
class AdminPredialysis(admin.ModelAdmin):
    pass

@admin.register(PostDialysis)
class AdminPostdialysis(admin.ModelAdmin):
    pass


