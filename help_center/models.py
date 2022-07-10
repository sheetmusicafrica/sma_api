from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50)
    preference = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Post(models.Model):
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    body = models.TextField()
    positive_count = models.PositiveIntegerField(default=0)
    negative_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "%s : %s"%(self.category.name,self.title)

