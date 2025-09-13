import { Button } from 'react-bootstrap';

interface TempModeButtonProps {
    zone: string;
    zoneTempModes: { [key: string]: number };
    setZoneTempMode: (zone: string, percent: number) => void;
}

function TempModeButton({ zone, zoneTempModes, setZoneTempMode }: TempModeButtonProps) {
    return (
        <>
            <Button
                variant={zoneTempModes[zone] < 16 ? 'primary' : 'info'}
                size='sm'
                onClick={() => {
                    setZoneTempMode(zone, zoneTempModes[zone] * -1);
                }}
            >
                {zone}
            </Button>
        </>
    );
}

export default TempModeButton;