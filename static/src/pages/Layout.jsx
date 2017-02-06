import React from 'react';

import Footer from '../components/layout/Footer';
import Nav from '../components/layout/Nav';

import './Layout.scss';

const Layout = props => (
    <div className="Layout">
        <div className="row">
            <Nav />
        </div>
        <div className="row content">
            <div className="container mt">
                {props.children}
            </div>
        </div>
        <Footer />
    </div>
);

Layout.propTypes = {
    children: React.PropTypes.element.isRequired,
};

export default Layout;
