from django.db import models
from accounts.models import Account
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


class Seat(models.Model):
    seat_number = models.IntegerField()
    is_booked = models.BooleanField(default=False)
    row = models.CharField(max_length=2)
    section = models.CharField(max_length=50)
    hall = models.ForeignKey(Hall,on_delete=models.CASCADE)
    show = models.ForeignKey(Show,on_delete=models.CASCADE,related_name="seats",null=True)
    price = models.DecimalField(max_digits=10,decimal_places=2,default=300.00)
    user = models.ForeignKey(Account,on_delete=models.SET_NULL,null=True,blank=True)
    def __str__(self):
        return f"{self.row}-{self.seat_number}"