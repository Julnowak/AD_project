import React, {useEffect, useState} from 'react';
import './App.css';
// @ts-ignore
import Plot from 'react-plotly.js';

interface Sensor {
    id: number,
    name: string,
    location: string,
}

function App() {

    const [socket, setSocket] = useState<WebSocket | null>(null);
    const [limit, setLimit] = useState<string | null>('100');
    const [startdate, setStartDate] = useState<string|null>(null);
    const [enddate, setEndDate] = useState<string|null>(null);

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

    // pressure
    const [plotPressure, setPlotPressure] = useState([]);

    // wind
    const [plotWindy, setPlotWindy] = useState([]);

    // sensors
    const [sensors, setSensors] = useState([]);
    const [sensor, setSensor] = useState<Sensor|null| string>(null);

    useEffect(() => {

        const newSocket = new WebSocket(`ws://127.0.0.1:8000/ws/socket/`);
        // @ts-ignore
        setSocket(newSocket);
        newSocket.onopen = () => {
            console.log("WebSocket connected");
            let btn = document.getElementById("subbtn")
            btn?.click();
        };
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

                // pressure

                const pressureData = data.pressure_plot;
                const minPressure = Math.min(...pressureData.value);
                const maxPressure = Math.max(...pressureData.value);
                const yMin = minPressure - 20;
                const yMax = maxPressure + 10;
          
                console.log("Pressure Data:", pressureData);
                console.log("Pressure Y-Axis Range:", yMin, yMax);

                // @ts-ignore
                setPlotPressure(
                  // @ts-ignore
                  <Plot
                    data={[
                      {
                        x: pressureData.date,
                        y: pressureData.value,
                        fill: 'tozeroy',
                        type: 'scatter',
                        mode: 'lines',
                        line: { color: 'blue' },
                      },
                    ]}
                    layout={{
                      title: 'Ciśnienie',
                      xaxis: { title: 'Data', type: 'date' },
                      yaxis: { title: 'Ciśnienie (hPa)', range: [yMin, yMax] },
                    }}
                  />
                );



                // // @ts-ignore
                // setPlotPressure([
                //     // @ts-ignore
                //     { x: data.pressure_plot.date,
                //       y: data.pressure_plot.value,
                //       fill: 'tozeroy',
                //       type: 'scatter',
                //       mode: 'lines',
                //       line: { color: 'blue' },
                //     }
                //   ]);


                // wind
                const windData = data.windy_plot;
                const fixedArrowLength = 2.5; // Adjust this length to make arrows shorter
          
                const annotations = windData.date.map((date: string, idx: number) => {
                  const angleRad = windData.direction[idx] * (Math.PI / 180); // Convert degrees to radians
                  const x0 = new Date(date).getTime();
                  const y0 = windData.speed[idx];
                  const x1 = x0 + fixedArrowLength * Math.cos(angleRad) * 3600000; // Convert to milliseconds
                  const y1 = y0 + fixedArrowLength * Math.sin(angleRad);
          
                  return {
                    x: new Date(x0),
                    y: y0,
                    ax: new Date(x1),
                    ay: y1,
                    xref: 'x',
                    yref: 'y',
                    axref: 'x',
                    ayref: 'y',
                    showarrow: true,
                    arrowhead: 2,
                    arrowsize: 1,
                    arrowwidth: 1,
                    arrowcolor: 'black',
                  };
                });
                
                // @ts-ignore
                setPlotWindy(
                  // @ts-ignore
                  <Plot
                    data={[
                      {
                        x: windData.date,
                        y: windData.speed,
                        mode: 'markers',
                        marker: { color: 'blue', size: 1 },
                        name: 'Wind Speed',
                      },
                    ]}
                    layout={{
                      title: 'Prędkość wiatru',
                      xaxis: { title: 'Data', type: 'date' },
                      yaxis: { title: 'Szybkość (m/s)' },
                      annotations: annotations,
                      showlegend: false,
                    }}
                  />
                );


                // @ts-ignore
                // setPlotWindy([
                //     // @ts-ignore
                //     { x: data.windy_plot.date,
                //       y: data.windy_plot.speed,
                //       fill: 'tozeroy',
                //       type: 'scatter',
                //       mode: 'lines',
                //       line: { color: 'blue' },
                //     }
                //   ]);

                setSensor(data.sensor)

            }
    }

    }, [socket]);


    // @ts-ignore
    const handleSubmit = (event) => {
    event.preventDefault();
    if (socket) {

        console.log(sensor)
        const data = {
            limit: limit,
            sensor: sensor,
            startdate: startdate,
            enddate: enddate,
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
                  title: 'Temperatura (°C)',
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
                  title: 'Wilgotność (%)',
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

        {/* <Plot
              data={plotPressure}
              layout={{
                title: 'Ciśnienie',
                xaxis: {
                  title: 'Data',
                  type: 'date',
                },
                yaxis: {
                  title: 'Ciśnienie (hPa)',
                },
              }}
            /> */}
            {plotPressure}

      <h3>Wiatr</h3>

        {/* <Plot
              data={plotWindy}
              layout={{
                title: 'Ciśnienie',
                xaxis: {
                  title: 'Data',
                  type: 'date',
                },
                yaxis: {
                  title: 'Szybkość [m/s]',
                },
              }}
            /> */}
            {plotWindy}


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
            <input type="date" className="form-control" onChange={e => setStartDate(e.target.value)}/>
            <input type="date" className="form-control" onChange={e => setEndDate(e.target.value)}/>
        </div>

        <div>
            <label>Wybierz czujnik</label>
            <select className="form-select" aria-label="Default select example" onChange={e => setSensor(e.target.value)}>
                {sensors.map((d: Sensor) => {
                    return(
                        <option key={d.id} value={d.location}>{d.location}</option>
                        )
                })}

            </select>
        </div>

        <button className="btn btn-dark" id="subbtn" type="submit" >Filtruj</button>
      </form>


    </div>
  );
}

export default App;
