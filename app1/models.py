from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Book(models.Model):
    name = models.CharField(max_length =200)
    author = models.CharField(max_length =200)
    isbn = models.PositiveIntegerField()
    category = models.CharField(max_length=50)

    def __str__(self):
        return self.name + "["+str(self.isbn)+']'

class Contact(models.Model):
    name = models.CharField(max_length = 122)
    email = models.CharField(max_length = 122)
    phone = models.CharField(max_length = 12)
    desc = models.TextField()
    date = models.DateField()

    def __str__(self):
        return self.name

class Student(models.Model):
    user = models.OneToOneField(User,on_delete=models. CASCADE)
    grade = models.CharField(max_length=10)
    branch = models.CharField(max_length=10,blank=True)
    roll_no = models.CharField(max_length=3,blank=True)
    phone = models.CharField(max_length=10,blank=True)

    def __str__(self):
        return str(self.user) + " ["+str(self.branch)+']'+ " ["+str(self.classroom)+']' + " ["+str(self.roll_no)+']'