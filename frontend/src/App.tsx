import React, {useEffect, useState} from 'react';
import './App.css';
// @ts-ignore
import Plot from 'react-plotly.js';

// interface Sensor = {
//     id: number,
//     name: string
// }
function App() {

    const [socket, setSocket] = useState<WebSocket | null>(null);
    const [limit, setLimit] = useState<string | null>('100');

    // temperature
    const [plotData, setPlotData] = useState([]);
    const [maxTemp, setMaxTemp] = useState(0);
    const [minTemp, setMinTemp] = useState(0);
    const [avgTemp, setAvgTemp] = useState(0);

    // humidity
    const [plotHumidity, setPlotHumidity] = useState([]);
    const [maxHum, setMaxHum] = useState(0);
    const [minHum, setMinHum] = useState(0);
    const [avgHum, setAvgHum] = useState(0);

    // cloudy
    const [plotCloudy, setPlotCloudy] = useState([]);
    // const [maxHum, setMaxHum] = useState(0);
    // const [minHum, setMinHum] = useState(0);
    // const [avgHum, setAvgHum] = useState(0);

    // sensors
    const [sensors, setSensors] = useState([]);

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
                setSensors(data.sensors)


                // @ts-ignore
                setPlotData([
                    // @ts-ignore
                    { x: data.temperature_plot.date,
                      y: data.temperature_plot.temperature,
                      type: 'scatter',
                      mode: 'markers',
                      marker: {color: 'red'},
                    }
                  ]);

                setMinTemp(data.temperature_plot.min)
                setMaxTemp(data.temperature_plot.max)
                setAvgTemp(data.temperature_plot.avg)

                setPlotHumidity([
                    // @ts-ignore
                    { x: data.humidity_plot.date,
                      y: data.humidity_plot.humidity,
                      type: 'bar',
                      mode: 'lines+markers',
                      marker: {color: 'lightblue'},
                    }
                  ]);

                setMinHum(data.humidity_plot.min)
                setMaxHum(data.humidity_plot.max)
                setAvgHum(data.humidity_plot.avg)

                // cloudy

                // @ts-ignore
                setPlotCloudy([
                    // @ts-ignore
                    { x: data.cloudy_plot.status,
                      y: data.cloudy_plot.number,
                      type: 'bar',
                      mode: 'markers',
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
        <div style={{display: "inline-block"}}>
            <Plot
              data={plotData}
              layout={{
                title: 'Temperatura',
                xaxis: {
                  title: 'Data',
                  type: 'date',
                },
                yaxis: {
                  title: 'Temperatura',
                },
              }}
            />

            <table style={{border: "1px black solid", width: 300, margin: "auto"}} className="table">
                <thead>
                <tr>
                    <th style={{border: "1px black solid"}} scope="col"></th>
                    <th scope="col">Wartość temperatury</th>
                </tr>
                </thead>
                <tbody>
                <tr>
                    <th style={{border: "1px black solid"}} scope="row">Minimalna</th>
                    <td>{minTemp}</td>
                </tr>
                <tr>
                    <th style={{border: "1px black solid"}} scope="row">Maksymalna</th>
                    <td>{maxTemp}</td>
                </tr>
                <tr>
                    <th style={{border: "1px black solid"}} scope="row">Średnia</th>
                    <td>{avgTemp}</td>
                </tr>
                </tbody>
            </table>
        </div>

        <div style={{display: "inline-block"}}>
            <Plot
              data={plotHumidity}
              layout={{
                title: 'Wilgotność powietrza',
                xaxis: {
                  title: 'Data',
                  type: 'date',
                },
                yaxis: {
                  title: 'Wilgotność',
                },
              }}
            />

            <table style={{border: "1px black solid", width: 300, margin: "auto"}} className="table">
                <thead>
                <tr>
                    <th style={{border: "1px black solid"}} scope="col"></th>
                    <th scope="col">Wilgotność</th>
                </tr>
                </thead>
                <tbody>
                <tr>
                    <th style={{border: "1px black solid"}} scope="row">Minimalna</th>
                    <td>{minHum}</td>
                </tr>
                <tr>
                    <th style={{border: "1px black solid"}} scope="row">Maksymalna</th>
                    <td>{maxHum}</td>
                </tr>
                <tr>
                    <th style={{border: "1px black solid"}} scope="row">Średnia</th>
                    <td>{avgHum}</td>
                </tr>
                </tbody>
            </table>

        </div>


      <h3>Ciśnienie</h3>
      <h3>Wiatr</h3>
      <h3>Zachmurzenie</h3>
        <Plot
              data={plotCloudy}
              layout={{
                title: 'Zachmurzenie',
                xaxis: {
                  title: 'Status',
                  type: 'category',
                },
                yaxis: {
                  title: 'Zachmurzenie',
                },
              }}
            />

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
        {/*{sensors.map(d => (<li key={d.id}>{d.name}</li>))} */}
    </div>
  );
}

export default App;
