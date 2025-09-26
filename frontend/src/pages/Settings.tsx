import { motion } from 'framer-motion';
import { Moon, RotateCcw, Save, Sun } from 'lucide-react';
import React, { useState } from 'react';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import { useBotStore } from '../stores/botStore';

const Settings: React.FC = () => {
  const { theme, toggleTheme } = useBotStore();
  const [settings, setSettings] = useState({
    checkInterval: 0.5,
    resultsReportInterval: 5,
    rejectedReportInterval: 43200, // 12 hours
    quickCheckInterval: 10,
    enableQuickCheck: false,
    enableResultsReporting: true,
    enableRejectedReporting: true,
    maxAcceptPerRun: 5,
    jobTypeFilter: 'Telephone interpreting',
  });

  const handleSave = () => {
    // Save settings to backend
    console.log('Saving settings:', settings);
    // TODO: Implement API call to save settings
  };

  const handleReset = () => {
    setSettings({
      checkInterval: 0.5,
      resultsReportInterval: 5,
      rejectedReportInterval: 43200,
      quickCheckInterval: 10,
      enableQuickCheck: false,
      enableResultsReporting: true,
      enableRejectedReporting: true,
      maxAcceptPerRun: 5,
      jobTypeFilter: 'Telephone interpreting',
    });
  };

  const formatHours = (seconds: number) => {
    const hours = seconds / 3600;
    return hours >= 1 ? `${hours}h` : `${seconds}s`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-secondary-900 dark:text-white">
            Settings
          </h1>
          <p className="text-secondary-600 dark:text-secondary-400 mt-1">
            Configure bot behavior and preferences
          </p>
        </div>
        <div className="flex space-x-3">
          <Button
            variant="ghost"
            onClick={toggleTheme}
            className="flex items-center space-x-2"
          >
            {theme === 'dark' ? (
              <Sun className="w-4 h-4" />
            ) : (
              <Moon className="w-4 h-4" />
            )}
            <span>{theme === 'dark' ? 'Light' : 'Dark'} Mode</span>
          </Button>
        </div>
      </div>

      {/* Bot Configuration */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold text-secondary-900 dark:text-white mb-6">
          Bot Configuration
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Check Interval */}
          <div>
            <label className="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-2">
              Check Interval (seconds)
            </label>
            <input
              type="number"
              step="0.1"
              min="0.1"
              max="10"
              value={settings.checkInterval}
              onChange={(e) => setSettings({ ...settings, checkInterval: parseFloat(e.target.value) })}
              className="w-full px-3 py-2 border border-secondary-300 dark:border-secondary-600 rounded-lg bg-white dark:bg-secondary-800 text-secondary-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <p className="text-xs text-secondary-500 dark:text-secondary-400 mt-1">
              How often the bot checks for new jobs
            </p>
          </div>

          {/* Results Report Interval */}
          <div>
            <label className="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-2">
              Results Report Interval (seconds)
            </label>
            <input
              type="number"
              min="1"
              max="300"
              value={settings.resultsReportInterval}
              onChange={(e) => setSettings({ ...settings, resultsReportInterval: parseInt(e.target.value) })}
              className="w-full px-3 py-2 border border-secondary-300 dark:border-secondary-600 rounded-lg bg-white dark:bg-secondary-800 text-secondary-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <p className="text-xs text-secondary-500 dark:text-secondary-400 mt-1">
              How often to report accepted/rejected jobs
            </p>
          </div>

          {/* Rejected Report Interval */}
          <div>
            <label className="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-2">
              Rejected Report Interval
            </label>
            <input
              type="number"
              min="60"
              value={settings.rejectedReportInterval}
              onChange={(e) => setSettings({ ...settings, rejectedReportInterval: parseInt(e.target.value) })}
              className="w-full px-3 py-2 border border-secondary-300 dark:border-secondary-600 rounded-lg bg-white dark:bg-secondary-800 text-secondary-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <p className="text-xs text-secondary-500 dark:text-secondary-400 mt-1">
              Currently: {formatHours(settings.rejectedReportInterval)}
            </p>
          </div>

          {/* Quick Check Interval */}
          <div>
            <label className="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-2">
              Quick Check Interval (seconds)
            </label>
            <input
              type="number"
              min="5"
              max="300"
              value={settings.quickCheckInterval}
              onChange={(e) => setSettings({ ...settings, quickCheckInterval: parseInt(e.target.value) })}
              className="w-full px-3 py-2 border border-secondary-300 dark:border-secondary-600 rounded-lg bg-white dark:bg-secondary-800 text-secondary-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <p className="text-xs text-secondary-500 dark:text-secondary-400 mt-1">
              How often to perform quick job checks
            </p>
          </div>

          {/* Max Accept Per Run */}
          <div>
            <label className="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-2">
              Max Accept Per Run
            </label>
            <input
              type="number"
              min="1"
              max="50"
              value={settings.maxAcceptPerRun}
              onChange={(e) => setSettings({ ...settings, maxAcceptPerRun: parseInt(e.target.value) })}
              className="w-full px-3 py-2 border border-secondary-300 dark:border-secondary-600 rounded-lg bg-white dark:bg-secondary-800 text-secondary-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <p className="text-xs text-secondary-500 dark:text-secondary-400 mt-1">
              Maximum jobs to accept in a single run
            </p>
          </div>

          {/* Job Type Filter */}
          <div>
            <label className="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-2">
              Job Type Filter
            </label>
            <select
              value={settings.jobTypeFilter}
              onChange={(e) => setSettings({ ...settings, jobTypeFilter: e.target.value })}
              className="w-full px-3 py-2 border border-secondary-300 dark:border-secondary-600 rounded-lg bg-white dark:bg-secondary-800 text-secondary-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="Telephone interpreting">Telephone interpreting</option>
              <option value="Face-to-Face">Face-to-Face</option>
              <option value="Video interpreting">Video interpreting</option>
              <option value="Onsite">Onsite</option>
            </select>
            <p className="text-xs text-secondary-500 dark:text-secondary-400 mt-1">
              Type of jobs to accept
            </p>
          </div>
        </div>

        {/* Toggle Options */}
        <div className="mt-6 space-y-4">
          <h3 className="text-lg font-medium text-secondary-900 dark:text-white">
            Feature Toggles
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={settings.enableQuickCheck}
                onChange={(e) => setSettings({ ...settings, enableQuickCheck: e.target.checked })}
                className="w-4 h-4 text-primary-600 bg-secondary-100 border-secondary-300 rounded focus:ring-primary-500 dark:focus:ring-primary-600 dark:ring-offset-secondary-800 focus:ring-2 dark:bg-secondary-700 dark:border-secondary-600"
              />
              <span className="text-sm font-medium text-secondary-700 dark:text-secondary-300">
                Enable Quick Check
              </span>
            </label>

            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={settings.enableResultsReporting}
                onChange={(e) => setSettings({ ...settings, enableResultsReporting: e.target.checked })}
                className="w-4 h-4 text-primary-600 bg-secondary-100 border-secondary-300 rounded focus:ring-primary-500 dark:focus:ring-primary-600 dark:ring-offset-secondary-800 focus:ring-2 dark:bg-secondary-700 dark:border-secondary-600"
              />
              <span className="text-sm font-medium text-secondary-700 dark:text-secondary-300">
                Enable Results Reporting
              </span>
            </label>

            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={settings.enableRejectedReporting}
                onChange={(e) => setSettings({ ...settings, enableRejectedReporting: e.target.checked })}
                className="w-4 h-4 text-primary-600 bg-secondary-100 border-secondary-300 rounded focus:ring-primary-500 dark:focus:ring-primary-600 dark:ring-offset-secondary-800 focus:ring-2 dark:bg-secondary-700 dark:border-secondary-600"
              />
              <span className="text-sm font-medium text-secondary-700 dark:text-secondary-300">
                Enable Rejected Reporting
              </span>
            </label>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end space-x-3 mt-8">
          <Button
            variant="secondary"
            onClick={handleReset}
            className="flex items-center space-x-2"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Reset</span>
          </Button>
          <Button
            onClick={handleSave}
            className="flex items-center space-x-2"
          >
            <Save className="w-4 h-4" />
            <span>Save Settings</span>
          </Button>
        </div>
      </Card>
    </motion.div>
  );
};

export default Settings;
