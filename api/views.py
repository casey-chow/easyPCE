from django.shortcuts import render
from rest_framework import generics, viewsets

import models
import serializers


class TermViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.Term.objects.all()
    serializer_class = serializers.TermSerializer
    lookup_field = 'code'


class SubjectViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.Subject.objects.all()
    serializer_class = serializers.SubjectSerializer
    lookup_field = 'code'


class CourseViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseSerializer
    lookup_field = 'course_id' # TODO: figure out how to require term AND course id

