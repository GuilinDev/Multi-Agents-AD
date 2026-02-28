import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { colors } from '../theme';

interface Props {
  data: Array<{ date: string; score: number; [k: string]: unknown }>;
}

export default function TrendChart({ data }: Props) {
  if (!data.length) return <p className="empty">No trend data yet.</p>;
  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" tick={{ fontSize: 12 }} />
        <YAxis domain={[0, 10]} />
        <Tooltip />
        <Line type="monotone" dataKey="score" stroke={colors.lavender} strokeWidth={2} dot={{ r: 4 }} />
      </LineChart>
    </ResponsiveContainer>
  );
}
