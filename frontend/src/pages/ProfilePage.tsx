import { useState, useEffect } from 'react';
import { useAuthStore } from '@/stores/authStore';
import { HealthProfile } from '@/types';
import toast from 'react-hot-toast';
import { User, Heart, Pill, AlertCircle, Activity, Users } from 'lucide-react';

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
    body_fat_percentage: undefined,
    body_measurements: {},
    // Legacy fields
    chronic_conditions: [],
    allergies: {
      drug: [],
      food: [],
      environmental: []
    },
    current_medications: [],
    past_surgeries: [],
    smoking_status: '',
    alcohol_consumption: '',
    exercise_frequency: '',
    emergency_contact: {
      name: '',
      relationship: '',
      phone: ''
    }
  });

  // Tag inputs state
  const [chronicConditionInput, setChronicConditionInput] = useState('');
  const [drugAllergyInput, setDrugAllergyInput] = useState('');
  const [foodAllergyInput, setFoodAllergyInput] = useState('');
  const [environmentalAllergyInput, setEnvironmentalAllergyInput] = useState('');
  const [medicationInput, setMedicationInput] = useState({ name: '', dose: '' });
  const [surgeryInput, setSurgeryInput] = useState({ name: '', year: '' });

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
      toast.success('Health profile updated successfully!');
    } catch (error) {
      toast.error('Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const addChronicCondition = () => {
    if (chronicConditionInput.trim()) {
      setFormData({
        ...formData,
        chronic_conditions: [...(formData.chronic_conditions || []), chronicConditionInput.trim()]
      });
      setChronicConditionInput('');
    }
  };

  const removeChronicCondition = (index: number) => {
    setFormData({
      ...formData,
      chronic_conditions: formData.chronic_conditions?.filter((_, i) => i !== index)
    });
  };

  const addAllergy = (type: 'drug' | 'food' | 'environmental', value: string) => {
    if (value.trim()) {
      setFormData({
        ...formData,
        allergies: {
          ...formData.allergies,
          [type]: [...(formData.allergies?.[type] || []), value.trim()]
        }
      });
    }
  };

  const removeAllergy = (type: 'drug' | 'food' | 'environmental', index: number) => {
    setFormData({
      ...formData,
      allergies: {
        ...formData.allergies,
        [type]: formData.allergies?.[type]?.filter((_, i) => i !== index) || []
      }
    });
  };

  const addMedication = () => {
    if (medicationInput.name.trim()) {
      setFormData({
        ...formData,
        current_medications: [
          ...(formData.current_medications || []),
          { name: medicationInput.name.trim(), dose: medicationInput.dose.trim() }
        ]
      });
      setMedicationInput({ name: '', dose: '' });
    }
  };

  const removeMedication = (index: number) => {
    setFormData({
      ...formData,
      current_medications: formData.current_medications?.filter((_, i) => i !== index)
    });
  };

  const addSurgery = () => {
    if (surgeryInput.name.trim()) {
      setFormData({
        ...formData,
        past_surgeries: [
          ...(formData.past_surgeries || []),
          { name: surgeryInput.name.trim(), year: surgeryInput.year }
        ]
      });
      setSurgeryInput({ name: '', year: '' });
    }
  };

  const removeSurgery = (index: number) => {
    setFormData({
      ...formData,
      past_surgeries: formData.past_surgeries?.filter((_, i) => i !== index)
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
          <h1 className="text-3xl font-bold text-gray-900">Health Profile</h1>
          <p className="text-gray-600 mt-2">
            Keep your health information up to date for personalized medical advice
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
                <p className="text-sm text-gray-600">Your fundamental health metrics</p>
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
                  placeholder="e.g., 35"
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
                  placeholder="e.g., 175"
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
                  placeholder="e.g., 70"
                  min="20"
                  max="300"
                  step="0.1"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Blood Type
                </label>
                <select
                  value={formData.blood_type || ''}
                  onChange={(e) => setFormData({ ...formData, blood_type: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="">Select blood type</option>
                  <option value="A+">A+</option>
                  <option value="A-">A-</option>
                  <option value="B+">B+</option>
                  <option value="B-">B-</option>
                  <option value="AB+">AB+</option>
                  <option value="AB-">AB-</option>
                  <option value="O+">O+</option>
                  <option value="O-">O-</option>
                </select>
              </div>

              {bmi && (
                <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                  <div className="text-sm font-medium text-blue-900">BMI</div>
                  <div className="text-2xl font-bold text-blue-700">{bmi}</div>
                  <div className="text-xs text-blue-600 mt-1">
                    {parseFloat(bmi) < 18.5 && 'Underweight'}
                    {parseFloat(bmi) >= 18.5 && parseFloat(bmi) < 25 && 'Normal weight'}
                    {parseFloat(bmi) >= 25 && parseFloat(bmi) < 30 && 'Overweight'}
                    {parseFloat(bmi) >= 30 && 'Obese'}
                  </div>
                </div>
              )}
            </div>
          </section>

          {/* Medical History */}
          <section className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                <Heart className="w-5 h-5 text-red-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">Medical History</h2>
                <p className="text-sm text-gray-600">Chronic conditions and past health issues</p>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Chronic Conditions
                </label>
                <div className="flex gap-2 mb-3">
                  <input
                    type="text"
                    value={chronicConditionInput}
                    onChange={(e) => setChronicConditionInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addChronicCondition())}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="e.g., diabetes, hypertension"
                  />
                  <button
                    type="button"
                    onClick={addChronicCondition}
                    className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
                  >
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.chronic_conditions?.map((condition, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center gap-2 px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm"
                    >
                      {condition}
                      <button
                        type="button"
                        onClick={() => removeChronicCondition(index)}
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

          {/* Allergies */}
          <section className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
                <AlertCircle className="w-5 h-5 text-yellow-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">Allergies</h2>
                <p className="text-sm text-gray-600">Important for medication safety</p>
              </div>
            </div>

            <div className="space-y-6">
              {/* Drug Allergies */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Drug Allergies
                </label>
                <div className="flex gap-2 mb-3">
                  <input
                    type="text"
                    value={drugAllergyInput}
                    onChange={(e) => setDrugAllergyInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addAllergy('drug', drugAllergyInput), setDrugAllergyInput(''))}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="e.g., penicillin, aspirin"
                  />
                  <button
                    type="button"
                    onClick={() => { addAllergy('drug', drugAllergyInput); setDrugAllergyInput(''); }}
                    className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
                  >
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.allergies?.drug?.map((allergy, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center gap-2 px-3 py-1 bg-yellow-100 text-yellow-900 rounded-full text-sm font-medium"
                    >
                      {allergy}
                      <button
                        type="button"
                        onClick={() => removeAllergy('drug', index)}
                        className="hover:text-yellow-950"
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
                <div className="flex gap-2 mb-3">
                  <input
                    type="text"
                    value={foodAllergyInput}
                    onChange={(e) => setFoodAllergyInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addAllergy('food', foodAllergyInput), setFoodAllergyInput(''))}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="e.g., peanuts, shellfish"
                  />
                  <button
                    type="button"
                    onClick={() => { addAllergy('food', foodAllergyInput); setFoodAllergyInput(''); }}
                    className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
                  >
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.allergies?.food?.map((allergy, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center gap-2 px-3 py-1 bg-yellow-100 text-yellow-900 rounded-full text-sm"
                    >
                      {allergy}
                      <button
                        type="button"
                        onClick={() => removeAllergy('food', index)}
                        className="hover:text-yellow-950"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              {/* Environmental Allergies */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Environmental Allergies
                </label>
                <div className="flex gap-2 mb-3">
                  <input
                    type="text"
                    value={environmentalAllergyInput}
                    onChange={(e) => setEnvironmentalAllergyInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addAllergy('environmental', environmentalAllergyInput), setEnvironmentalAllergyInput(''))}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="e.g., pollen, dust mites"
                  />
                  <button
                    type="button"
                    onClick={() => { addAllergy('environmental', environmentalAllergyInput); setEnvironmentalAllergyInput(''); }}
                    className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
                  >
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.allergies?.environmental?.map((allergy, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center gap-2 px-3 py-1 bg-yellow-100 text-yellow-900 rounded-full text-sm"
                    >
                      {allergy}
                      <button
                        type="button"
                        onClick={() => removeAllergy('environmental', index)}
                        className="hover:text-yellow-950"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </section>

          {/* Current Medications */}
          <section className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <Pill className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">Current Medications</h2>
                <p className="text-sm text-gray-600">Medications you're currently taking</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <input
                  type="text"
                  value={medicationInput.name}
                  onChange={(e) => setMedicationInput({ ...medicationInput, name: e.target.value })}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Medication name"
                />
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={medicationInput.dose}
                    onChange={(e) => setMedicationInput({ ...medicationInput, dose: e.target.value })}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="Dosage (e.g., 500mg twice daily)"
                  />
                  <button
                    type="button"
                    onClick={addMedication}
                    className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
                  >
                    Add
                  </button>
                </div>
              </div>

              <div className="space-y-2">
                {formData.current_medications?.map((med, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200"
                  >
                    <div>
                      <div className="font-medium text-blue-900">{med.name}</div>
                      {med.dose && <div className="text-sm text-blue-700">{med.dose}</div>}
                    </div>
                    <button
                      type="button"
                      onClick={() => removeMedication(index)}
                      className="text-blue-600 hover:text-blue-800 font-bold"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* Past Surgeries */}
          <section className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <Activity className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">Past Surgeries</h2>
                <p className="text-sm text-gray-600">Previous surgical procedures</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <input
                  type="text"
                  value={surgeryInput.name}
                  onChange={(e) => setSurgeryInput({ ...surgeryInput, name: e.target.value })}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Surgery name"
                />
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={surgeryInput.year}
                    onChange={(e) => setSurgeryInput({ ...surgeryInput, year: e.target.value })}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="Year (e.g., 2020)"
                  />
                  <button
                    type="button"
                    onClick={addSurgery}
                    className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
                  >
                    Add
                  </button>
                </div>
              </div>

              <div className="space-y-2">
                {formData.past_surgeries?.map((surgery, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-purple-50 rounded-lg border border-purple-200"
                  >
                    <div>
                      <div className="font-medium text-purple-900">{surgery.name}</div>
                      {surgery.year && <div className="text-sm text-purple-700">{surgery.year}</div>}
                    </div>
                    <button
                      type="button"
                      onClick={() => removeSurgery(index)}
                      className="text-purple-600 hover:text-purple-800 font-bold"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* Lifestyle */}
          <section className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <Activity className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">Lifestyle</h2>
                <p className="text-sm text-gray-600">Health habits and behaviors</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Smoking Status
                </label>
                <select
                  value={formData.smoking_status || ''}
                  onChange={(e) => setFormData({ ...formData, smoking_status: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="">Select</option>
                  <option value="never">Never</option>
                  <option value="former">Former smoker</option>
                  <option value="current">Current smoker</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Alcohol Consumption
                </label>
                <select
                  value={formData.alcohol_consumption || ''}
                  onChange={(e) => setFormData({ ...formData, alcohol_consumption: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="">Select</option>
                  <option value="none">None</option>
                  <option value="occasional">Occasional</option>
                  <option value="moderate">Moderate</option>
                  <option value="heavy">Heavy</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Exercise Frequency
                </label>
                <select
                  value={formData.exercise_frequency || ''}
                  onChange={(e) => setFormData({ ...formData, exercise_frequency: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="">Select</option>
                  <option value="none">None</option>
                  <option value="1-2_per_week">1-2 times per week</option>
                  <option value="3-4_per_week">3-4 times per week</option>
                  <option value="5+_per_week">5+ times per week</option>
                </select>
              </div>
            </div>
          </section>

          {/* Emergency Contact */}
          <section className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
                <Users className="w-5 h-5 text-orange-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">Emergency Contact</h2>
                <p className="text-sm text-gray-600">Someone we can reach in case of emergency</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Name
                </label>
                <input
                  type="text"
                  value={formData.emergency_contact?.name || ''}
                  onChange={(e) => setFormData({
                    ...formData,
                    emergency_contact: { ...formData.emergency_contact, name: e.target.value }
                  })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Full name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Relationship
                </label>
                <input
                  type="text"
                  value={formData.emergency_contact?.relationship || ''}
                  onChange={(e) => setFormData({
                    ...formData,
                    emergency_contact: { ...formData.emergency_contact, relationship: e.target.value }
                  })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="e.g., spouse, parent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Phone Number
                </label>
                <input
                  type="tel"
                  value={formData.emergency_contact?.phone || ''}
                  onChange={(e) => setFormData({
                    ...formData,
                    emergency_contact: { ...formData.emergency_contact, phone: e.target.value }
                  })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Phone number"
                />
              </div>
            </div>
          </section>

          {/* Submit Button */}
          <div className="flex justify-end gap-4">
            <button
              type="button"
              onClick={() => window.history.back()}
              className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Saving...' : 'Save Health Profile'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
