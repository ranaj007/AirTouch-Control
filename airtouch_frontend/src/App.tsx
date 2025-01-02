import { useState, useEffect } from 'react'
import { Container, Button, Row, Col, Form } from 'react-bootstrap'
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
  const [data, setData] = useState(['test', 'test2']);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [zoneStates, setZoneStates] = useState({});
  const [zonePercentages, setZonePercentages] = useState({});
  const [zoneTemps, setZoneTemps] = useState({});
  const [ventTotal, setVentTotal] = useState(0);
  const [buttonText, setButtonText] = useState('Set Vents');

  const thumbColor = ventTotal >= 100 ? '#5fc998' : '#61a1fe';

  const stateColors = {
    'ON': 'primary',
    'OFF': 'secondary',
  };

  const fetchData = async () => {
    try {
      const response = await fetch('api/get_zones');
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      const result = await response.json();
      setData(result['zones']);
      setZoneStates(result['zone_states']);
      setZonePercentages(result['zone_percents']);
      setZoneTemps(result['zone_temps']);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const setZones = async () => {
    setButtonText('Waiting...');
    try {
      const response = await fetch('api/set_zones', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({'zone_states': zoneStates, 'zone_percents': zonePercentages}),
      });
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
    } catch (error) {
      setError(error.message);
    }
    setButtonText('Set Vents');
  };

  const setZoneState = (zone: string) => {
    setZoneStates({
      ...zoneStates,
      [zone]: zoneStates[zone] === 'ON' ? 'OFF' : 'ON',
    });
  }

  const setZonePercent = (zone: string, percent: number) => {
    setZonePercentages({
      ...zonePercentages,
      [zone]: percent,
    });
  };

  const calcVentTotal = () => {
    let total = 0;
    for (const zone in zonePercentages) {
      if (zoneStates[zone] === 'ON') {
        total += zonePercentages[zone];
      }
    }
    total = Math.min(total, 100);
    setVentTotal(total);
  }

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    calcVentTotal();
  }, [zoneStates, zonePercentages]);

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
      <Col xs="1"></Col>
        <Col xs="2">Total</Col>
        <Col xs="2"></Col>
        <Col xs="1" className="p-1">{ventTotal}%</Col>
        <Col className="ps-3">
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
      <Row>
        {data && (
          <Col>
            {data.map((zone: any) => (
              <Row key={zone} className="mb-2 align-items-center">
                <Col xs="1" className="d-flex justify-content-center">
                  <Button size='sm'
                    variant={stateColors[zoneStates[zone]]}
                    onClick={() => setZoneState(zone)}
                  >
                    {zoneStates[zone] === 'ON' ? '⦿' : '⦾'}
                  </Button>
                </Col>
                <Col xs="2">{zone}</Col>
                <Col xs="2">{zoneTemps[zone] && <div>{zoneTemps[zone]}°C</div>}</Col>
                <Col xs="1" className="px-2">{zoneStates[zone] === 'ON' ? zonePercentages[zone] : '0'}%</Col>
                <Col className="ps-3">
                  <Form.Range
                    value={zonePercentages[zone]}
                    onChange={(e) => { setZonePercent(zone, parseInt(e.target.value)) }}
                    min={0}
                    max={100}
                    step={5}
                    disabled={buttonText === 'waiting' || zoneStates[zone] === 'OFF'}
                  />
                </Col>
                <Col xs="1"></Col>
              </Row>
            ))}
          </Col>
        )}
      </Row>
      <Row className="justify-content-center">
        <Col xs="auto">
          <Button
            onClick={setZones}
            disabled={ventTotal < 100}
          >
            {buttonText}
          </Button>
        </Col>
        <Col xs="auto">
          <Button variant='success' onClick={fetchData}>
            ↻
          </Button>
        </Col>

      </Row>
    </Container>
  )
}

export default App
