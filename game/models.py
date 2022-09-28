from enum import unique
from django.db import models
from django.db.models import Q

from sheet_music_africa.storage_backends import GameMediaStorage


class Competition(models.Model):
    name = models.CharField(max_length=20)
    pass_phrase = models.CharField(max_length=20)
    date_started = models.DateField(null=True,blank=True)
    date_ended = models.DateField(null=True,blank=True)
    location = models.CharField(max_length=200,default="Virtual")
    status = models.CharField(
        max_length=3,
        choices=[("PEN", 'PENDING'),("STA", 'STARTED'),("END", 'ENDED'),
    ],
        default="PEN",
    )

    def __str__(self):
        return f"{self.name} {self.status}"

    def get_number_of_contenders(self):
        return GameProfile.objects.filter(Q(competition=self)&Q(can_compete=True)).count()

    
    def get_leader_board(self):
        return self.gameprofile_set.all().order_by("-score")


class GameProfile(models.Model):    
    full_name = models.CharField(max_length=300)
    nickname = models.CharField(max_length=100,default="",unique=True)
    pic = models.FileField(null=True,blank=True,storage=GameMediaStorage())
    score = models.PositiveBigIntegerField(default=0)
    competition = models.ManyToManyField(Competition,blank=True)    

    class Meta:
        ordering = ['-score']

    def __str__(self):
        return self.full_name




