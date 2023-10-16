from django.db import models


# Create your models here
class Kind_of_activity(models.Model):
    name=models.CharField(max_length=64,unique=True)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Kind of activity'
        
        
class Companies(models.Model):
    image = models.ImageField(upload_to='logo', blank=True)
    name = models.CharField(max_length=64,unique=True)
    number = models.IntegerField()
    code = models.CharField(max_length=6,unique=True)
    date = models.DateField(auto_now_add=True)
    status = models.BooleanField(default=True)
    email = models.CharField(max_length=64,unique=True)
    phone1 = models.CharField(max_length=20,unique=True)
    phone2 = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=256,unique=True)
    kind_of_activity = models.ForeignKey(Kind_of_activity,on_delete=models.CASCADE)

    def __str__(self):
        return self.name