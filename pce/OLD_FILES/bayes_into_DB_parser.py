import operator
import sys
sys.path.append('/srv/www/easypce/')
from easypce import settings
from django.core.management import setup_environ
setup_environ(settings)
from models import *

FILE_NAME = 'ratings_final'


def insertBayes():
    f = open(FILE_NAME)
    for l in f:
        fields = l.replace(':', '').split()
        try:
            d = Department.objects.get(dept=fields[0])
            cn = CourseNum.objects.get(dept=d, number=fields[1])
            print l
            print cn
            cn.bayes = float(fields[2])
            cn.save()
        except Department.DoesNotExist:
            print "Dept does not exist"
            continue
        except CourseNum.DoesNotExist:
            print "CourseNum does not exist"
            continue


insertBayes()
