import React from 'react';
import ReactDOM from 'react-dom';

class BooksList extends React.Component {
    componentDidMount() {
        this.loadBooksFromServer();
        setInterval(this.loadBooksFromServer, 
                    this.props.pollInterval)
    }

    loadBooksFromServer() {
        $.ajax({
            url: this.props.url,
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
        if (this.state.data) {
            console.log('DATA!');
            var bookNodes = this.state.data.map(function(book){
                return <li> {book.title} </li>
            });
        }
        return (
            <div>
                <h1>Hello React!</h1>
                <ul>
                    {bookNodes}
                </ul>
            </div>
        )
    }
}

ReactDOM.render(<BooksList url='/api/' pollInterval={1000} />, 
    document.getElementById('container'))