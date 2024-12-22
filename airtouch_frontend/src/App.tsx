import { useState, useEffect } from 'react'
import { Container, Button, Row, Col, Form } from 'react-bootstrap'
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
  const [data, setData] = useState(['test', 'test2']);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [zonePercentages, setZonePercentages] = useState({});
  const [zoneTemps, setZoneTemps] = useState({});
  const [ventTotal, setVentTotal] = useState(0);

  const thumbColor = ventTotal >= 100 ? '#5fc998' : '#61a1fe';

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

  const setZones = async () => {
    try {
      const response = await fetch('api/set_zones', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(zonePercentages),
      });
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      const result = await response.json();
      setZonePercentages(result);
    } catch (error) {
      setError(error.message);
    }
  };

  const setZonePercent = (zone: string, percent: number) => {
    setZonePercentages({
      ...zonePercentages,
      [zone]: percent,
    });
  };

  const calcVentTotal = () => {
    let total = 0;
    for (const zone in zonePercentages) {
      total += zonePercentages[zone];
    }
    total = Math.min(total, 100);
    setVentTotal(total);
  }

  const presets = [0, 10, 25, 100];

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    calcVentTotal();
  }, [zonePercentages]);

  return (
    <Container className="mx-0">
      <h1>AirTouch Controller</h1>
        {loading && <p>Loading...</p>}
        <Row>
            <Col xs="2"><h4>Zone</h4></Col>
            <Col xs="2"></Col>
            <Col xs="2"></Col>
            <Col className="text-center"><h4>Vent</h4></Col>
            <Col xs="1"></Col>
        </Row>
        <Row>
          {data && (
            <Col>
              {data.map((zone: any) => (
                <Row key={zone} className="mb-2">
                  <Col xs="2">{zone}</Col>
                  <Col xs="2">{zoneTemps[zone] && <div>{zoneTemps[zone]}°C</div>}</Col>
                  <Col xs="2">{zonePercentages[zone]}%</Col>
                  <Col>
                    <Form.Range
                      value={zonePercentages[zone]}
                      onChange={(e) => { setZonePercent(zone, parseInt(e.target.value)) }}
                      min={0}
                      max={100}
                      step={5}
                    />
                  </Col>
                  <Col xs="1"></Col>
                </Row>
              ))}
            </Col>
          )}
        </Row>
        <Row>
            <Col xs="2">Total</Col>
            <Col xs="2"></Col>
            <Col xs="2">{ventTotal}%</Col>
            <Col>
            <Form.Range
            className='custom-range'
            style={{
              '--thumb-color': thumbColor,
            }}
              value={ventTotal}
                      min={0}
                      max={100}
                      step={5}
                    />
            </Col>
            <Col xs="1"></Col>
        </Row>
        <Row className="justify-content-center">
          <Col xs="auto">
            <Button
              onClick={setZones}
              disabled={ventTotal < 100}
            >
              Set Vents
            </Button>
          </Col>

        </Row>
    </Container>
  )
}

export default App
