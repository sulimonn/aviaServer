from django.db import models


# Create your models here
class Kind_of_activity(models.Model):
    name=models.CharField(max_length=64,unique=True)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Kind of activity'
        
        
class Companies(models.Model):
    name = models.CharField(max_length=64,unique=True)
    number = models.IntegerField()
    code =  models.CharField(max_length=6,unique=True)
    validity = models.DateField()
    status = models.BooleanField(default=True)
    address = models.CharField(max_length=256,unique=True)
    first_phone = models.CharField(max_length=20,unique=True,default="SOME NUMBER")
    second_phone = models.CharField(max_length=20, unique=True,default="SOME NUMBER")
    email = models.CharField(max_length=64,unique=True)
    kind_of_activity = models.ForeignKey(Kind_of_activity,on_delete=models.CASCADE)
    def __str__(self):
        return self.name
