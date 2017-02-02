import React from "react";


export default class Footer extends React.Component {
  render() {
    return (
      <div id="footerwrap">
        <div className="container">
          <div className="row">
            <div className="col-lg-4">
              <h4>About</h4>
              <div className="hline-w"></div>
              <p>Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s.</p>
            </div>
          <div className="col-lg-4">
            <h4>Social Links</h4>
            <div className="hline-w"></div>
            <p>
              <a href="#"><i className="fa fa-dribbble"></i></a>
              <a href="#"><i className="fa fa-facebook"></i></a>
              <a href="#"><i className="fa fa-twitter"></i></a>
              <a href="#"><i className="fa fa-instagram"></i></a>
              <a href="#"><i className="fa fa-tumblr"></i></a>
            </p>
          </div>
          <div className="col-lg-4">
            <h4>Our Bunker</h4>
            <div className="hline-w"></div>
            <p>
              Some Ave, 987,<br/>
              23890, New York,<br/>
              United States.<br/>
            </p>
          </div>
        </div> 
      </div>
    </div> 
    );
  }
}
