from django.contrib import admin

from paper.models import AERecommendation, AERecommendationFile, DecisionFile, EICDecision

from .models import Attribute
 

# Register your models here.
admin.site.register(Attribute)

admin.site.register(AERecommendation)

admin.site.register(EICDecision)

admin.site.register(AERecommendationFile)

admin.site.register(DecisionFile)
