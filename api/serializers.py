"""
Serializers for the easyPCE API.
"""
from rest_framework import serializers

from models import Term
from models import Subject
from models import Course
from models import CourseNumber
from models import Instructor
from models import Section
from models import Evaluation
from models import Advice
from models import User


class TermSerializer(serializers.Serializer):
    class Meta:
        model = Term
        fields = ('suffix', 'name', 'code', 'start_date',
                  'end_date', 'season', 'year')
