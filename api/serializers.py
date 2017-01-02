"""
Serializers for the easyPCE API.
"""
from rest_framework import serializers

import models


class TermSerializer(serializers.ModelSerializer):

    courses = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = models.Term
        fields = (
            'suffix',
            'name',
            'code',
            'courses',
            'start_date',
            'end_date',
            'season',
            'year',
        )


class SubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Subject
        fields = '__all__'
        # fields = (
        #     'code',
        #     'name',
        #     'courses',
        # )


class SubjectCodeField(serializers.RelatedField):
    """Represents a subject code, ex. COS, EGR, etc."""

    def to_representation(self, value):
        return value.code


class CourseNumberSerializer(serializers.ModelSerializer):

    course = serializers.PrimaryKeyRelatedField(read_only=True)
    subject = SubjectCodeField(read_only=True)

    class Meta:
        model = models.CourseNumber
        fields = (
            'course',
            'subject',
            'number',
        )


class InstructorSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Instructor
        fields = (
            'first_name',
            'last_name',
        )


class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Course
        fields = (
            'course_id',
            'title',
            'term',
            'primary_number',
            'pdf',
            'pdf_only',
            'audit',
            'dist_req',
            'description',
            'additional_info',
            'instructors',
            'last_updated',
            'sections',
            'evaluations',
            'advice',
        )


class SectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Section
        fields = (
            'class_id',
            'name',
            'type',
            'status',
            'enrollment',
            'capacity',
            'meetings',
        )


class MeetingSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Meeting
        fields = (
            'start_time',
            'end_time',
            'days',
            'location'
        )


class EvaluationSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Evaluation
        fields = (
            'question_text',
            'response_avg',
        )


class AdviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Advice
        fields = (
            'text',
        )


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.User
        fields = (
            'netid',
        )

