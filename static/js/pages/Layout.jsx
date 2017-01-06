import React from 'react';
import { Link } from "react-router";
import $ from 'jquery';
import ReactDOM from 'react-dom';

class Layout extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            data: [],
        };
        this.loadBooksFromServer = this.loadBooksFromServer.bind(this);
        this.url = '/api/';
        this.pollInterval=1000;
    }

    componentDidMount() {
        this.loadBooksFromServer();
        setInterval(this.loadBooksFromServer, 
                    this.pollInterval)
    }

    loadBooksFromServer() {
        $.ajax({
            url: this.url,
            datatype: 'json',
            cache: false,
            success: (data) => {
                this.setState({data: data});
            },
        });
    }

    getInitialState() {
        return {data: []};
    }

    render() {
        console.log("the current state is: ", this.state)
        if (this.state.data) {
            console.log('DATA!');
            var bookNodes = this.state.data.map(function(book){
                return <li> {book.title} </li>
            });
        }
        return (
            <div>
                <h1>Hello React! This is a test.</h1>
                <ul>
                    {bookNodes}
                </ul>
            </div>
        )
    }
}


export default Layout;
