import { Col, Form, Button } from 'react-bootstrap';
import RangeRow from './RangeRow';

interface VentRangeRowProps {
    zone: string;
    zoneStates: { [key: string]: boolean };
    zoneTempModes: { [key: string]: number };
    zoneTemps: { [key: string]: number };
    buttonText: string;
    setZoneState: (zone: string) => void;
    setZoneValue: (zone: string, percent: number) => void;
    getStateColor: (state: boolean) => string;
}

function TempRangeRow({ zone, zoneStates, zoneTempModes, zoneTemps, buttonText, setZoneState, setZoneValue: setzoneTempMode, getStateColor }: VentRangeRowProps) {
    return (
        <>
            <RangeRow
                labelText={<Button size='sm'>{zone}</Button>}
                value={zoneTempModes[zone] ?? 0}
                tempSensor={zoneTemps[zone]}
                showButton={true}
                variant={getStateColor(zoneStates[zone])}
                onClick={() => setZoneState(zone)}
                buttonState={zoneStates[zone]}
                unit="°C"
            />
            <Col className="ps-3">
                <Form.Range
                    value={zoneTempModes[zone] ?? 0}
                    onChange={(e) => { setzoneTempMode(zone, parseInt(e.target.value)) }}
                    min={16}
                    max={32}
                    step={0.5}
                    disabled={buttonText === 'waiting' || !zoneStates[zone]}
                />
            </Col>
            <Col xs="1"></Col>
        </>
    );
}

export default TempRangeRow;