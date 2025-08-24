from django.db import models
from django.utils.text import slugify


# Create your models here.

class Hall(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    column = models.IntegerField()

    def __str__(self):
        return self.name

class Show(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True,blank=True)
    image = models.ImageField(upload_to="images/",null=True)
    description = models.TextField(null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    hall = models.ForeignKey(Hall,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.start_time}"
    
    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug=slugify(self.name)
        super().save(*args,**kwargs)