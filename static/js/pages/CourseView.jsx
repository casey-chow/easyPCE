import React from 'react';
import { connect } from "react-redux";
import { fetchCourses } from "../actions/coursesActions"

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
        this.props.dispatch(fetchCourses())
    }

    render() {
        console.log("the current props are... ", this.props)
        return ( 
            <div>
                <h1>Hello React! This is a test.</h1>
                <p>Test test test</p>
                <p> Test again </p>
            </div>
        )
    }
}
