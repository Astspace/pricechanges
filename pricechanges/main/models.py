from django.db import models

class Items(models.Model):
    id_wb = models.IntegerField(blank=True)
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']
        indexes = [
            models.Index(fields=['-id'])
        ]
