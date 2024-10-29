from django.db import models

class Items(models.Model):
    id_wb = models.CharField(max_length=30)
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    rating = models.FloatField()
    feedbacks = models.IntegerField()
    volume = models.IntegerField()
    time_create = models.DateTimeField(auto_now_add=True)
