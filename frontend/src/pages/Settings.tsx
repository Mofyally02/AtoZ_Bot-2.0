import { Moon, Sun, Settings as SettingsIcon, Monitor, Smartphone, Tablet } from 'lucide-react';
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import { useBotStore } from '../stores/botStore';
import DynamicSettingsForm from '../components/settings/DynamicSettingsForm';
import ConfigurationPresets from '../components/settings/ConfigurationPresets';
import { SettingsProvider, useSettings } from '../components/settings/SettingsStore';

const Settings: React.FC = () => {
  return (
    <SettingsProvider>
      <SettingsContent />
    </SettingsProvider>
  );
};

const SettingsContent: React.FC = () => {
  const { theme, toggleTheme } = useBotStore();
  const { state: settingsState, actions } = useSettings();
  const [activeTab, setActiveTab] = useState<'form' | 'presets'>('form');
  const [deviceView, setDeviceView] = useState<'desktop' | 'tablet' | 'mobile'>('desktop');

  const handlePresetSelect = async (config: any) => {
    try {
      await actions.updateConfiguration(config);
      // Refresh the settings to show the updated configuration
      await actions.refreshSettings();
    } catch (error) {
      console.error('Failed to apply preset:', error);
      throw error; // Re-throw to let the preset component handle the error
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold text-foreground">Settings</h1>
          <p className="text-muted-foreground">
            Configure bot behavior with dynamic, responsive controls
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          {/* Device View Toggle */}
          <div className="flex items-center space-x-2 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
            <button
              onClick={() => setDeviceView('desktop')}
              className={`p-2 rounded-md transition-colors ${
                deviceView === 'desktop' 
                  ? 'bg-white dark:bg-gray-700 text-primary-600 shadow-sm' 
                  : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
              title="Desktop View"
            >
              <Monitor className="w-4 h-4" />
            </button>
            <button
              onClick={() => setDeviceView('tablet')}
              className={`p-2 rounded-md transition-colors ${
                deviceView === 'tablet' 
                  ? 'bg-white dark:bg-gray-700 text-primary-600 shadow-sm' 
                  : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
              title="Tablet View"
            >
              <Tablet className="w-4 h-4" />
            </button>
            <button
              onClick={() => setDeviceView('mobile')}
              className={`p-2 rounded-md transition-colors ${
                deviceView === 'mobile' 
                  ? 'bg-white dark:bg-gray-700 text-primary-600 shadow-sm' 
                  : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
              title="Mobile View"
            >
              <Smartphone className="w-4 h-4" />
            </button>
          </div>

          {/* Theme Toggle */}
          <Button variant="ghost" onClick={toggleTheme} className="flex items-center space-x-2">
            {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            <span>{theme === 'dark' ? 'Light' : 'Dark'} Mode</span>
          </Button>
        </div>
      </motion.div>

      {/* Tab Navigation */}
      <motion.div variants={itemVariants}>
        <Card className="p-0 overflow-hidden">
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="flex space-x-8 px-6">
              <button
                onClick={() => setActiveTab('form')}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'form'
                    ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                <SettingsIcon className="w-4 h-4 inline mr-2" />
                Dynamic Configuration
              </button>
              <button
                onClick={() => setActiveTab('presets')}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'presets'
                    ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                Configuration Presets
              </button>
            </nav>
          </div>
        </Card>
      </motion.div>

      {/* Tab Content */}
      <motion.div variants={itemVariants}>
        {activeTab === 'form' ? (
          <DynamicSettingsForm
            onSave={(config) => {
              console.log('Configuration saved:', config);
            }}
            onReset={() => {
              console.log('Configuration reset');
            }}
            showAdvanced={false}
          />
        ) : (
          <ConfigurationPresets
            onPresetSelect={handlePresetSelect}
            currentConfig={settingsState.activeConfiguration}
            isLoading={settingsState.isLoading}
          />
        )}
      </motion.div>

      {/* Responsive Preview */}
      <motion.div variants={itemVariants}>
        <Card className="p-4 bg-gray-50 dark:bg-gray-800/50">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white">
                Responsive Preview
              </h4>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Current view: {deviceView} - Settings adapt automatically to screen size
              </p>
            </div>
            <div className="text-xs text-gray-400">
              {deviceView === 'desktop' && '≥ 1024px'}
              {deviceView === 'tablet' && '768px - 1023px'}
              {deviceView === 'mobile' && '< 768px'}
            </div>
          </div>
        </Card>
      </motion.div>
    </motion.div>
  );
};

export default Settings;