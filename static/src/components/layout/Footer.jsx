import React from 'react';

import './Footer.scss';

const Footer = () => (
    <div className="Footer">
        <div className="container">
            <div className="row">
                <div className="col-lg-4">
                    <h4>About</h4>
                    <div className="hline-w"></div>
                </div>
                <div className="col-lg-4">
                    <h4>Social Links</h4>
                    <div className="hline-w"></div>
                    <p>
                        <a href="#"><i className="fa fa-dribbble"></i></a>
                        <a href="#"><i className="fa fa-facebook"></i></a>
                        <a href="#"><i className="fa fa-tumblr"></i></a>
                    </p>
                </div>
                <div className="col-lg-4">
                    <h4>Our Bunker</h4>
                    <div className="hline-w"></div>
                </div>
            </div>
        </div>
    </div>
);

export default Footer;
