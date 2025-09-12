import { Col, Form, Button } from 'react-bootstrap';
import RangeRow from './RangeRow';

interface VentRangeRowProps {
    zone: string;
    zoneStates: { [key: string]: boolean };
    zoneValues: { [key: string]: number };
    zoneTemps: { [key: string]: number };
    zoneTempMode: { [key: string]: boolean };
    buttonText: string;
    setZoneState: (zone: string) => void;
    setZoneValue: (zone: string, percent: number) => void;
    getStateColor: (state: boolean) => string;
    min?: number;
    max?: number;
    step?: number;
}

function VentRangeRow({ zone, zoneStates, zoneValues, zoneTemps, zoneTempMode, buttonText, setZoneState, setZoneValue, getStateColor, min = 0, max = 100, step = 5 }: VentRangeRowProps) {
    let displayValue;
    if (Object.keys(zoneTempMode).includes(zone) && zoneTempMode[zone]) {
        displayValue = zoneValues[zone] ?? 0; // always show temperature
    } else {
        displayValue = zoneStates[zone] ? zoneValues[zone] : 0; // only show vent percentage if vent is on
    }

    return (
        <>
            <RangeRow
                labelText={Object.keys(zoneTempMode).includes(zone) ? <Button size='sm'>{zone}</Button> : zone}
                value={displayValue}
                tempSensor={zoneTemps[zone]}
                showButton={true}
                variant={getStateColor(zoneStates[zone])}
                onClick={() => setZoneState(zone)}
                buttonState={zoneStates[zone]}
            />
            <Col className="ps-3">
                <Form.Range
                    value={zoneValues[zone] ?? 0}
                    onChange={(e) => { setZoneValue(zone, parseInt(e.target.value)) }}
                    min={min}
                    max={max}
                    step={step}
                    disabled={buttonText === 'waiting' || !zoneStates[zone]}
                />
            </Col>
            <Col xs="1"></Col>
        </>
    );
}

export default VentRangeRow;