export default function reducer(state = {
    subjects: {},
    fetching: false,
    fetched: false,
    error: null,
}, action) {
    switch (action.type) {
    case 'FETCH_SUBJECTS': {
        return { ...state, fetching: true };
    }
    case 'FETCH_SUBJECTS_REJECTED': {
        return { ...state, fetching: false, error: action.payload };
    }
    case 'FETCH_SUBJECTS_FULFILLED': {
        return {
            ...state,
            fetching: false,
            fetched: true,
            subjects: action.payload,
        };
    }
    default: {
        return state;
    }
    }
}
