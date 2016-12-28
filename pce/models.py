from django.db import models


class Department(models.Model):
    """Represents a department, i.e. COS, CBE, EGR."""
    dept = models.CharField(max_length=5)
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return u"%s" % (self.dept)

    class Meta:
        app_label = 'pce'


class Professor(models.Model):
    """
    Represents a professor. A professor can belong to
    many departments.
    """
    firstname = models.CharField(max_length=40)
    lastname = models.CharField(max_length=40)
    netid = models.CharField(max_length=40)
    depts = models.ManyToManyField(Department)

    def __unicode__(self):
        return u"%s %s" % (self.firstname, self.lastname)

    class Meta:
        app_label = 'pce'


class Load(models.Model):
    """Represents the amount of work that a course entails."""
    text = models.TextField(null=True)
    ppw = models.CharField(max_length=15, null=True, blank=True)
    papers = models.IntegerField(max_length=2, null=True, blank=True)

    def __unicode__(self):
        return u"%s" % self.text

    class Meta:
        app_label = 'pce'


class Course(models.Model):
    title = models.CharField(max_length=200)
    regNum = models.IntegerField(max_length=0)  # registar formal course num.
    description = models.TextField()
    profs = models.ManyToManyField(Professor)
    semester = models.CharField(max_length=10)
    year = models.CharField(max_length=15)
    da = models.CharField(max_length=5, null=True, blank=True)
    # Format: 'day, day; time; day; time etc.'
    lectureTime = models.TextField(null=True, blank=True)
    # Format: 'day, day; time; day, day, day; time etc'
    preceptTime = models.TextField(null=True, blank=True)
    pdf = models.NullBooleanField()
    nopdf = models.NullBooleanField()
    load = models.OneToOneField(Load, null=True)

    def __unicode__(self):
        if self.da:
            return u"%s (%s)" % (self.title, self.da)
        else:
            return u"%s" % (self.title)

    class Meta:
        app_label = 'pce'


class CourseNum(models.Model):
    avg = models.CharField(max_length=5, null=True, blank=True)
    bayes = models.FloatField(null=True)
    bestprof = models.ManyToManyField(Professor, null=True, blank=True)
    dept = models.ForeignKey(Department)
    number = models.CharField(max_length=10)  # for cases like CEE 102a
    instance = models.ManyToManyField(Course)

    def __unicode__(self):
        return u"%s %s" % (self.dept.dept, self.number)

    def save(self, *args, **kwargs):
        bps = Professor.objects.filter(coursenum=self)
        for p in bps:
            self.bestprof.remove(p)
        values = []
        value = 0.0
        ps = None
        instances = Course.objects.filter(coursenum=self)
        for i in instances:
            evals = Evaluation.objects.filter(instance=i)
            for e in evals:
                if (("overall quality of the course" in e.questiontext) or (
                        "Overall quality of the writing seminar" in e.questiontext)):
                    if float(e.mean) > value:
                        value = float(e.mean)
                        ps = Professor.objects.filter(course=i)
                    values.append(float(e.mean))
        if ps is not None:
            for p in ps:
                self.bestprof.add(p)
        sumation = 0.0
        if len(values) is not 0:
            for v in values:
                sumation += v
            self.avg = "{0:.2f}".format(sumation / float(len(values)))
        super(CourseNum, self).save(*args, **kwargs)

    class Meta:
        app_label = 'pce'


class Advice(models.Model):
    instance = models.ForeignKey(Course)
    text = models.TextField()
    length = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        self.length = len(self.text)
        super(Advice, self).save(*args, **kwargs)

    class Meta:
        app_label = 'pce'


class Evaluation(models.Model):
    questiontext = models.TextField()
    num_responses = models.IntegerField(default=0)
    rate_responses = models.CharField(max_length=5)
    excellent = models.CharField(max_length=5)
    veryGood = models.CharField(max_length=5)
    good = models.CharField(max_length=5)
    fair = models.CharField(max_length=5)
    poor = models.CharField(max_length=5)
    na = models.CharField(max_length=5)
    mean = models.DecimalField(max_digits=5, decimal_places=3)
    instance = models.ForeignKey(Course)

    class Meta:
        app_label = 'pce'

    def __unicode__(self):
        return u"Excellent: %s   Very Good: %s   Good: %s   Fair: %s   Poor: %s   (Response Rate/Number of respondees: %s / %s)" % (
            self.excellent, self.veryGood, self.good, self.fair, self.poor, self.rate_responses, self.num_responses)


class User(models.Model):
    netid = models.CharField(max_length=40)

    def __unicode__(self):
        return u"%s" % (self.netid)

    class Meta:
        app_label = 'pce'


class Favorite(models.Model):
    user = models.ForeignKey(User)
    course = models.ForeignKey(Course)

    class Meta:
        app_label = 'pce'
