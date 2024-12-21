import { useState, useEffect } from 'react'
import { Container, Button, Row, Col, Form } from 'react-bootstrap'
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
  const [data, setData] = useState(['test', 'test2']);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [value, setValue] = useState(50);
  const [zonePercentages, setZonePercentages] = useState({});
  const [zoneTemps, setZoneTemps] = useState({});

  const setZonePercent = (zone: string, percent: number) => {
    setZonePercentages({
      ...zonePercentages,
      [zone]: percent,
    });
  };

  const presets = [0, 10, 25, 100];

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('api/get_zones');
        if (!response.ok) {
          throw new Error(`Error: ${response.status}`);
        }
        const result = await response.json();
        setData(result['zones']);
        setZonePercentages(result['zone_percents']);
        setZoneTemps(result['zone_temps']);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="mx-2">
      <h1>AirTouch Controller</h1>
        {loading && <p>Loading...</p>}
        <Row>
          <Col>
          <Row>
            <Col xs="2"><h4>Zone</h4></Col>
            <Col xs="1"><h4>Temp</h4></Col>
            <Col xs="1"><h4>Vent</h4></Col>
            <Col md={{offset: 1}}><h4>Set</h4></Col>
            <Col className='ms-5'><h4>Presets</h4></Col>
          </Row>
          </Col>
        </Row>
        <Row>

          {data && (
            <Col>
              {data.map((zone: any) => (
                <Row key={zone} className="mb-2">
                  <Col xs="2">{zone}</Col>
                  <Col xs="1">{zoneTemps[zone] && <div>{zoneTemps[zone]}°C</div>}</Col>
                  <Col xs="auto">{zonePercentages[zone]}%</Col>
                  <Col>
                    <Form.Range
                      value={zonePercentages[zone]}
                      onChange={(e) => { setZonePercent(zone, parseInt(e.target.value)) }}
                      min={0}
                      max={100}
                      step={5}
                    />
                  </Col>
                  {presets.map((preset) => (
                    <Col className="px-1" key={`${zone}-${preset}`} xs="auto">
                      <Button key={preset} onClick={() => setZonePercent(zone, preset)}>{preset}</Button>
                    </Col>
                  ))}
                </Row>
              ))}
            </Col>
          )}
        </Row>
    </div>
  )
}

export default App
