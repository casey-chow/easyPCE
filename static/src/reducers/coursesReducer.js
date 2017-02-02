export default function reducer(state = {
    courses: {},
    fetching: false,
    fetched: false,
    error: null,
}, action) {
    switch (action.type) {
    case 'FETCH_COURSES': {
        return { ...state, fetching: true };
    }
    case 'FETCH_COURSES_REJECTED': {
        return { ...state, fetching: false, error: action.payload };
    }
    case 'FETCH_COURSES_FULFILLED': {
        return {
            ...state,
            fetching: false,
            fetched: true,
            courses: action.payload,
        };
    }
    default: {
        return state;
    }
    }
}

/* course format:
{
    course_id: null,
    title: null,
    term: null,
    primary_number: null;
    pdf: null,
    pdf_only: null,
    audit: null,
    dist_req: null,
    description: null,
    additional_info: null,
    instructors: null,
    last_updated: null,

}
*/
