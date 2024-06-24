import React, {useEffect, useState} from 'react';
import './App.css';
// @ts-ignore
import Plot from 'react-plotly.js';

function App() {

    const [socket, setSocket] = useState<WebSocket | null>(null);
    const [limit, setLimit] = useState<string | null>('100');
    const [plotData, setPlotData] = useState([]);

    useEffect(() => {

        const newSocket = new WebSocket(`ws://127.0.0.1:8000/ws/socket/`);
        // @ts-ignore
        setSocket(newSocket);
        newSocket.onopen = () => console.log("WebSocket connected");
        newSocket.onclose = () => {
            console.log("WebSocket disconnected");
        };
        return () => {
            newSocket.close();
        };

    }, []);

    useEffect(() => {
    if (socket) {
            socket.onmessage = (event) => {

                const data = JSON.parse(event.data);
                console.log(data)
                // @ts-ignore
                setPlotData([
                    // @ts-ignore
                    { x: data.likes,
                      y: data.likes,
                      type: 'scatter',
                      mode: 'lines+markers',
                      marker: {color: 'red'},
                    }
                  ]);

            }
    }

    }, [socket]);


    // @ts-ignore
    const handleSubmit = (event) => {
    event.preventDefault();
    if (socket) {

        console.log(limit)
        const data = {
            limit: limit,
        };
        socket.send(JSON.stringify(data));

    }
    };

  return (
    <div className="App">
      <h1>Hello</h1>

      <h3>Temperatura i wilgotność</h3>
        <Plot
          data={plotData}
          layout={{ title: 'Real-Time Data' }}
        />
      <h3>Ciśnienie</h3>
      <h3>Wiatr</h3>
      <h3>Zachmurzenie</h3>

      <form onSubmit={handleSubmit} style={{ width: 400, margin: "auto"}}>
        <div>
            <label>Liczba wyników</label>
            <input type="number" className="form-control" step={1} min={1} max={1000} defaultValue={100} onChange={e => setLimit(e.target.value)}/>
        </div>

        <div>
            <label>Zakres</label>
            <input type="date" className="form-control" />
            <input type="date" className="form-control" />
        </div>

        <div>
            <label>Krok czasowy</label>
            <select className="form-select" aria-label="Default select example">
                <option value="1">Godzina</option>
                <option value="2">Dzień</option>
                <option value="3">Miesiąc</option>
            </select>
        </div>
        <button className="btn btn-dark" type="submit" >Filtruj</button>
      </form>
    </div>
  );
}

export default App;
