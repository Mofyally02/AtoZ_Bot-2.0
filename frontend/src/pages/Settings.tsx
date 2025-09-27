import { Moon, RotateCcw, Save, Sun } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import { apiService } from '../services/api';
import { useBotStore } from '../stores/botStore';

const defaultSettings = {
  check_interval_seconds: 0.5,
  results_report_interval_seconds: 5,
  rejected_report_interval_seconds: 43200,
  quick_check_interval_seconds: 10,
  enable_quick_check: false,
  enable_results_reporting: true,
  enable_rejected_reporting: true,
  max_accept_per_run: 5,
  job_type_filter: 'Telephone interpreting',
};

const Settings: React.FC = () => {
  const { theme, toggleTheme } = useBotStore();
  const [settings, setSettings] = useState(defaultSettings);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setIsLoading(true);
    try {
      const config = await apiService.getBotConfiguration();
      setSettings(config);
    } catch (error) {
      console.error('Failed to load settings:', error);
      toast.error('Failed to load settings');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      await apiService.updateBotConfiguration(settings);
      toast.success('Settings saved successfully');
    } catch (error) {
      console.error('Failed to save settings:', error);
      toast.error('Failed to save settings');
    }
  };

  const handleReset = async () => {
    try {
      await apiService.updateBotConfiguration(defaultSettings);
      setSettings(defaultSettings);
      toast.success('Settings reset to default');
    } catch (error) {
      console.error('Failed to reset settings:', error);
      toast.error('Failed to reset settings');
    }
  };

  const updateSetting = (key: string, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const InputField = ({ label, type, key, value, onChange, min, max, step, description }: any) => (
    <div>
      <label className="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-2">
        {label}
      </label>
      <input
        type={type}
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(key, type === 'number' ? parseFloat(e.target.value) : e.target.value)}
        disabled={isLoading}
        className="w-full px-3 py-2 border border-secondary-300 dark:border-secondary-600 rounded-lg bg-white dark:bg-secondary-800 text-secondary-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
      />
      {description && (
        <p className="text-xs text-secondary-500 dark:text-secondary-400 mt-1">{description}</p>
      )}
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Settings</h1>
          <p className="text-muted-foreground mt-1">Configure bot behavior and preferences</p>
        </div>
        <Button variant="ghost" onClick={toggleTheme} className="flex items-center space-x-2">
          {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          <span>{theme === 'dark' ? 'Light' : 'Dark'} Mode</span>
        </Button>
      </div>

      {/* Bot Configuration */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold text-card-foreground mb-6">
          Bot Configuration
          {isLoading && (
            <div className="inline-flex items-center ml-3">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600"></div>
              <span className="ml-2 text-sm text-secondary-600 dark:text-secondary-400">Loading...</span>
            </div>
          )}
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <InputField
            label="Check Interval (seconds)"
            type="number"
            key="check_interval_seconds"
            value={settings.check_interval_seconds}
            onChange={updateSetting}
            min={0.1}
            max={10}
            step={0.1}
            description="How often the bot checks for new jobs"
          />

          <InputField
            label="Results Report Interval (seconds)"
            type="number"
            key="results_report_interval_seconds"
            value={settings.results_report_interval_seconds}
            onChange={updateSetting}
            min={1}
            max={300}
            description="How often to report accepted/rejected jobs"
          />

          <InputField
            label="Rejected Report Interval (seconds)"
            type="number"
            key="rejected_report_interval_seconds"
            value={settings.rejected_report_interval_seconds}
            onChange={updateSetting}
            min={60}
            description={`Currently: ${Math.round(settings.rejected_report_interval_seconds / 3600)}h`}
          />

          <InputField
            label="Quick Check Interval (seconds)"
            type="number"
            key="quick_check_interval_seconds"
            value={settings.quick_check_interval_seconds}
            onChange={updateSetting}
            min={5}
            max={300}
            description="How often to perform quick job checks"
          />

          <InputField
            label="Max Accept Per Run"
            type="number"
            key="max_accept_per_run"
            value={settings.max_accept_per_run}
            onChange={updateSetting}
            min={1}
            max={50}
            description="Maximum jobs to accept in a single run"
          />

          <div>
            <label className="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-2">
              Job Type Filter
            </label>
            <select
              value={settings.job_type_filter}
              onChange={(e) => updateSetting('job_type_filter', e.target.value)}
              disabled={isLoading}
              className="w-full px-3 py-2 border border-secondary-300 dark:border-secondary-600 rounded-lg bg-white dark:bg-secondary-800 text-secondary-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
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

        {/* Feature Toggles */}
        <div className="mt-6">
          <h3 className="text-lg font-medium text-secondary-900 dark:text-white mb-4">
            Feature Toggles
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { key: 'enable_quick_check', label: 'Enable Quick Check' },
              { key: 'enable_results_reporting', label: 'Enable Results Reporting' },
              { key: 'enable_rejected_reporting', label: 'Enable Rejected Reporting' }
            ].map(({ key, label }) => (
              <label key={key} className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  checked={settings[key as keyof typeof settings] as boolean}
                  onChange={(e) => updateSetting(key, e.target.checked)}
                  disabled={isLoading}
                  className="w-4 h-4 text-primary-600 bg-secondary-100 border-secondary-300 rounded focus:ring-primary-500 dark:focus:ring-primary-600 dark:ring-offset-secondary-800 focus:ring-2 dark:bg-secondary-700 dark:border-secondary-600 disabled:opacity-50 disabled:cursor-not-allowed"
                />
                <span className="text-sm font-medium text-secondary-700 dark:text-secondary-300">
                  {label}
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end space-x-3 mt-8">
          <Button variant="secondary" onClick={handleReset} disabled={isLoading}>
            <RotateCcw className="w-4 h-4 mr-2" />
            Reset
          </Button>
          <Button onClick={handleSave} disabled={isLoading}>
            <Save className="w-4 h-4 mr-2" />
            Save Settings
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default Settings;
