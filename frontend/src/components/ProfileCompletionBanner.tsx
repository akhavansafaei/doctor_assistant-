import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import { AlertCircle, CheckCircle, X } from 'lucide-react';
import { HealthProfile } from '@/types';

export default function ProfileCompletionBanner() {
  const navigate = useNavigate();
  const { healthProfile } = useAuthStore();
  const [dismissed, setDismissed] = useState(false);
  const [completionData, setCompletionData] = useState({
    percentage: 0,
    missingFields: [] as string[],
    isComplete: false
  });

  useEffect(() => {
    if (healthProfile) {
      const result = calculateProfileCompletion(healthProfile);
      setCompletionData(result);

      // Auto-dismiss if profile is complete
      if (result.isComplete) {
        setDismissed(true);
      }
    }
  }, [healthProfile]);

  const calculateProfileCompletion = (profile: HealthProfile | null) => {
    if (!profile) {
      return {
        percentage: 0,
        missingFields: ['age', 'gender', 'chronic_conditions', 'allergies', 'height_cm', 'weight_kg'],
        isComplete: false
      };
    }

    const fields = [
      { key: 'age', weight: 15, label: 'Age' },
      { key: 'gender', weight: 10, label: 'Gender' },
      { key: 'height_cm', weight: 10, label: 'Height' },
      { key: 'weight_kg', weight: 10, label: 'Weight' },
      { key: 'blood_type', weight: 5, label: 'Blood Type' },
      { key: 'chronic_conditions', weight: 15, label: 'Chronic Conditions', isArray: true },
      { key: 'allergies', weight: 15, label: 'Allergies', isObject: true },
      { key: 'current_medications', weight: 10, label: 'Current Medications', isArray: true },
      { key: 'past_surgeries', weight: 5, label: 'Past Surgeries', isArray: true },
      { key: 'smoking_status', weight: 5, label: 'Smoking Status' }
    ];

    let totalWeight = 0;
    let completedWeight = 0;
    const missingFields: string[] = [];

    fields.forEach(field => {
      totalWeight += field.weight;
      const value = profile[field.key as keyof HealthProfile];

      let isComplete = false;
      if (field.isArray) {
        isComplete = Array.isArray(value) && value.length > 0;
      } else if (field.isObject) {
        isComplete = value !== null && value !== undefined && Object.keys(value).length > 0;
      } else {
        isComplete = value !== null && value !== undefined && value !== '';
      }

      if (isComplete) {
        completedWeight += field.weight;
      } else {
        missingFields.push(field.label);
      }
    });

    const percentage = Math.round((completedWeight / totalWeight) * 100);

    return {
      percentage,
      missingFields,
      isComplete: percentage >= 80 // Consider 80% as "complete enough"
    };
  };

  if (dismissed || !healthProfile) {
    return null;
  }

  const getStatusColor = () => {
    if (completionData.percentage >= 80) return 'green';
    if (completionData.percentage >= 50) return 'yellow';
    return 'red';
  };

  const statusColor = getStatusColor();

  const colorClasses = {
    green: {
      bg: 'bg-green-50',
      border: 'border-green-400',
      text: 'text-green-800',
      progressBg: 'bg-green-200',
      progressBar: 'bg-green-600',
      button: 'text-green-800 hover:text-green-900'
    },
    yellow: {
      bg: 'bg-yellow-50',
      border: 'border-yellow-400',
      text: 'text-yellow-800',
      progressBg: 'bg-yellow-200',
      progressBar: 'bg-yellow-600',
      button: 'text-yellow-800 hover:text-yellow-900'
    },
    red: {
      bg: 'bg-red-50',
      border: 'border-red-400',
      text: 'text-red-800',
      progressBg: 'bg-red-200',
      progressBar: 'bg-red-600',
      button: 'text-red-800 hover:text-red-900'
    }
  };

  const colors = colorClasses[statusColor];

  return (
    <div className={`${colors.bg} border-l-4 ${colors.border} p-4 mb-4 rounded-r-lg shadow-sm`}>
      <div className="flex items-start">
        <div className="flex-shrink-0">
          {completionData.isComplete ? (
            <CheckCircle className={`w-5 h-5 ${colors.text}`} />
          ) : (
            <AlertCircle className={`w-5 h-5 ${colors.text}`} />
          )}
        </div>

        <div className="ml-3 flex-1">
          <h3 className={`text-sm font-medium ${colors.text}`}>
            {completionData.isComplete
              ? 'Health profile complete!'
              : 'Complete your health profile for personalized advice'}
          </h3>

          <div className="mt-2">
            <div className={`${colors.progressBg} rounded-full h-2 overflow-hidden`}>
              <div
                className={`${colors.progressBar} h-2 rounded-full transition-all duration-500 ease-out`}
                style={{ width: `${completionData.percentage}%` }}
              />
            </div>
            <p className={`text-xs ${colors.text} mt-1 font-medium`}>
              {completionData.percentage}% complete
            </p>
          </div>

          {!completionData.isComplete && completionData.missingFields.length > 0 && (
            <div className="mt-2">
              <p className={`text-xs ${colors.text}`}>
                Missing: {completionData.missingFields.slice(0, 3).join(', ')}
                {completionData.missingFields.length > 3 && ` and ${completionData.missingFields.length - 3} more`}
              </p>
            </div>
          )}

          {completionData.isComplete && (
            <p className={`text-xs ${colors.text} mt-2`}>
              Your profile is helping provide you with personalized medical advice.
            </p>
          )}
        </div>

        <div className="ml-4 flex items-center gap-2">
          {!completionData.isComplete && (
            <button
              onClick={() => navigate('/profile')}
              className={`text-sm font-medium ${colors.button} hover:underline whitespace-nowrap`}
            >
              Complete Now →
            </button>
          )}

          <button
            onClick={() => setDismissed(true)}
            className={`${colors.text} hover:opacity-70`}
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
