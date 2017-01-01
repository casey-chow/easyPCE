"""
Models for the easyPCE API. The terminology used here closely
maps to the OIT WebFeeds API.

Design Decisions:
- The format of these values may change erratically, so we use surrogate keys
  instead of natural keys for the primary key, even when provided.
- We use UUID primary keys because they deal with concurrent inserts a lot
  better than sequentials.
"""
from __future__ import unicode_literals
import re
import uuid
from django.utils.timezone import now

from django.db import models
from django.core.validators import RegexValidator
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from extended_choices import Choices


class UUIDModel(models.Model):
    """
    This abstract model automatically uses UUID fields for the models instead
    of auto-incrementing integers.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    class Meta:
        abstract = True


class Term(UUIDModel):

    """
    Represents a term, such as 2016 Fall. A term has many
    courses.
    """

    # Suffix code, ex. F2016 or SU2015
    suffix = models.CharField(
        max_length=6,  # longest code available is SU####
        validators=[RegexValidator(
            regex=r'^(?:S|SU|F)\d{4}$',
            message='suffix is invalid',
        )],
        unique=True,
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
        validators=[
            MinValueValidator(1000),
            MaxValueValidator(10000),
        ],
        unique=True,
    )

    # Start and end dates
    start_date = models.DateField(
        unique=True,
    )
    end_date = models.DateField(
        unique=True,
    )

    # Season and year of term
    SEASONS = Choices(
        ('S', 'S', 'Spring'),
        ('SU', 'SU', 'Summer'),
        ('F', 'F', 'Fall'),
    )
    season = models.CharField(
        max_length=2,
        choices=SEASONS,
    )
    year = models.PositiveSmallIntegerField(
        validators=[  # sanity check constraints
            MinValueValidator(2000),
            MaxValueValidator(3000),
        ],
    )

    # Automatically update the season and year upon save
    def save(self, *args, **kwargs):
        season, year = re.match(r'^(S|SU|F)(\d{4})$', self.suffix).groups()
        self.season = season
        self.year = int(year)
        super(Term, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name.decode('utf-8')


class Subject(UUIDModel):

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
        unique=True,
    )

    # The pretty name for the subject
    name = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
    )

    def __unicode__(self):
        return self.name.decode('utf-8')


class Course(UUIDModel):

    """
    Represents a course, ex. COS 217. Note that this model represents a
    course over all terms, as opposed to an Offering, which occurs over
    one term.
    """

    # Course ID, as provided by the Registrar
    course_id = models.CharField(
        max_length=10,
        unique=True,
    )

    def __unicode__(self):
        return unicode(self.course_id)


class CourseNumber(UUIDModel):

    """
    Represents the actual catalog number of a course. This is a many-to-many
    relationship because of the existence of cross-listings.
    """

    offering = models.ForeignKey(
        'Offering',
        null=True,
        blank=True,
        related_name='cross_listings',  # anything not the primary # is a xlist
        on_delete=models.CASCADE,  # delete if course deleted
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,  # delete if subject deleted
        related_name='course_numbers',
    )
    # the number itself, including suffixes, ex. 201C
    number = models.CharField(
        max_length=5,
    )

    def __unicode__(self):
        return u'%s %s' % (self.subject.code, self.number)


class Instructor(UUIDModel):

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
    emplid = models.CharField(
        max_length=15,
        unique=True,
    )

    def __unicode__(self):
        return u"%s %s" % (self.first_name, self.last_name)


class Offering(UUIDModel):

    """
    Represents a course offering, ex. COS 217, Fall 2016. This is as opposed
    to a Course, which represents a course over time.

    Yes, I know it gets confusing. Sorry, but there's really no other way to
    distinguish across terms. So ask yourself this rule of thumb when trying
    to choose between a Course and an Offering: does this apply to _every_
    term? Or can it change between terms?
    """

    # Course Identifiers
    guid = models.IntegerField()
    title = models.CharField(
        max_length=150,
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='offerings',
    )
    term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
        related_name='offerings',
    )

    # Primary course number (not cross-listings)
    primary_number = models.ForeignKey(
        CourseNumber,
        on_delete=models.CASCADE,  # delete model if primary number gone
        related_name='+',  # don't create a back-reference
    )

    # PDF/Audit information
    # None indicates a lack of indication on the PDF status
    pdf = models.NullBooleanField()
    pdf_only = models.BooleanField(
        default=False,
    )
    audit = models.NullBooleanField()

    # Distribution Requirement
    # http://www.b-list.org/weblog/2007/nov/02/handle-choices-right-way/
    DIST_REQ = Choices(
        ('EC', 'EC', 'Epistemology and Cognition'),
        ('EM', 'EM', 'Ethical Thought and Moral Values'),
        ('HA', 'HA', 'Historical Analysis'),
        ('LA', 'LA', 'Literature and the Arts'),
        ('QR', 'QR', 'Quantitative Reasoning'),
        ('SA', 'SA', 'Social Analysis'),
        ('STL', 'STL', 'Science and Technology with Lab'),
        ('STN', 'STN', 'Science and Technology, no Lab'),
    )
    dist_req = models.CharField(
        max_length=3,
        choices=DIST_REQ,
        blank=True,
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
        return u'%s (%s)' % (self.title, self.term)


class Section(UUIDModel):

    """
    Represents a class section, such as a seminar or lecture.
    """

    # Class number used to enroll
    class_id = models.CharField(
        max_length=15,
        unique=True,
    )

    # Parent offering
    offering = models.ForeignKey(
        Offering,
        on_delete=models.CASCADE,
        related_name='sections',
    )

    # Name, ex. S01, B03, P01A
    name = models.CharField(
        max_length=5,
        validators=[RegexValidator(
            regex=r'^[A-Z]\d\d[A-Z]?$',
            message='section name is invalid',
        )],
    )

    # Type, ex. lecture, lab, etc.
    # https://github.com/PrincetonUSG/recal/blob/master/course_selection/models.py#L93
    TYPE_CODES = Choices(
        ('CLASS', 'C', 'Class'),
        ('DRILL', 'D', 'Drill'),
        ('EAR_TRAINING', 'E', 'Ear training'),
        ('FILM', 'F', 'Film'),
        ('LAB', 'B', 'Lab'),
        ('LECTURE', 'L', 'Lecture'),
        ('PRECEPT', 'P', 'Precept'),
        ('SEMINAR', 'S', 'Seminar'),
        ('STUDIO', 'U', 'Studio'),
    )
    type_code = models.CharField(
        max_length=1,
        choices=TYPE_CODES,
    )

    @property
    def type(self):
        return TYPE_CODES.for_value(self.type_code).display

    @type.setter
    def set_type(self):
        self.type_code = TYPE_CODES.for_display(val).value

    # Status
    STATUS_CODES = Choices(
        ('OPEN', 'O', 'Open'),
        ('CLOSED', 'C', 'Closed'),
        ('CANCELLED', 'X', 'Cancelled'),
    )
    status_code = models.CharField(
        max_length=1,
        choices=STATUS_CODES,
    )

    @property
    def status(self):
        return STATUS_CODES.for_value(self.status_code).display

    @status.setter
    def set_status(self, val):
        self.status_code = STATUS_CODES.for_display(val).value

    # Enrollment and Capacity
    enrollment = models.PositiveSmallIntegerField()
    capacity = models.PositiveSmallIntegerField()

    def __unicode__(self):
        return self.name.decode('utf-8')


class Meeting(UUIDModel):

    """
    Represents a class meeting, within a section.
    Why is this necesary, you ask? Because of this shit:
    https://registrar.princeton.edu/course-offerings/
    course_details.xml?courseid=010006&term=1172
    Seriously, Princeton? Get your shit together yo. I
    had to refactor my models because of your shit.
    """
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='meetings',
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

    # Meeting Location
    # Format should be [Building] [Room #]
    location = models.CharField(
        max_length=100,
        blank=True,
    )

    def __unicode__(self):
        return u'%s %s %s at %s' % (self.days, self.start_time,
                                    self.end_time, self.location)


class Evaluation(UUIDModel):

    """
    Represents an evaluation metric given to a course offering.
    """

    offering = models.ForeignKey(
        Offering,
        on_delete=models.CASCADE,
        related_name='evaluations',
    )

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


class Advice(UUIDModel):

    """
    Represents advice given to future students by people who had
    already taken a given course.
    """

    offering = models.ForeignKey(
        Offering,
        on_delete=models.CASCADE,
        related_name='advice',
    )
    text = models.TextField()


class User(UUIDModel):

    """
    Custom user profile.
    """

    netid = models.CharField(
        max_length=15,
    )

    def __unicode__(self):
        return self.netid.decode('utf-8')
