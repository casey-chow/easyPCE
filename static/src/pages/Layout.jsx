import React from 'react';

import Footer from '../components/layout/Footer';
import Nav from '../components/layout/Nav';

const Layout = props => (
    <div>
        <div className="row">
            <Nav />
        </div>
        <div className="row">
            <div className="container mt">
                {props.children}
            </div>
        </div>
        <div className="row">
            <Footer />
        </div>
    </div>
);

Layout.propTypes = {
    children: React.PropTypes.element.isRequired,
};

export default Layout;
