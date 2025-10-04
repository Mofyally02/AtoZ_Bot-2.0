import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Save, 
  RotateCcw, 
  Settings as SettingsIcon, 
  AlertCircle,
  Info,
  ToggleLeft,
  ToggleRight,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import toast from 'react-hot-toast';
import Button from '../ui/Button';
import Card from '../ui/Card';
import { apiService } from '../../services/api';
import { useBotStore } from '../../stores/botStore';

// Field type definitions
interface FieldDefinition {
  key: string;
  label: string;
  type: 'number' | 'boolean' | 'string' | 'select' | 'multiselect' | 'range' | 'text';
  description?: string;
  placeholder?: string;
  min?: number;
  max?: number;
  step?: number;
  options?: Array<{ value: string | number; label: string }>;
  validation?: {
    required?: boolean;
    min?: number;
    max?: number;
    pattern?: string;
    custom?: (value: any) => string | null;
  };
  category?: string;
  advanced?: boolean;
}

// Default field definitions based on current schema
const defaultFieldDefinitions: FieldDefinition[] = [
  {
    key: 'config_name',
    label: 'Configuration Name',
    type: 'string',
    description: 'Unique name for this configuration',
    placeholder: 'Enter configuration name',
    validation: { required: true }
  },
  {
    key: 'check_interval_seconds',
    label: 'Check Interval',
    type: 'range',
    description: 'Time between job checks in seconds',
    min: 1,
    max: 60,
    step: 1,
    category: 'Timing'
  },
  {
    key: 'results_report_interval_seconds',
    label: 'Results Report Interval',
    type: 'range',
    description: 'How often to report results',
    min: 1,
    max: 3600,
    step: 1,
    category: 'Timing'
  },
  {
    key: 'rejected_report_interval_seconds',
    label: 'Rejected Report Interval',
    type: 'range',
    description: 'How often to report rejected jobs',
    min: 60,
    max: 86400,
    step: 60,
    category: 'Timing'
  },
  {
    key: 'quick_check_interval_seconds',
    label: 'Quick Check Interval',
    type: 'range',
    description: 'Interval for quick job checks',
    min: 1,
    max: 300,
    step: 1,
    category: 'Timing'
  },
  {
    key: 'max_accept_per_run',
    label: 'Max Accept Per Run',
    type: 'range',
    description: 'Maximum jobs to accept per bot run',
    min: 1,
    max: 100,
    step: 1,
    category: 'Limits'
  },
  {
    key: 'job_type_filter',
    label: 'Job Type Filter',
    type: 'select',
    description: 'Type of jobs to look for',
    options: [
      { value: 'Telephone interpreting', label: 'Telephone interpreting' },
      { value: 'Video interpreting', label: 'Video interpreting' },
      { value: 'On-site interpreting', label: 'On-site interpreting' },
      { value: 'All types', label: 'All types' }
    ],
    category: 'Filters'
  },
  {
    key: 'enable_quick_check',
    label: 'Enable Quick Check',
    type: 'boolean',
    description: 'Enable quick job checking feature',
    category: 'Features'
  },
  {
    key: 'enable_results_reporting',
    label: 'Enable Results Reporting',
    type: 'boolean',
    description: 'Enable automatic results reporting',
    category: 'Features'
  },
  {
    key: 'enable_rejected_reporting',
    label: 'Enable Rejected Reporting',
    type: 'boolean',
    description: 'Enable rejected jobs reporting',
    category: 'Features'
  }
];

interface DynamicSettingsFormProps {
  onSave?: (config: any) => void;
  onReset?: () => void;
  showAdvanced?: boolean;
}

