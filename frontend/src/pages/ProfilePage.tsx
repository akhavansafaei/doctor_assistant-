import { useState, useEffect } from 'react';
import { useAuthStore } from '@/stores/authStore';
import { HealthProfile } from '@/types';
import toast from 'react-hot-toast';
import { User, Dumbbell, Target, Calendar, Utensils, AlertCircle } from 'lucide-react';

export default function ProfilePage() {
  const { healthProfile, updateHealthProfile, user } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<Partial<HealthProfile>>({
    age: undefined,
    gender: '',
    height_cm: undefined,
    weight_kg: undefined,
    blood_type: '',
    // Fitness-specific fields
    fitness_level: '',
    training_experience: '',
    fitness_goals: [],
    available_equipment: [],
    training_days_per_week: undefined,
    training_duration_minutes: undefined,
    current_injuries: [],
    health_conditions: [],
    diet_preference: '',
    dietary_restrictions: [],
    food_allergies: [],
    exercise_frequency: '',
    body_fat_percentage: undefined,
    body_measurements: {},
    emergency_contact: {
      name: '',
      relationship: '',
      phone: ''
    }
  });

  // Tag inputs state for fitness
  const [fitnessGoalInput, setFitnessGoalInput] = useState('');
  const [equipmentInput, setEquipmentInput] = useState('');
  const [injuryInput, setInjuryInput] = useState('');
  const [healthConditionInput, setHealthConditionInput] = useState('');
  const [dietaryRestrictionInput, setDietaryRestrictionInput] = useState('');
  const [foodAllergyInput, setFoodAllergyInput] = useState('');

  useEffect(() => {
    if (healthProfile) {
      setFormData(healthProfile);
    }
  }, [healthProfile]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await updateHealthProfile(formData);
      toast.success('Fitness profile updated successfully!');
    } catch (error) {
      toast.error('Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  // Fitness Goals handlers
  const addFitnessGoal = () => {
    if (fitnessGoalInput.trim()) {
      setFormData({
        ...formData,
        fitness_goals: [...(formData.fitness_goals || []), fitnessGoalInput.trim()]
      });
      setFitnessGoalInput('');
    }
  };

  const removeFitnessGoal = (index: number) => {
    setFormData({
      ...formData,
      fitness_goals: formData.fitness_goals?.filter((_, i) => i !== index)
    });
  };

  // Equipment handlers
  const addEquipment = () => {
    if (equipmentInput.trim()) {
      setFormData({
        ...formData,
        available_equipment: [...(formData.available_equipment || []), equipmentInput.trim()]
      });
      setEquipmentInput('');
    }
  };

  const removeEquipment = (index: number) => {
    setFormData({
      ...formData,
      available_equipment: formData.available_equipment?.filter((_, i) => i !== index)
    });
  };

  // Injury handlers
  const addInjury = () => {
    if (injuryInput.trim()) {
      setFormData({
        ...formData,
        current_injuries: [...(formData.current_injuries || []), injuryInput.trim()]
      });
      setInjuryInput('');
    }
  };

  const removeInjury = (index: number) => {
    setFormData({
      ...formData,
      current_injuries: formData.current_injuries?.filter((_, i) => i !== index)
    });
  };

  // Health Condition handlers
  const addHealthCondition = () => {
    if (healthConditionInput.trim()) {
      setFormData({
        ...formData,
        health_conditions: [...(formData.health_conditions || []), healthConditionInput.trim()]
      });
      setHealthConditionInput('');
    }
  };

  const removeHealthCondition = (index: number) => {
    setFormData({
      ...formData,
      health_conditions: formData.health_conditions?.filter((_, i) => i !== index)
    });
  };

  // Dietary Restriction handlers
  const addDietaryRestriction = () => {
    if (dietaryRestrictionInput.trim()) {
      setFormData({
        ...formData,
        dietary_restrictions: [...(formData.dietary_restrictions || []), dietaryRestrictionInput.trim()]
      });
      setDietaryRestrictionInput('');
    }
  };

  const removeDietaryRestriction = (index: number) => {
    setFormData({
      ...formData,
      dietary_restrictions: formData.dietary_restrictions?.filter((_, i) => i !== index)
    });
  };

  // Food Allergy handlers
  const addFoodAllergy = () => {
    if (foodAllergyInput.trim()) {
      setFormData({
        ...formData,
        food_allergies: [...(formData.food_allergies || []), foodAllergyInput.trim()]
      });
      setFoodAllergyInput('');
    }
  };

  const removeFoodAllergy = (index: number) => {
    setFormData({
      ...formData,
      food_allergies: formData.food_allergies?.filter((_, i) => i !== index)
    });
  };

  const calculateBMI = () => {
    if (formData.height_cm && formData.weight_kg) {
      const heightInMeters = formData.height_cm / 100;
      return (formData.weight_kg / (heightInMeters * heightInMeters)).toFixed(1);
    }
    return null;
  };

  const bmi = calculateBMI();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-5xl mx-auto px-6 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Fitness Profile</h1>
          <p className="text-gray-600 mt-2">
            Keep your fitness information up to date for personalized workout plans and nutrition guidance
          </p>
        </div>
      </div>

      {/* Profile Form */}
      <div className="max-w-5xl mx-auto px-6 py-8">
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Basic Information */}
          <section className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                <User className="w-5 h-5 text-primary-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">Basic Information</h2>
                <p className="text-sm text-gray-600">Your fundamental physical metrics</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Age *
                </label>
                <input
                  type="number"
                  value={formData.age || ''}
                  onChange={(e) => setFormData({ ...formData, age: parseInt(e.target.value) })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="e.g., 28"
                  min="0"
                  max="120"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Gender *
                </label>
                <select
                  value={formData.gender || ''}
                  onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  required
                >
                  <option value="">Select gender</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                  <option value="prefer_not_to_say">Prefer not to say</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Height (cm)
                </label>
                <input
                  type="number"
                  value={formData.height_cm || ''}
                  onChange={(e) => setFormData({ ...formData, height_cm: parseFloat(e.target.value) })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="e.g., 180"
                  min="50"
                  max="250"
                  step="0.1"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Weight (kg)
                </label>
                <input
                  type="number"
                  value={formData.weight_kg || ''}
                  onChange={(e) => setFormData({ ...formData, weight_kg: parseFloat(e.target.value) })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="e.g., 75"
                  min="20"
                  max="300"
                  step="0.1"
                />
              </div>

              {bmi && (
                <div className="col-span-2">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">
                      Your BMI: <span className="font-semibold text-gray-900">{bmi}</span>
                    </p>
                  </div>
                </div>
              )}
            </div>
          </section>

          {/* Fitness Goals & Experience */}
          <section className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <Target className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">Fitness Goals & Experience</h2>
                <p className="text-sm text-gray-600">What you want to achieve and your experience level</p>
              </div>
            </div>

            <div className="space-y-6">
              {/* Fitness Level */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Fitness Level
                </label>
                <select
                  value={formData.fitness_level || ''}
                  onChange={(e) => setFormData({ ...formData, fitness_level: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="">Select your fitness level</option>
                  <option value="beginner">Beginner (0-1 year)</option>
                  <option value="intermediate">Intermediate (1-3 years)</option>
                  <option value="advanced">Advanced (3+ years)</option>
                </select>
              </div>

              {/* Training Experience */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Training Experience
                </label>
                <input
                  type="text"
                  value={formData.training_experience || ''}
                  onChange={(e) => setFormData({ ...formData, training_experience: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="e.g., 2 years, 6 months"
                />
              </div>

              {/* Fitness Goals */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Fitness Goals
                </label>
                <div className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={fitnessGoalInput}
                    onChange={(e) => setFitnessGoalInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addFitnessGoal())}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="e.g., muscle gain, fat loss, strength"
                  />
                  <button
                    type="button"
                    onClick={addFitnessGoal}
                    className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                  >
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.fitness_goals?.map((goal, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
                    >
                      {goal}
                      <button
                        type="button"
                        onClick={() => removeFitnessGoal(index)}
                        className="hover:text-blue-900"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Common goals: muscle gain, fat loss, strength building, athletic performance, general fitness
                </p>
              </div>
            </div>
          </section>

          {/* Training Schedule */}
          <section className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <Calendar className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">Training Schedule</h2>
                <p className="text-sm text-gray-600">How often and how long you can train</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Training Days Per Week
                </label>
                <input
                  type="number"
                  value={formData.training_days_per_week || ''}
                  onChange={(e) => setFormData({ ...formData, training_days_per_week: parseInt(e.target.value) })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="e.g., 4"
                  min="1"
                  max="7"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Training Duration (minutes/session)
                </label>
                <input
                  type="number"
                  value={formData.training_duration_minutes || ''}
                  onChange={(e) => setFormData({ ...formData, training_duration_minutes: parseInt(e.target.value) })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="e.g., 60"
                  min="15"
                  max="240"
                  step="15"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Current Activity Level
                </label>
                <select
                  value={formData.exercise_frequency || ''}
                  onChange={(e) => setFormData({ ...formData, exercise_frequency: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="">Select activity level</option>
                  <option value="sedentary">Sedentary (little or no exercise)</option>
                  <option value="lightly_active">Lightly Active (1-2 days/week)</option>
                  <option value="moderately_active">Moderately Active (3-4 days/week)</option>
                  <option value="very_active">Very Active (5-6 days/week)</option>
                  <option value="extremely_active">Extremely Active (daily intense training)</option>
                </select>
              </div>
            </div>
          </section>

          {/* Available Equipment */}
          <section className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <Dumbbell className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">Available Equipment</h2>
                <p className="text-sm text-gray-600">What equipment you have access to</p>
              </div>
            </div>

            <div>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={equipmentInput}
                  onChange={(e) => setEquipmentInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addEquipment())}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="e.g., dumbbells, barbell, pull-up bar"
                />
                <button
                  type="button"
                  onClick={addEquipment}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                >
                  Add
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {formData.available_equipment?.map((equipment, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center gap-1 px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm"
                  >
                    {equipment}
                    <button
                      type="button"
                      onClick={() => removeEquipment(index)}
                      className="hover:text-purple-900"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Examples: full gym, dumbbells, barbells, resistance bands, pull-up bar, bodyweight only
              </p>
            </div>
          </section>

          {/* Injuries & Health Conditions */}
          <section className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                <AlertCircle className="w-5 h-5 text-red-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">Injuries & Health Conditions</h2>
                <p className="text-sm text-gray-600">Any injuries or health issues to consider</p>
              </div>
            </div>

            <div className="space-y-6">
              {/* Current Injuries */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Current Injuries
                </label>
                <div className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={injuryInput}
                    onChange={(e) => setInjuryInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addInjury())}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="e.g., knee pain, shoulder strain"
                  />
                  <button
                    type="button"
                    onClick={addInjury}
                    className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                  >
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.current_injuries?.map((injury, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center gap-1 px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm"
                    >
                      {injury}
                      <button
                        type="button"
                        onClick={() => removeInjury(index)}
                        className="hover:text-red-900"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              {/* Health Conditions */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Health Conditions
                </label>
                <div className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={healthConditionInput}
                    onChange={(e) => setHealthConditionInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addHealthCondition())}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="e.g., high blood pressure, asthma"
                  />
                  <button
                    type="button"
                    onClick={addHealthCondition}
                    className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                  >
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.health_conditions?.map((condition, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center gap-1 px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-sm"
                    >
                      {condition}
                      <button
                        type="button"
                        onClick={() => removeHealthCondition(index)}
                        className="hover:text-orange-900"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </section>

          {/* Diet & Nutrition */}
          <section className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
                <Utensils className="w-5 h-5 text-yellow-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">Diet & Nutrition Preferences</h2>
                <p className="text-sm text-gray-600">Your dietary preferences and restrictions</p>
              </div>
            </div>

            <div className="space-y-6">
              {/* Diet Preference */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Diet Preference
                </label>
                <select
                  value={formData.diet_preference || ''}
                  onChange={(e) => setFormData({ ...formData, diet_preference: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="">Select diet preference</option>
                  <option value="persian_cuisine">Persian Cuisine</option>
                  <option value="flexible">Flexible</option>
                  <option value="mediterranean">Mediterranean</option>
                  <option value="other">Other</option>
                </select>
              </div>

              {/* Dietary Restrictions */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Dietary Restrictions
                </label>
                <div className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={dietaryRestrictionInput}
                    onChange={(e) => setDietaryRestrictionInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addDietaryRestriction())}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="e.g., vegetarian, halal, gluten-free"
                  />
                  <button
                    type="button"
                    onClick={addDietaryRestriction}
                    className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                  >
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.dietary_restrictions?.map((restriction, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center gap-1 px-3 py-1 bg-yellow-100 text-yellow-700 rounded-full text-sm"
                    >
                      {restriction}
                      <button
                        type="button"
                        onClick={() => removeDietaryRestriction(index)}
                        className="hover:text-yellow-900"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              {/* Food Allergies */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Food Allergies
                </label>
                <div className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={foodAllergyInput}
                    onChange={(e) => setFoodAllergyInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addFoodAllergy())}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="e.g., peanuts, dairy, shellfish"
                  />
                  <button
                    type="button"
                    onClick={addFoodAllergy}
                    className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                  >
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.food_allergies?.map((allergy, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center gap-1 px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm"
                    >
                      {allergy}
                      <button
                        type="button"
                        onClick={() => removeFoodAllergy(index)}
                        className="hover:text-red-900"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </section>

          {/* Body Composition (Optional) */}
          <section className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
                <User className="w-5 h-5 text-indigo-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">Body Composition (Optional)</h2>
                <p className="text-sm text-gray-600">Track your body composition metrics</p>
              </div>
            </div>

            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Body Fat Percentage (%)
                </label>
                <input
                  type="number"
                  value={formData.body_fat_percentage || ''}
                  onChange={(e) => setFormData({ ...formData, body_fat_percentage: parseFloat(e.target.value) })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="e.g., 15.5"
                  min="3"
                  max="50"
                  step="0.1"
                />
                <p className="text-xs text-gray-500 mt-1">
                  You can get this measured via DEXA scan, calipers, or bioelectrical impedance
                </p>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm font-medium text-gray-700 mb-2">Body Measurements (cm)</p>
                <div className="grid grid-cols-2 gap-4">
                  <input
                    type="number"
                    placeholder="Chest"
                    value={formData.body_measurements?.chest || ''}
                    onChange={(e) => setFormData({
                      ...formData,
                      body_measurements: { ...formData.body_measurements, chest: parseFloat(e.target.value) }
                    })}
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    step="0.1"
                  />
                  <input
                    type="number"
                    placeholder="Waist"
                    value={formData.body_measurements?.waist || ''}
                    onChange={(e) => setFormData({
                      ...formData,
                      body_measurements: { ...formData.body_measurements, waist: parseFloat(e.target.value) }
                    })}
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    step="0.1"
                  />
                  <input
                    type="number"
                    placeholder="Hips"
                    value={formData.body_measurements?.hips || ''}
                    onChange={(e) => setFormData({
                      ...formData,
                      body_measurements: { ...formData.body_measurements, hips: parseFloat(e.target.value) }
                    })}
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    step="0.1"
                  />
                  <input
                    type="number"
                    placeholder="Arms"
                    value={formData.body_measurements?.arms || ''}
                    onChange={(e) => setFormData({
                      ...formData,
                      body_measurements: { ...formData.body_measurements, arms: parseFloat(e.target.value) }
                    })}
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    step="0.1"
                  />
                </div>
              </div>
            </div>
          </section>

          {/* Submit Button */}
          <div className="flex justify-end gap-4">
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {loading ? 'Saving...' : 'Save Fitness Profile'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
