import { Row, Col } from 'react-bootstrap';

interface LabelRowProps {
  leftLabel: string;
  rightLabel: string;
}

function LabelRow({ leftLabel, rightLabel }: LabelRowProps) {
  return (
    <Row>
      <Col xs="2"><h4>{leftLabel}</h4></Col>
      <Col xs="2"></Col>
      <Col xs="2"></Col>
      <Col className="text-center"><h4>{rightLabel}</h4></Col>
      <Col xs="1"></Col>
    </Row>
  );
}

export default LabelRow;