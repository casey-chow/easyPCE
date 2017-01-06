import axios from "axios";

export function fetchCourses() {
  return function(dispatch) {
    axios.get("/api/courses")
      .then((response) => {
        dispatch({type: "FETCH_COURSES_FULFILLED", payload: response.data})
      })
      .catch((err) => {
        dispatch({type: "FETCH_COURSES_REJECTED", payload: err})
      })
  }
}
