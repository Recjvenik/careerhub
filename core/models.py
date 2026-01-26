from django.db import models

class State(models.Model):
    name = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return self.name

class CityState(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='city_states')
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='city_states')

    class Meta:
        unique_together = ['city', 'state']

    def __str__(self):
        return f"{self.city.name} - {self.state.name}"

class College(models.Model):
    name = models.CharField(max_length=500,default=None, db_index=True)
    short_name = models.CharField(max_length=255,default=None)

    def __str__(self):
        return self.name

class Branch(models.Model):
    name = models.CharField(max_length=255,default=None, db_index=True)
    short_name = models.CharField(max_length=255,default=None)

    def __str__(self):
        return self.name

class Degree(models.Model):
    CATEGORY_CHOICES = [
        ('Arts & Humanities', 'Arts & Humanities'),
        ('Commerce & Management', 'Commerce & Management'),
        ('Science', 'Science'),
        ('Engineering & Technology', 'Engineering & Technology'),
        ('Computer & IT', 'Computer & IT'),
        ('Education', 'Education'),
        ('Law', 'Law'),
        ('Medical & Health Sciences', 'Medical & Health Sciences'),
        ('Pharmacy', 'Pharmacy'),
        ('Design & Architecture', 'Design & Architecture'),
        ('Journalism & Media', 'Journalism & Media'),
        ('Social Work', 'Social Work'),
        ('Agriculture & Allied Sciences', 'Agriculture & Allied Sciences'),
        ('Vocational & Diploma', 'Vocational & Diploma'),
        ('Research & Doctorate', 'Research & Doctorate'),
    ]

    name = models.CharField(max_length=100, db_index=True)
    full_name = models.CharField(max_length=255, db_index=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    is_tech = models.BooleanField(default=False)