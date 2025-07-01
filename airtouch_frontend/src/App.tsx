import { useState, useEffect } from 'react'
import { Container, Button, Row, Col, Form } from 'react-bootstrap'
import LabelRow from './LabelRow';
import RangeRow from './RangeRow';

import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
  const [data, setData] = useState(['test', 'test2']);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [acPower, setAcPower] = useState(false);
  const [acTemp, setAcTemp] = useState(20);
  const [zoneStates, setZoneStates] = useState<{ [key: string]: boolean }>({});
  const [zonePercentages, setZonePercentages] = useState<{ [key: string]: number }>({});
  const [zoneTemps, setZoneTemps] = useState<{ [key: string]: number }>({});
  const [ventTotal, setVentTotal] = useState(0);
  const [buttonText, setButtonText] = useState('Set Vents');

  const thumbColor = ventTotal >= 100 ? '#5fc998' : '#61a1fe';

  const getStateColor = (zoneState: boolean) =>{
    if (zoneState)
    {
      return 'primary';
    } else {
      return 'secondary';
    }
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
    } catch (error: any) {
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
        body: JSON.stringify({ 'zone_states': zoneStates, 'zone_percents': zonePercentages }),
      });
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
    } catch (error: any) {
      setError(error.message);
    }
    setButtonText('Set Vents');
  };

  const setZoneState = (zone: string) => {
    setZoneStates({
      ...zoneStates,
      [zone]: !zoneStates[zone],
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
      if (zoneStates[zone]) {
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
      <LabelRow
        leftLabel='Power'
        rightLabel='Temp'
      />

      <Row className="mb-2 align-items-center">
        <RangeRow
          labelText='AC'
          value={acTemp}
          unit="°C"
          showButton={true}
          variant={acPower ? 'primary' : 'secondary'}
          onClick={() => setAcPower(!acPower)}
          buttonState={acPower}
        />
        <Col className="ps-3">
          <Form.Range
            value={acTemp}
            min={16}
            max={32}
            onChange={(e) => setAcTemp(parseInt(e.target.value))}
            disabled={!acPower}
          />
        </Col>
        <Col xs="1"></Col>
      </Row>

      <LabelRow
        leftLabel='Zone'
        rightLabel='Vent'
      />

      <Row>
        <RangeRow
          labelText='Total'
          value={ventTotal}
        />
        <Col className="ps-3">
          <Form.Range
            className='custom-range'
            style={{
              '--thumb-color': thumbColor,
            } as React.CSSProperties}
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
                <RangeRow
                  labelText={zone}
                  value={zoneStates[zone] ? zonePercentages[zone] : 0}
                  tempSensor={zoneTemps[zone]}
                  showButton={true}
                  variant={getStateColor(zoneStates[zone])}
                  onClick={() => setZoneState(zone)}
                  buttonState={zoneStates[zone]}
                />
                <Col className="ps-3">
                  <Form.Range
                    value={zonePercentages[zone] ?? 0}
                    onChange={(e) => { setZonePercent(zone, parseInt(e.target.value)) }}
                    min={0}
                    max={100}
                    step={5}
                    disabled={buttonText === 'waiting' || !zoneStates[zone]}
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
