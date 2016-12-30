from django.contrib import admin

from models import Term
from models import Subject
from models import Course
from models import CourseNumber
from models import Instructor
from models import Offering
from models import Section
from models import Evaluation
from models import Advice
from models import User

# Register your models here.
admin.site.register(Term)
admin.site.register(Subject)
admin.site.register(Course)
admin.site.register(CourseNumber)
admin.site.register(Instructor)
admin.site.register(Offering)
admin.site.register(Section)
admin.site.register(Evaluation)
admin.site.register(Advice)
admin.site.register(User)
