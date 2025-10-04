import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Zap, 
  Clock, 
  Target, 
  Shield, 
  Plus, 
  Save, 
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import toast from 'react-hot-toast';
import Button from '../ui/Button';
import Card from '../ui/Card';

// Preset configurations
const configurationPresets = [
  {
    id: 'aggressive',
    name: 'Aggressive Mode',
    description: 'Fast checking with maximum job acceptance',
    icon: Zap,
    color: 'text-red-600',
    bgColor: 'bg-red-50 dark:bg-red-900/20',
    config: {
      config_name: 'Aggressive Mode',
      check_interval_seconds: 2,
      results_report_interval_seconds: 3,
      rejected_report_interval_seconds: 3600,
      quick_check_interval_seconds: 5,
      enable_quick_check: true,
      enable_results_reporting: true,
      enable_rejected_reporting: false,
      max_accept_per_run: 20,
      job_type_filter: 'All types'
    }
  },
  {
    id: 'balanced',
    name: 'Balanced Mode',
    description: 'Optimal balance between speed and efficiency',
    icon: Target,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 dark:bg-blue-900/20',
    config: {
      config_name: 'Balanced Mode',
      check_interval_seconds: 10,
      results_report_interval_seconds: 5,
      rejected_report_interval_seconds: 43200,
      quick_check_interval_seconds: 10,
      enable_quick_check: true,
      enable_results_reporting: true,
      enable_rejected_reporting: true,
      max_accept_per_run: 5,
      job_type_filter: 'Telephone interpreting'
    }
  },
  {
    id: 'conservative',
    name: 'Conservative Mode',
    description: 'Careful checking with selective job acceptance',
    icon: Shield,
    color: 'text-green-600',
    bgColor: 'bg-green-50 dark:bg-green-900/20',
    config: {
      config_name: 'Conservative Mode',
      check_interval_seconds: 30,
      results_report_interval_seconds: 10,
      rejected_report_interval_seconds: 86400,
      quick_check_interval_seconds: 30,
      enable_quick_check: false,
      enable_results_reporting: true,
      enable_rejected_reporting: true,
      max_accept_per_run: 2,
      job_type_filter: 'Telephone interpreting'
    }
  },
  {
    id: 'monitoring',
    name: 'Monitoring Mode',
    description: 'Slow checking for monitoring and analysis',
    icon: Clock,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50 dark:bg-purple-900/20',
    config: {
      config_name: 'Monitoring Mode',
      check_interval_seconds: 60,
      results_report_interval_seconds: 30,
      rejected_report_interval_seconds: 86400,
      quick_check_interval_seconds: 60,
      enable_quick_check: false,
      enable_results_reporting: true,
      enable_rejected_reporting: true,
      max_accept_per_run: 1,
      job_type_filter: 'All types'
    }
  }
];

interface ConfigurationPresetsProps {
  onPresetSelect: (config: any) => void;
  currentConfig?: any;
  isLoading?: boolean;
}

