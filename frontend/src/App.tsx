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
    const [plotCloudyPie, setPlotCloudyPie] = useState([]);

    // pressure
    const [plotPressure, setPlotPressure] = useState([]);
    const [maxPress, setMaxPress] = useState(0);
    const [minPress, setMinPress] = useState(0);
    const [avgPress, setAvgPress] = useState(0);

    // wind
    const [plotWindy, setPlotWindy] = useState([]);
    const [maxWind, setMaxWind] = useState(0);
    const [minWind, setMinWind] = useState(0);
    const [avgWind, setAvgWind] = useState(0);

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
                      type: 'lines+markers',
                      mode: 'lines+markers',
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
                      type: 'bar',mode: 'markers',
                      marker: {color: ['#00adc4', '#FFBB28', '#ff7442']},
                    }]);

                // @ts-ignore
                setPlotCloudyPie([
                    // @ts-ignore
                    { labels: data.cloudy_plot.status,
                      values: data.cloudy_plot.number,
                      type: 'pie',
                      textinfo: 'percent',

                      marker: {
                        colors: ['#00adc4', '#FFBB28', '#ff7442']
                      },
                      automargin: true
                    }
                  ]);



                // pressure

                const pressureData = data.pressure_plot;

                setMinPress(data.pressure_plot.min)
                setMaxPress(data.pressure_plot.max)
                setAvgPress(data.pressure_plot.avg)

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

                      },
                    ]}
                    layout={{
                      title: 'Ciśnienie',
                      xaxis: { title: 'Data', type: 'date' },
                      yaxis: { title: 'Ciśnienie (hPa)', range: [yMin, yMax] },
                    }}
                  />
                );

                // wind
                const windData = data.windy_plot;
                setMinWind(data.windy_plot.min)
                setMaxWind(data.windy_plot.max)
                setAvgWind(data.windy_plot.avg)

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

        <nav className="navbar navbar-dark bg-dark" style={{position: "fixed", top: 0, zIndex: 1000, width:"100%"}}>
            <div className="container-fluid">
                <h1 className="navbar-brand">
                    <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" fill="currentColor"
                         className="bi bi-cloud-sun" viewBox="0 0 16 16">
                        <path
                            d="M7 8a3.5 3.5 0 0 1 3.5 3.555.5.5 0 0 0 .624.492A1.503 1.503 0 0 1 13 13.5a1.5 1.5 0 0 1-1.5 1.5H3a2 2 0 1 1 .1-3.998.5.5 0 0 0 .51-.375A3.5 3.5 0 0 1 7 8m4.473 3a4.5 4.5 0 0 0-8.72-.99A3 3 0 0 0 3 16h8.5a2.5 2.5 0 0 0 0-5z"/>
                        <path
                            d="M10.5 1.5a.5.5 0 0 0-1 0v1a.5.5 0 0 0 1 0zm3.743 1.964a.5.5 0 1 0-.707-.707l-.708.707a.5.5 0 0 0 .708.708zm-7.779-.707a.5.5 0 0 0-.707.707l.707.708a.5.5 0 1 0 .708-.708zm1.734 3.374a2 2 0 1 1 3.296 2.198q.3.423.516.898a3 3 0 1 0-4.84-3.225q.529.017 1.028.129m4.484 4.074c.6.215 1.125.59 1.522 1.072a.5.5 0 0 0 .039-.742l-.707-.707a.5.5 0 0 0-.854.377M14.5 6.5a.5.5 0 0 0 0 1h1a.5.5 0 0 0 0-1z"/>
                    </svg>
                </h1>

                <h1 className="navbar-brand">
                    Aplikacja pogodowa - z Open-Meteo API
                </h1>
                <h1 className="navbar-brand">

                </h1>
            </div>
        </nav>


        <div className="container-fluid">
            <div className="row" >
                <div className="col-3 px-3 position-fixed" id="sticky-sidebar" style={{backgroundColor: "darkgray", height: '100%', zIndex: 1000, marginTop:75}} >

                    <h1 style={{margin: 20}}>Filtry</h1>
                    <form onSubmit={handleSubmit} style={{ margin: "auto"}}>
                        <div style={{marginTop: 20, marginBottom: 20}}>
                            <label style={{marginTop: 20, marginBottom: 20}}><h4>Liczba wyników</h4></label>
                            <input style={{textAlign: "center"}} type="number" className="form-control" step={1} min={1} max={1000} defaultValue={100} onChange={e => setLimit(e.target.value)}/>
                        </div>

                        <div>
                            <div style={{display: "block"}}>
                                <label><h4>Zakres</h4></label>
                            </div>

                            <div style={{display: "inline-flex", width: '100%'}}>
                                <label style={{justifyContent: "center", alignContent: "center", marginRight: 10}}><b>Od:</b></label>
                                <input style={{marginTop: 20, marginBottom: 20}} type="date" className="form-control" defaultValue={"1990-01-01"} onChange={e => setStartDate(e.target.value)}/>
                            </div>
                            <div style={{display: "inline-flex", width: '100%'}}>
                                <label style={{justifyContent: "center", alignContent: "center", marginRight: 10}}><b>Do:</b></label>
                                <input style={{marginTop: 20, marginBottom: 20}} type="date" className="form-control" defaultValue={"2024-06-28"} onChange={e => setEndDate(e.target.value)}/>
                            </div>
                        </div>

                        <div>
                            <label>Wybierz czujnik</label>
                            <select className="form-select" aria-label="Default select example" onChange={e => setSensor(e.target.value)}>
                                {sensors.map((d: Sensor) => {
                                    return(
                                        <option style={{textAlign: "center"}} key={d.id} value={d.location}>{d.location}</option>
                                        )
                                })}

                            </select>
                        </div>

                        <button style={{marginTop: 20, marginBottom: 20, width: 120}} className="btn btn-dark" id="subbtn" type="submit" >Filtruj</button>
                      </form>
                </div>

                <div className="col offset-3" id="main">
                    <h1 style={{margin: 20, marginTop: 95}}>Temperatura i wilgotność</h1>

                <div style={{display: "inline-block"}}>
                    <div style={{border: "1px lightgray solid", margin:5, marginTop:20, borderRadius: 10, padding: 20}}>
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
                        <table style={{border: "1px gray solid", width: '100%', margin: "auto"}} className="table">
                            <thead>
                            <tr>
                                <th style={{border: "1px gray solid", backgroundColor: "gray"}} scope="col"></th>
                                <th style={{ backgroundColor: "darkgray"}} scope="col">Wartość temperatury [°C]</th>
                            </tr>
                            </thead>
                            <tbody>
                            <tr>
                                <th style={{border: "1px gray solid", backgroundColor: "lightgray"}} scope="row">Minimalna</th>
                                <td>{minTemp}</td>
                            </tr>
                            <tr>
                                <th style={{border: "1px gray solid", backgroundColor: "lightgray"}} scope="row">Maksymalna</th>
                                <td>{maxTemp}</td>
                            </tr>
                            <tr>
                                <th style={{border: "1px gray solid", backgroundColor: "lightgray"}} scope="row">Średnia</th>
                                <td>{avgTemp}</td>
                            </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <div style={{display: "inline-block"}}>
                    <div style={{border: "1px lightgray solid", margin:5, marginTop:20, borderRadius: 10, padding: 20}}>
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

                        <table style={{border: "1px gray solid", width: '100%', margin: "auto"}} className="table">
                            <thead>
                            <tr>
                                <th style={{border: "1px gray solid", backgroundColor: "gray"}} scope="col"></th>
                                <th style={{ backgroundColor: "darkgray"}} scope="col">Wilgotność [%]</th>
                            </tr>
                            </thead>
                            <tbody>
                            <tr>
                                <th style={{border: "1px gray solid", backgroundColor: "lightgray"}} scope="row">Minimalna</th>
                                <td>{minHum}</td>
                            </tr>
                            <tr>
                                <th style={{border: "1px gray solid", backgroundColor: "lightgray"}} scope="row">Maksymalna</th>
                                <td>{maxHum}</td>
                            </tr>
                            <tr>
                                <th style={{border: "1px gray solid", backgroundColor: "lightgray"}} scope="row">Średnia</th>
                                <td>{avgHum}</td>
                            </tr>
                            </tbody>
                        </table>
                    </div>
                </div>


              <div style={{display: "inline-block"}}>
                <h1 style={{margin: 20, marginTop: 30}}>Ciśnienie</h1>
                <div style={{border: "1px lightgray solid", margin:5, marginTop:20, borderRadius: 10, padding: 20}}>
                    {plotPressure}
                    <table style={{border: "1px gray solid", width: '100%', margin: "auto"}} className="table">
                            <thead>
                            <tr>
                                <th style={{border: "1px gray solid", backgroundColor: "gray"}} scope="col"></th>
                                <th style={{ backgroundColor: "darkgray"}} scope="col">Ciśnienie [hPa]</th>
                            </tr>
                            </thead>
                            <tbody>
                            <tr>
                                <th style={{border: "1px gray solid", backgroundColor: "lightgray"}} scope="row">Minimalne</th>
                                <td>{minPress}</td>
                            </tr>
                            <tr>
                                <th style={{border: "1px gray solid", backgroundColor: "lightgray"}} scope="row">Maksymalne</th>
                                <td>{maxPress}</td>
                            </tr>
                            <tr>
                                <th style={{border: "1px gray solid", backgroundColor: "lightgray"}} scope="row">Średnie</th>
                                <td>{avgPress}</td>
                            </tr>
                            </tbody>
                        </table>
                </div>
              </div>

              <div style={{display: "inline-block"}}>
                <h1 style={{margin: 20, marginTop: 30}}>Wiatr</h1>
                <div style={{border: "1px lightgray solid", margin:5, marginTop:20, borderRadius: 10, padding: 20}}>
                    {plotWindy}
                    <table style={{border: "1px gray solid", width: '100%', margin: "auto"}} className="table">
                            <thead>
                            <tr>
                                <th style={{border: "1px gray solid", backgroundColor: "gray"}} scope="col"></th>
                                <th style={{ backgroundColor: "darkgray"}} scope="col">Prędkość wiatru [m/s]</th>
                            </tr>
                            </thead>
                            <tbody>
                            <tr>
                                <th style={{border: "1px gray solid", backgroundColor: "lightgray"}} scope="row">Minimalne</th>
                                <td>{minWind}</td>
                            </tr>
                            <tr>
                                <th style={{border: "1px gray solid", backgroundColor: "lightgray"}} scope="row">Maksymalne</th>
                                <td>{maxWind}</td>
                            </tr>
                            <tr>
                                <th style={{border: "1px gray solid", backgroundColor: "lightgray"}} scope="row">Średnie</th>
                                <td>{avgWind}</td>
                            </tr>
                            </tbody>
                        </table>
                </div>
              </div>

                 <h1 style={{margin: 20, marginTop: 30}}>Zachmurzenie</h1>
                 <div style={{display: "inline-block", marginBottom: 30}}>
                    <div style={{border: "1px lightgray solid", margin:5, marginTop:20, borderRadius: 10, padding: 20}}>
                    <Plot
                      data={plotCloudy}
                      layout={{
                        title: 'Zachmurzenie - wykres słupkowy',
                        xaxis: {
                          title: 'Status',
                          type: 'category',
                        },
                        yaxis: {
                          title: 'Zachmurzenie',
                        },
                      }}
                    />
                    </div>
                 </div>

                 <div style={{display: "inline-block", marginBottom: 30}}>
                    <div style={{border: "1px lightgray solid", margin:5, marginTop:20, borderRadius: 10, padding: 20}}>
                        <Plot
                          data={plotCloudyPie}
                          layout={{
                            title: 'Zachmurzenie - wykres kołowy',
                          }}
                        />
                    </div>
                 </div>






                </div>
            </div>
        </div>
    </div>
  );
}

export default App;
