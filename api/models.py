"""
Models for the easyPCE API. The terminology used here closely
maps to the OIT WebFeeds API.
"""
from __future__ import unicode_literals
import re
from django.utils.timezone import now

from django.db import models
from django.core.validators import RegexValidator
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator


class Term(models.Model):

    """
    Represents a term, such as 2016 Fall. A term has many
    courses.
    """

    # Suffix code, ex. F2016 or SU2015
    suffix = models.CharField(
        max_length=6,  # longest code available is SU####
        primary_key=True,
        validators=[RegexValidator(
            regex=r'^(?:S|SU|F)\d{4}$',
            message='suffix is invalid',
        )],
    )

    # Pretty name
    name = models.CharField(
        max_length=11,  # longest name is 'Summer ####'
        validators=[RegexValidator(
            regex=r'^(?:Fall|Spring|Summer) \d{4}$',
            message='invalid term name',
        )],
        unique=True
    )

    # Numeric code used in the registrar
    code = models.PositiveSmallIntegerField(
        unique=True,
        validators=[
            MinValueValidator(1000),
            MaxValueValidator(10000),
        ],
    )

    # Start and end dates
    start_date = models.DateField(
        unique=True,
    )
    end_date = models.DateField(
        unique=True,
    )

    # Season and year of term
    season = models.CharField(
        max_length=2,
        choices=(
            ('S', 'Spring'),
            ('SU', 'Summer'),
            ('F', 'Fall'),
        ),
    )
    year = models.PositiveSmallIntegerField(
        validators=[  # sanity check constraints
            MinValueValidator(2000),
            MaxValueValidator(3000),
        ],
    )

    # Automatically update the season and year upon save
    def save(self):
        season, year = re.match(r'^(S|SU|F)(\d{4})$', self.suffix)
        self.season = season
        self.year = int(year)
        super(Term, self).save()

    def __unicode__(self):
        return unicode(self.name, 'utf-8')


class Subject(models.Model):

    """
    Represents a subject, ex. COS, CBE, EGR. A subject can have
    many Courses.
    """

    # The 3-letter code for the subject
    code = models.CharField(
        max_length=3,
        validators=[RegexValidator(
            regex=r'[A-Z]{3}',
            message='invalid subject code'
        )],
        primary_key=True,
    )

    # The pretty name for the subject
    name = models.CharField(
        max_length=100,
        unique=True
    )

    def __unicode__(self):
        return unicode(self.name)


class Course(models.Model):

    """
    Represents a course, ex. COS 217. Note that this model
    represents a course over all terms, as opposed to an Offering, which
    occurs over one term.
    """

    # Course ID, as provided by the Registrar
    id = models.PositiveIntegerField(
        primary_key=True,
    )

    # Primary course number
    # put in string because CourseNumber hasn't yet been defined
    # http://stackoverflow.com/a/3682524/237904
    num = models.ForeignKey(
        'CourseNumber',
        related_name='+',  # don't create a back-reference
    )


class CourseNumber(models.Model):

    """
    Represents the actual catalog number of a course. This is a many-to-many
    relationship because of the existence of cross-listings.
    """

    course = models.ForeignKey(
        Course,
        # must be allowed to be blank so that circular creation
        # doesn't occur
        null=True,
        blank=True,
    )
    subject = models.ForeignKey(Subject)
    num = models.CharField(
        max_length=5,
    )

    def __unicode__(self):
        return u'%s %s' % (self.subject.code, self.num)


class Instructor(models.Model):

    """
    Represents an instructor.
    """

    # First and last name
    first_name = models.CharField(
        max_length=40
    )
    last_name = models.CharField(
        max_length=40
    )

    # Employee ID, as given in OIT WebFeeds
    id = models.PositiveIntegerField(
        primary_key=True,
    )

    def __unicode__(self):
        return u"%s %s" % (self.first_name, self.last_name)


class Offering(models.Model):

    """
    Represents a course offering, ex. COS 217, Fall 2016. This is as opposed
    to a Course, which represents a course over time.
    """

    # Course Identifiers
    title = models.CharField(
        max_length=150,
    )
    course = models.ForeignKey(Course)
    term = models.ForeignKey(Term)
    course_nums = models.ManyToManyField(CourseNumber)

    # PDF/Audit information
    # None indicates a lack of indication on the PDF status
    pdf = models.NullBooleanField()
    audit = models.NullBooleanField()

    # Distribution Requirement
    dist_req = models.CharField(
        max_length=3,
        choices=(
            ('EC', 'Epistemology and Cognition'),
            ('EM', 'Ethical Thought and Moral Values'),
            ('HA', 'Historical Analysis'),
            ('LA', 'Literature and the Arts'),
            ('QR', 'Quantitative Reasoning'),
            ('SA', 'Social Analysis'),
            ('STL', 'Science and Technology with Lab'),
            ('STN', 'Science and Technology, no Lab'),
        ),
    )

    # Official description
    description = models.TextField(
        blank=True,
    )
    # Other information included in the registrar
    additional_info = models.TextField(
        blank=True,
    )
    # Instructors
    instructors = models.ManyToManyField(Instructor)

    # Timestamp, for scraping
    last_updated = models.DateTimeField(
        default=now,
    )

    def __unicode__(self):
        return unicode(title)


class Section(models.Model):

    """
    Represents a class section, such as a seminar or lecture.
    """

    # Class number used to enroll
    id = models.PositiveIntegerField(
        primary_key=True
    )

    # Name, ex. S01, B03
    name = models.CharField(
        max_length=3,
        validators=[RegexValidator(
            regex=r'^[A-Z]\d\d$',
            message='section name is invalid',
        )],
    )

    # Type, ex. lecture, lab, etc.
    type = models.CharField(
        max_length=10,  # 'Seminar' is 7 chars
    )

    # Status
    status = models.CharField(
        max_length=1,
        choices=(
            ('O', 'Open'),
            ('C', 'Closed'),
            ('X', 'Canceled'),
        )
    )

    # Times and Dates
    # We store the days the class meets as a comma-separated list,
    # with a comma after every day, including the last one. The
    # following code is used: M T W Th F
    start_time = models.TimeField()
    end_time = models.TimeField()
    days = models.CharField(
        max_length=13,
        validators=[RegexValidator(
            regex=r'^M?T?W?(?:Th)?F?$',
            message='meeting days string is invalid',
        )],
    )

    # Enrollment and Capacity
    enrollment = models.PositiveIntegerField()
    capacity = models.PositiveIntegerField()

    # Meeting Location
    # Format should be [Building] [Room #]
    location = models.CharField(
        max_length=100,
    )


class Evaluation(models.Model):

    """
    Represents an evaluation metric given to a course offering.
    """

    course = models.ForeignKey(Offering)

    question_text = models.CharField(
        max_length=100,
    )
    response_avg = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[
            MaxValueValidator(5.0),
            MinValueValidator(0.0),
        ],
    )

    def __unicode__(self):
        return u'%s: %.2f' % (self.question_text, self.response_avg)


class Advice(models.Model):

    """
    Represents advice given to future students by people who had
    already taken a given course.
    """

    offering = models.ForeignKey(Offering)
    text = models.TextField()


class User(models.Model):

    """
    Custom user profile.
    """

    netid = models.CharField(
        max_length=15,
        primary_key=True,
    )

    def __unicode__(self):
        return unicode(self.netid)