const ConfigurationPresets: React.FC<ConfigurationPresetsProps> = ({
  onPresetSelect,
  currentConfig,
  isLoading = false
}) => {
  const [selectedPreset, setSelectedPreset] = useState<string | null>(null);
  const [showCustomPreset, setShowCustomPreset] = useState(false);
  const [customPresetName, setCustomPresetName] = useState('');
  const [customPresetDescription, setCustomPresetDescription] = useState('');

  const handlePresetSelect = async (preset: typeof configurationPresets[0]) => {
    setSelectedPreset(preset.id);
    
    // Apply the preset configuration immediately
    try {
      await onPresetSelect(preset.config);
      
      // Show success message
      toast.success(`Applied ${preset.name} configuration successfully!`);
      
      // If bot is running, show restart notice
      if (currentConfig && currentConfig.is_running) {
        toast('Bot restart required for new settings to take effect', {
          duration: 5000,
          icon: 'ℹ️',
        });
      }
    } catch (error) {
      console.error('Failed to apply preset:', error);
      toast.error(`Failed to apply ${preset.name} configuration`);
    }
  };

  const handleSaveCustomPreset = () => {
    if (!customPresetName.trim()) return;

    const customPreset = {
      config_name: customPresetName,
      check_interval_seconds: currentConfig?.check_interval_seconds || 0.5,
      results_report_interval_seconds: currentConfig?.results_report_interval_seconds || 5,
      rejected_report_interval_seconds: currentConfig?.rejected_report_interval_seconds || 43200,
      quick_check_interval_seconds: currentConfig?.quick_check_interval_seconds || 10,
      enable_quick_check: currentConfig?.enable_quick_check || false,
      enable_results_reporting: currentConfig?.enable_results_reporting || true,
      enable_rejected_reporting: currentConfig?.enable_rejected_reporting || true,
      max_accept_per_run: currentConfig?.max_accept_per_run || 5,
      job_type_filter: currentConfig?.job_type_filter || 'Telephone interpreting'
    };

    onPresetSelect(customPreset);
    setShowCustomPreset(false);
    setCustomPresetName('');
    setCustomPresetDescription('');
  };

  const isCurrentConfigPreset = (preset: typeof configurationPresets[0]) => {
    if (!currentConfig) return false;
    
    return Object.keys(preset.config).every(key => {
      if (key === 'config_name') return true; // Skip name comparison
      return currentConfig[key as keyof typeof currentConfig] === preset.config[key as keyof typeof preset.config];
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          Configuration Presets
        </h3>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Choose from predefined configurations or save your current settings as a preset
        </p>
      </div>

      {/* Preset Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {configurationPresets.map((preset) => {
          const Icon = preset.icon;
          const isCurrent = isCurrentConfigPreset(preset);
          const isSelected = selectedPreset === preset.id;

          return (
            <motion.div
              key={preset.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <div 
                className={`
                  p-4 cursor-pointer transition-all duration-200 rounded-lg border border-gray-200 dark:border-gray-700
                  ${isSelected ? 'ring-2 ring-primary-500 bg-primary-50 dark:bg-primary-900/20' : ''}
                  ${isCurrent ? 'border-green-500 bg-green-50 dark:bg-green-900/20' : ''}
                  hover:shadow-md bg-white dark:bg-gray-800
                `}
                onClick={() => !isLoading && handlePresetSelect(preset)}
              >
                <div className="flex items-start space-x-3">
                  <div className={`
                    p-2 rounded-lg ${preset.bgColor}
                  `}>
                    <Icon className={`w-5 h-5 ${preset.color}`} />
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <h4 className="font-medium text-gray-900 dark:text-white">
                        {preset.name}
                      </h4>
                      {isCurrent && (
                        <CheckCircle className="w-4 h-4 text-green-600" />
                      )}
                    </div>
                    
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                      {preset.description}
                    </p>

                    {/* Configuration Summary */}
                    <div className="mt-3 space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-500 dark:text-gray-400">Check Interval:</span>
                        <span className="text-gray-900 dark:text-white">
                          {preset.config.check_interval_seconds}s
                        </span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-500 dark:text-gray-400">Max Accept:</span>
                        <span className="text-gray-900 dark:text-white">
                          {preset.config.max_accept_per_run} jobs
                        </span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-500 dark:text-gray-400">Job Type:</span>
                        <span className="text-gray-900 dark:text-white">
                          {preset.config.job_type_filter}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {isCurrent && (
                  <div className="mt-3 pt-3 border-t border-green-200 dark:border-green-800">
                    <div className="flex items-center space-x-2 text-green-600 dark:text-green-400">
                      <CheckCircle className="w-4 h-4" />
                      <span className="text-sm font-medium">Currently Active</span>
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Custom Preset */}
      <Card className="p-4">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="font-medium text-gray-900 dark:text-white">
              Save Current Configuration
            </h4>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Save your current settings as a custom preset
            </p>
          </div>
          
          <Button
            variant="secondary"
            onClick={() => setShowCustomPreset(!showCustomPreset)}
            disabled={isLoading}
            className="flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Save Preset</span>
          </Button>
        </div>

        <AnimatePresence>
          {showCustomPreset && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden"
            >
              <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Preset Name
                  </label>
                  <input
                    type="text"
                    value={customPresetName}
                    onChange={(e) => setCustomPresetName(e.target.value)}
                    placeholder="Enter preset name"
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
                             focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                             bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Description (optional)
                  </label>
                  <textarea
                    value={customPresetDescription}
                    onChange={(e) => setCustomPresetDescription(e.target.value)}
                    placeholder="Enter description"
                    rows={2}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
                             focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                             bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                  />
                </div>

                <div className="flex items-center space-x-3">
                  <Button
                    onClick={handleSaveCustomPreset}
                    disabled={!customPresetName.trim() || isLoading}
                    className="flex items-center space-x-2"
                  >
                    <Save className="w-4 h-4" />
                    <span>Save Preset</span>
                  </Button>
                  
                  <Button
                    variant="secondary"
                    onClick={() => {
                      setShowCustomPreset(false);
                      setCustomPresetName('');
                      setCustomPresetDescription('');
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </Card>

      {/* Current Configuration Info */}
      {currentConfig && (
        <Card className="p-4 bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
            <div>
              <h4 className="font-medium text-blue-900 dark:text-blue-100">
                Current Configuration
              </h4>
              <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                {currentConfig.config_name || 'Custom Configuration'}
              </p>
              <div className="mt-2 text-xs text-blue-600 dark:text-blue-400">
                <div>Check Interval: {currentConfig.check_interval_seconds}s</div>
                <div>Max Accept: {currentConfig.max_accept_per_run} jobs</div>
                <div>Job Type: {currentConfig.job_type_filter}</div>
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};

export default ConfigurationPresets;
