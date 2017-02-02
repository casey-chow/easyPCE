import React from 'react';
import { Link } from 'react-router';

import Footer from '../components/layout/Footer';
import Nav from '../components/layout/Nav';

class Layout extends React.Component {
    render() {
        const { location } = this.props;

        return (
            <div>
                <div className="row">
                    <Nav />
                </div>
                <div className="row">
                    <div className="container mt">
                        {this.props.children}
                    </div>
                </div>
                <div className="row">
                    <Footer />
                </div>
            </div>
        );
    }
}


export default Layout;
