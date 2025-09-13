import { Col, Button } from 'react-bootstrap';

interface RangeRowProps {
    labelText: string | JSX.Element;
    value: number;
    unit?: string;
    tempSensor?: number;
    showButton?: boolean;
    variant?: string;
    onClick?: any;
    buttonState?: boolean;
}


function RangeRow({ labelText, value, unit = '%', tempSensor = 0, showButton = false, variant, onClick, buttonState }: RangeRowProps) {
    return (
        <>
            <Col xs="1" className="d-flex justify-content-center">
                {showButton && (
                    <Button size='sm'
                        variant={variant}
                        onClick={onClick}
                    >
                        {buttonState ? '⦿' : '⦾'}
                    </Button>
                )}
            </Col>
            <Col xs="2">{labelText}</Col>
            <Col xs="2">{tempSensor>0 && <div>{tempSensor.toFixed(1)}°C</div>}</Col>
            <Col xs="1" className="p-1">{value}{unit}</Col>
        </>
    );
}

export default RangeRow;