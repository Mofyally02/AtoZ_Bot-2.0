import { Clock } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { useBotStore } from '../../stores/botStore';
import MetricCard from './MetricCard';

const BotUptimeCard: React.FC = () => {
  const { botStatus, loginStartTime } = useBotStore();
  const [uptime, setUptime] = useState('00:00:00');

  useEffect(() => {
    console.log('BotUptimeCard: botStatus.is_running:', botStatus?.is_running, 'loginStartTime:', loginStartTime);
    if (!botStatus?.is_running || !loginStartTime) {
      setUptime('00:00:00');
      return;
    }

    const calculateUptime = () => {
      if (!loginStartTime) {
        setUptime('00:00:00');
        return;
      }
      
      const now = new Date();
      const diffMs = now.getTime() - loginStartTime.getTime();

      console.log('BotUptimeCard: calculateUptime - diffMs:', diffMs, 'loginStartTime:', loginStartTime, 'now:', now);

      if (diffMs < 0) {
        setUptime('00:00:00');
        return;
      }

      // Convert to hours, minutes, seconds
      const totalSeconds = Math.floor(diffMs / 1000);
      const hours = Math.floor(totalSeconds / 3600);
      const minutes = Math.floor((totalSeconds % 3600) / 60);
      const seconds = totalSeconds % 60;

      // Format as HH:MM:SS (24-hour format)
      const formattedTime = `${hours.toString().padStart(2, '0')}:${minutes
        .toString()
        .padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
      
      console.log('BotUptimeCard: formattedTime:', formattedTime);
      setUptime(formattedTime);
    };

    // Calculate initial uptime
    calculateUptime();

    // Update every second
    const interval = setInterval(calculateUptime, 1000);

    return () => clearInterval(interval);
  }, [botStatus?.is_running, loginStartTime]);

  return (
    <MetricCard
      title="Bot Uptime"
      value={uptime}
      icon={<Clock className="w-6 h-6 text-secondary-600" />}
    />
  );
};

export default BotUptimeCard;
