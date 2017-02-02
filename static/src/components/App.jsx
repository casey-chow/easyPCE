import React from 'react';
import { Provider } from 'react-redux';
import { Router, Route, IndexRoute, hashHistory } from 'react-router';

import Layout from '../pages/Layout';
import store from '../store';
import CourseView from '../pages/CourseView';

import './App.scss';

const App = () => (
  <Provider store={store}>
      <Router history={hashHistory}>
          <Route path="/" component={Layout}>
              <IndexRoute component={CourseView}></IndexRoute>
          </Route>
      </Router> 
  </Provider>
);

export default App;
