import React from 'react';
import { connect } from "react-redux";
import fetchCourses from "../actions/coursesActions"

@connect((store) => {
  return {
    courses: store.courses.courses,
  };
})

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

    render() {
        return (
            <div>
                <h1>Hello React!!</h1>
                <p>Test testing!</p>
            </div>
        );
    }
}
