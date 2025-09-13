import { Col, Form, Button } from 'react-bootstrap';
import RangeRow from './RangeRow';

interface ComboRangeRowProps {
    zone: string;
    labelText?: string | JSX.Element;
    zoneStates: { [key: string]: boolean };
    zonePercentages: { [key: string]: number };
    zoneTempModes: { [key: string]: number };
    zoneTemps: { [key: string]: number };
    buttonText: string;
    setZoneState: (zone: string) => void;
    setZonePercent: (zone: string, percent: number) => void;
    setZoneTempMode: (zone: string, percent: number) => void;
    getStateColor: (state: boolean) => string;
}

function ComboRangeRow({ zone, labelText = zone, zoneStates, zonePercentages, zoneTemps, zoneTempModes, buttonText, setZoneState, setZonePercent, setZoneTempMode, getStateColor }: ComboRangeRowProps) {
    let displayValue = zoneStates[zone] ? zonePercentages[zone] : 0; // only show vent percentage if vent is on
    let sliderValue = zonePercentages[zone] ?? 0;
    let unit = "%";
    let min = 0;
    let max = 100;
    let step = 5;
    let slideFactor = 1;

    let setZoneValue = setZonePercent;
    
    if (Object.keys(zoneTempModes).includes(zone)) {
        if (zoneTempModes[zone] >= 16) {
            displayValue = zoneTempModes[zone] ?? 0; // always show temperature
            sliderValue = zoneTempModes[zone] ?? 0;
            setZoneValue = setZoneTempMode;
            unit = "°C";
            min = 160;
            max = 320;
            step = 1;
            slideFactor = 10;
        }
    }

    return (
        <>
            <RangeRow
                labelText={labelText}
                value={displayValue}
                tempSensor={zoneTemps[zone]}
                showButton={true}
                variant={getStateColor(zoneStates[zone])}
                onClick={() => setZoneState(zone)}
                buttonState={zoneStates[zone]}
                unit={unit}
            />
            <Col className="ps-3">
                <Form.Range
                    value={sliderValue*slideFactor}
                    onChange={(e) => { setZoneValue(zone, parseInt(e.target.value)/slideFactor) }}
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

export default ComboRangeRow;