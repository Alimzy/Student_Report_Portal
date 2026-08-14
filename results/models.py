from django.db import models

from account.models import Staff
from core.models import User


# Create your models here.

class Course(models.Model):
    score = models.PositiveIntegerField(default=0)
    grade = models.CharField(max_length=1, blank=False, null=False)
    grade_points = models.IntegerField(default=0.0, blank=False, null=False)
    is_published = models.BooleanField(default=False)
    uploaded_by = models.ForeignKey(Staff,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.grade} -{self.grade_points} - {self.uploaded_by}"

