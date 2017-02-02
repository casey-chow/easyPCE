export default function reducer(state = {
    terms: {},
    fetching: false,
    fetched: false,
    error: null,
}, action) {
    switch (action.type) {
    case 'FETCH_TERMS': {
        return { ...state, fetching: true };
    }
    case 'FETCH_TERMS_REJECTED': {
        return { ...state, fetching: false, error: action.payload };
    }
    case 'FETCH_TERMS_FULFILLED': {
        return {
            ...state,
            fetching: false,
            fetched: true,
            terms: action.payload,
        };
    }
    default: {
        return state;
    }
    }
}
