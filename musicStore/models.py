from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q

from sheet_music_africa.storage_backends import PublicMediaStorage, PrivateMediaStorage

from .sendEmail import sendSongPercentageIncreaseEmail


class Genre(models.Model):
    name = models.CharField(max_length=50)
    background_image = models.FileField(null=True, blank=True)
    is_instrument = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class SheetMusic(models.Model):
    # model for uploaded songs
    name = models.CharField(max_length=50)
    discription = models.TextField(default="")
    genre = models.ManyToManyField(Genre)
    rating = models.PositiveIntegerField(default=0)
    composer = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    # schange to a choice select whenever possible
    skill_level = models.CharField(max_length=15, default="Beginner")
    video_link = models.TextField(default="")
    thumbnail = models.FileField(null=True, blank=True)
    demo = models.FileField(null=True, blank=True)  # demo pdf for display
    audio = models.FileField(null=True, blank=True)
    star = models.PositiveIntegerField(default=1)
    point = models.PositiveBigIntegerField(default=1)
    percentage = models.PositiveIntegerField(default=65)
    deleted = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    tags = models.TextField(blank=True,default="")

    class Meta:
        ordering = ['-rejected','verified']

    def __str__(self):
        return self.name

    def updateRating(self):
        star_landmark = {
            1:0,
            2:1,
            3:2,
            4:4,
            5:8
        }

        all_review = My_review.objects.filter(sheet=self)
        review_count = all_review.count()
        if review_count == 0:
            review_count = 1

        max_rate = review_count * 5
        rate = sum([i.rating for i in all_review])

        print("my stat ", max_rate, " ", rate)
        avg = (rate * 100)//max_rate

        print("my avg ", avg)

        if 0 < avg <= 20:
            star = 1
        elif 21 < avg <= 40:
            star = 2
        elif 41 < avg <= 60:
            star = 3
        elif 61 < avg <= 80:
            star = 4
        else:
            star = 5


        self.star = star
        
        if review_count > 10:
            self.point = review_count * star_landmark[star]

        self.rating = review_count
        self.save()

        # self.star = sum([i.rating for i in all_review])//all_review.count()
        # self.rating = all_review.count()
        # self.save()

    def update_score(self, score_list):
        all_song_score = Score.objects.filter(
            main_song=self).exclude(id__in=score_list)

        if all_song_score.count() > 0:
            for score in all_song_score:
                score_sale = Score_sale.objects.filter(
                    Q(score=score) & Q(purchased=True))
                if score_sale.count() > 0:
                    # hide score
                    score.deleted = True
                    score.save()
                else:
                    score.sheet.delete()
                    score.delete()

    def update_percentage(self):
        # update song sales percentage here
        song_score = Score.objects.filter(main_song=self)
        score_sale_count = Score_sale.objects.filter(
            Q(score__in=song_score)
            & Q(purchased=True)
        ).count()

        if 500 < score_sale_count > 101:
            percentage = 70
        elif 1500 < score_sale_count > 501:
            percentage = 75
        elif score_sale_count > 1501:
            percentage = 80
        else:
            percentage = 65

        if(self.percentage != percentage):
            self.percentage = percentage
            self.save()

            # send notification email here
            sendSongPercentageIncreaseEmail(self, percentage, score_sale_count)


class Score(models.Model):
    main_song = models.ForeignKey(SheetMusic, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sheet = models.FileField(null=True, blank=True,
                             storage=PrivateMediaStorage())
    deleted = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)

    def __str__(self):
        return "%s - %s" % (self.main_song.name, self.name)


class My_review(models.Model):
    sheet = models.ForeignKey(SheetMusic, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    rating = models.PositiveIntegerField(default=1)

    def __str_(self):
        return self.composer.first_name + " " + self.composer.last_name + " " + self.rating


class Score_sale(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.ForeignKey(Score, on_delete=models.CASCADE)
    date_added_to_cart = models.DateTimeField(default=timezone.now)
    downloadable = models.BooleanField(default=False)
    purchased = models.BooleanField(default=False)
    date_purchased = models.DateField(null=True, blank=True)
    """ we are storing price again although we can get it from score object,
        because the composer might change the score price in the future
        and we want the purchased price to read the actual price the user
        bought the score.
     """
    purchased_percentage = models.PositiveIntegerField(default=65)
    purchased_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    seller_revenue = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.user.username + " " + self.score.main_song.name + "-"+self.score.name
