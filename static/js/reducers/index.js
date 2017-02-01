import { combineReducers } from 'redux';

import courses from './coursesReducer';
import subjects from './subjectsReducer';
import terms from './termsReducer';

export default combineReducers({
    courses,
    subjects,
    terms,
});
