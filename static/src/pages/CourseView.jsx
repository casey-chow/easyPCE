import React from 'react';
import { connect } from 'react-redux';
import _ from 'lodash';
import fetchCourses from '../actions/coursesActions';

import CourseSummary from '../components/CourseSummary';

@connect(store => ({
    courses: store.courses.courses,
}))

export default class CourseView extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            data: [],
        };
    }

    componentWillMount() {
        this.props.dispatch(fetchCourses());
    }

    renderEmpty() {
        return (
            <div className="CourseView">
                <h1>Courses</h1>
                No courses found.
            </div>
        );
    }

    renderWithCourses() {
        return (
            <div className="CourseView">
                <h1>Courses</h1>
                {this.props.courses.map(course => (
                    <CourseSummary key={course.course_id} course={course} />
                ))}
            </div>
        );
    }

    render() {
        console.log('rendering CourseView with props', this.props);
        if (!_.isArray(this.props.courses)) return this.renderEmpty();
        return this.renderWithCourses();
    }
}

CourseView.propTypes = {
    courses: React.PropTypes.array,
};

CourseView.defaultProps = {
    courses: [],
};