const DynamicSettingsForm: React.FC<DynamicSettingsFormProps> = ({
  onSave,
  onReset,
  showAdvanced = false
}) => {
  const { botStatus } = useBotStore();
  const [config, setConfig] = useState<any>({});
  const [fieldDefinitions] = useState<FieldDefinition[]>(defaultFieldDefinitions);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set(['Timing', 'Features']));
  const [showAdvancedFields, setShowAdvancedFields] = useState(showAdvanced);

  // Group fields by category
  const fieldsByCategory = fieldDefinitions.reduce((acc, field) => {
    const category = field.category || 'General';
    if (!acc[category]) acc[category] = [];
    acc[category].push(field);
    return acc;
  }, {} as Record<string, FieldDefinition[]>);

  useEffect(() => {
    loadConfiguration();
  }, []);

  const loadConfiguration = async () => {
    setIsLoading(true);
    try {
      const configData = await apiService.getBotConfiguration();
      setConfig(configData);
      console.log('Loaded configuration:', configData);
    } catch (error) {
      console.error('Failed to load configuration:', error);
      toast.error('Failed to load settings');
    } finally {
      setIsLoading(false);
    }
  };

  const validateField = (field: FieldDefinition, value: any): string | null => {
    if (field.validation?.required && (!value || value === '')) {
      return `${field.label} is required`;
    }

    if (field.validation?.min !== undefined && typeof value === 'number' && value < field.validation.min) {
      return `${field.label} must be at least ${field.validation.min}`;
    }

    if (field.validation?.max !== undefined && typeof value === 'number' && value > field.validation.max) {
      return `${field.label} must be at most ${field.validation.max}`;
    }

    if (field.validation?.pattern && typeof value === 'string' && !new RegExp(field.validation.pattern).test(value)) {
      return `${field.label} format is invalid`;
    }

    if (field.validation?.custom) {
      return field.validation.custom(value);
    }

    return null;
  };

  const updateField = (key: string, value: any) => {
    const field = fieldDefinitions.find(f => f.key === key);
    if (field) {
      const error = validateField(field, value);
    setErrors((prev: Record<string, string>) => ({
      ...prev,
      [key]: error || ''
    }));
    }

    setConfig((prev: any) => ({
      ...prev,
      [key]: value
    }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      // Validate all fields
      const newErrors: Record<string, string> = {};
      fieldDefinitions.forEach(field => {
        const error = validateField(field, config[field.key]);
        if (error) {
          newErrors[field.key] = error;
        }
      });

      if (Object.keys(newErrors).length > 0) {
        setErrors(newErrors);
        toast.error('Please fix validation errors before saving');
        return;
      }

      const savedConfig = await apiService.updateBotConfiguration(config);
      setConfig(savedConfig);
      setErrors({});
      toast.success('Settings saved successfully!');
      
      if (onSave) {
        onSave(savedConfig);
      }
    } catch (error) {
      console.error('Failed to save configuration:', error);
      toast.error('Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  const handleReset = async () => {
    try {
      const defaultConfig = await apiService.updateBotConfiguration({
        config_name: 'default',
        check_interval_seconds: 0.5,
        results_report_interval_seconds: 5,
        rejected_report_interval_seconds: 43200,
        quick_check_interval_seconds: 10,
        enable_quick_check: false,
        enable_results_reporting: true,
        enable_rejected_reporting: true,
        max_accept_per_run: 5,
        job_type_filter: 'Telephone interpreting'
      });
      
      setConfig(defaultConfig);
      setErrors({});
      toast.success('Settings reset to default');
      
      if (onReset) {
        onReset();
      }
    } catch (error) {
      console.error('Failed to reset configuration:', error);
      toast.error('Failed to reset settings');
    }
  };

  const toggleCategory = (category: string) => {
    setExpandedCategories(prev => {
      const newSet = new Set(prev);
      if (newSet.has(category)) {
        newSet.delete(category);
      } else {
        newSet.add(category);
      }
      return newSet;
    });
  };

  const renderField = (field: FieldDefinition) => {
    const value = config[field.key];
    const error = errors[field.key];

    const baseInputClasses = `
      w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500
      transition-colors duration-200
      ${error ? 'border-red-500 bg-red-50 dark:bg-red-900/20' : 'border-gray-300 dark:border-gray-600'}
      ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}
      bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
    `;

    switch (field.type) {
      case 'boolean':
        return (
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-3">
                {value ? (
                  <ToggleRight 
                    className="w-8 h-8 text-primary-600 cursor-pointer" 
                    onClick={() => !isLoading && updateField(field.key, !value)}
                  />
                ) : (
                  <ToggleLeft 
                    className="w-8 h-8 text-gray-400 cursor-pointer" 
                    onClick={() => !isLoading && updateField(field.key, !value)}
                  />
                )}
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  {field.label}
                </span>
              </div>
              {field.description && (
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 ml-11">
                  {field.description}
                </p>
              )}
            </div>
          </div>
        );

      case 'select':
        return (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {field.label}
            </label>
            <select
              value={value || ''}
              onChange={(e) => updateField(field.key, e.target.value)}
              disabled={isLoading}
              className={baseInputClasses}
            >
              {field.options?.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {field.description && (
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {field.description}
              </p>
            )}
          </div>
        );

      case 'range':
        return (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {field.label}: {value || field.min || 0}
              {field.key.includes('seconds') && ' seconds'}
              {field.key.includes('per_run') && ' jobs'}
            </label>
            <input
              type="range"
              min={field.min || 0}
              max={field.max || 100}
              step={field.step || 1}
              value={value || field.min || 0}
              onChange={(e) => updateField(field.key, parseFloat(e.target.value))}
              disabled={isLoading}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
            />
            <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
              <span>{field.min || 0}</span>
              <span>{field.max || 100}</span>
            </div>
            {field.description && (
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {field.description}
              </p>
            )}
          </div>
        );

      case 'number':
        return (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {field.label}
            </label>
            <input
              type="number"
              min={field.min}
              max={field.max}
              step={field.step}
              value={value || ''}
              onChange={(e) => updateField(field.key, parseFloat(e.target.value) || 0)}
              disabled={isLoading}
              placeholder={field.placeholder}
              className={baseInputClasses}
            />
            {field.description && (
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {field.description}
              </p>
            )}
          </div>
        );

      case 'text':
        return (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {field.label}
            </label>
            <textarea
              value={value || ''}
              onChange={(e) => updateField(field.key, e.target.value)}
              disabled={isLoading}
              placeholder={field.placeholder}
              rows={3}
              className={baseInputClasses}
            />
            {field.description && (
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {field.description}
              </p>
            )}
          </div>
        );

      default: // string
        return (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {field.label}
            </label>
            <input
              type="text"
              value={value || ''}
              onChange={(e) => updateField(field.key, e.target.value)}
              disabled={isLoading}
              placeholder={field.placeholder}
              className={baseInputClasses}
            />
            {field.description && (
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {field.description}
              </p>
            )}
          </div>
        );
    }
  };

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          <span className="ml-3 text-gray-600 dark:text-gray-400">Loading settings...</span>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <SettingsIcon className="w-6 h-6 text-primary-600" />
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Dynamic Bot Configuration
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Configure bot behavior with real-time validation
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowAdvancedFields(!showAdvancedFields)}
            className="px-3 py-1 text-xs font-medium rounded-md border border-gray-300 dark:border-gray-600 
                     hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            {showAdvancedFields ? 'Hide' : 'Show'} Advanced
          </button>
        </div>
      </div>

      {/* Configuration Sections */}
      <div className="space-y-4">
        {Object.entries(fieldsByCategory).map(([category, fields]) => {
          const isExpanded = expandedCategories.has(category);
          const visibleFields = showAdvancedFields ? fields : fields.filter(f => !f.advanced);

          if (visibleFields.length === 0) return null;

          return (
            <Card key={category} className="p-0 overflow-hidden">
              <button
                onClick={() => toggleCategory(category)}
                className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800 
                         transition-colors border-b border-gray-200 dark:border-gray-700"
              >
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 rounded-full bg-primary-600"></div>
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                    {category}
                  </h3>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    ({visibleFields.length} settings)
                  </span>
                </div>
                {isExpanded ? (
                  <ChevronUp className="w-5 h-5 text-gray-400" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-gray-400" />
                )}
              </button>

              <AnimatePresence>
                {isExpanded && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden"
                  >
                    <div className="p-6 space-y-6">
                      {visibleFields.map((field) => (
                        <div key={field.key}>
                          {renderField(field)}
                          {errors[field.key] && (
                            <div className="flex items-center space-x-2 mt-2 text-red-600 dark:text-red-400">
                              <AlertCircle className="w-4 h-4" />
                              <span className="text-sm">{errors[field.key]}</span>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </Card>
          );
        })}
      </div>

      {/* Action Buttons */}
      <Card className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {botStatus?.is_running && (
              <div className="flex items-center space-x-2 text-amber-600 dark:text-amber-400">
                <Info className="w-4 h-4" />
                <span className="text-sm">
                  Bot is currently running. Changes will apply to the next session.
                </span>
              </div>
            )}
          </div>

          <div className="flex items-center space-x-3">
            <Button
              variant="secondary"
              onClick={handleReset}
              disabled={isLoading || isSaving}
              className="flex items-center space-x-2"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Reset to Default</span>
            </Button>
            
            <Button
              onClick={handleSave}
              disabled={isLoading || isSaving || Object.values(errors).some(e => e)}
              loading={isSaving}
              className="flex items-center space-x-2"
            >
              <Save className="w-4 h-4" />
              <span>Save Configuration</span>
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default DynamicSettingsForm;
