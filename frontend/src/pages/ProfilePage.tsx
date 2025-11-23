import { useState, useEffect } from 'react';
import { useAuthStore } from '@/stores/authStore';
import { ClientProfile } from '@/types';
import toast from 'react-hot-toast';
import { User, Briefcase, Scale, AlertCircle, Building, DollarSign } from 'lucide-react';

export default function ProfilePage() {
  const { clientProfile, updateClientProfile, user } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<Partial<ClientProfile>>({
    occupation: '',
    employer: '',
    citizenship: '',
    marital_status: '',
    legal_areas_of_interest: [],
    active_legal_matters: [],
    previous_legal_issues: [],
    legal_restrictions: [],
    business_entities: [],
    financial_concerns: [],
    preferred_communication: '',
    emergency_contact_name: '',
    emergency_contact_phone: '',
    emergency_contact_relationship: ''
  });

  // Input states
  const [legalAreaInput, setLegalAreaInput] = useState('');
  const [activeMatterInput, setActiveMatterInput] = useState({ description: '', status: '' });
  const [previousIssueInput, setPreviousIssueInput] = useState({ type: '', year: '' });
  const [restrictionInput, setRestrictionInput] = useState({ type: '', details: '' });
  const [businessEntityInput, setBusinessEntityInput] = useState({ name: '', type: '', ownership_percentage: 0 });
  const [financialConcernInput, setFinancialConcernInput] = useState('');

  useEffect(() => {
    if (clientProfile) {
      setFormData(clientProfile);
    }
  }, [clientProfile]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await updateClientProfile(formData);
      toast.success('Client profile updated successfully!');
    } catch (error) {
      toast.error('Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  // Legal areas management
  const addLegalArea = () => {
    if (legalAreaInput.trim()) {
      setFormData({
        ...formData,
        legal_areas_of_interest: [...(formData.legal_areas_of_interest || []), legalAreaInput.trim()]
      });
      setLegalAreaInput('');
    }
  };

  const removeLegalArea = (index: number) => {
    setFormData({
      ...formData,
      legal_areas_of_interest: formData.legal_areas_of_interest?.filter((_, i) => i !== index)
    });
  };

  // Active matters management
  const addActiveMatter = () => {
    if (activeMatterInput.description.trim()) {
      setFormData({
        ...formData,
        active_legal_matters: [
          ...(formData.active_legal_matters || []),
          { description: activeMatterInput.description.trim(), status: activeMatterInput.status }
        ]
      });
      setActiveMatterInput({ description: '', status: '' });
    }
  };

  const removeActiveMatter = (index: number) => {
    setFormData({
      ...formData,
      active_legal_matters: formData.active_legal_matters?.filter((_, i) => i !== index)
    });
  };

  // Previous issues management
  const addPreviousIssue = () => {
    if (previousIssueInput.type.trim()) {
      setFormData({
        ...formData,
        previous_legal_issues: [
          ...(formData.previous_legal_issues || []),
          { type: previousIssueInput.type.trim(), year: previousIssueInput.year }
        ]
      });
      setPreviousIssueInput({ type: '', year: '' });
    }
  };

  const removePreviousIssue = (index: number) => {
    setFormData({
      ...formData,
      previous_legal_issues: formData.previous_legal_issues?.filter((_, i) => i !== index)
    });
  };

  // Legal restrictions management
  const addRestriction = () => {
    if (restrictionInput.type.trim()) {
      setFormData({
        ...formData,
        legal_restrictions: [
          ...(formData.legal_restrictions || []),
          { type: restrictionInput.type.trim(), details: restrictionInput.details }
        ]
      });
      setRestrictionInput({ type: '', details: '' });
    }
  };

  const removeRestriction = (index: number) => {
    setFormData({
      ...formData,
      legal_restrictions: formData.legal_restrictions?.filter((_, i) => i !== index)
    });
  };

  // Business entities management
  const addBusinessEntity = () => {
    if (businessEntityInput.name.trim()) {
      setFormData({
        ...formData,
        business_entities: [
          ...(formData.business_entities || []),
          {
            name: businessEntityInput.name.trim(),
            type: businessEntityInput.type,
            ownership_percentage: businessEntityInput.ownership_percentage
          }
        ]
      });
      setBusinessEntityInput({ name: '', type: '', ownership_percentage: 0 });
    }
  };

  const removeBusinessEntity = (index: number) => {
    setFormData({
      ...formData,
      business_entities: formData.business_entities?.filter((_, i) => i !== index)
    });
  };

  // Financial concerns management
  const addFinancialConcern = () => {
    if (financialConcernInput.trim()) {
      setFormData({
        ...formData,
        financial_concerns: [...(formData.financial_concerns || []), financialConcernInput.trim()]
      });
      setFinancialConcernInput('');
    }
  };

  const removeFinancialConcern = (index: number) => {
    setFormData({
      ...formData,
      financial_concerns: formData.financial_concerns?.filter((_, i) => i !== index)
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-5xl mx-auto px-6 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Client Profile</h1>
          <p className="text-gray-600 mt-2">
            Keep your legal information up to date for personalized legal guidance
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
                <p className="text-sm text-gray-600">Your personal details</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Occupation
                </label>
                <input
                  type="text"
                  value={formData.occupation || ''}
                  onChange={(e) => setFormData({ ...formData, occupation: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="e.g., Software Engineer"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Employer
                </label>
                <input
                  type="text"
                  value={formData.employer || ''}
                  onChange={(e) => setFormData({ ...formData, employer: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="e.g., Tech Corp"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Citizenship
                </label>
                <input
                  type="text"
                  value={formData.citizenship || ''}
                  onChange={(e) => setFormData({ ...formData, citizenship: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="e.g., United States"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Marital Status
                </label>
                <select
                  value={formData.marital_status || ''}
                  onChange={(e) => setFormData({ ...formData, marital_status: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="">Select...</option>
                  <option value="single">Single</option>
                  <option value="married">Married</option>
                  <option value="divorced">Divorced</option>
                  <option value="widowed">Widowed</option>
                </select>
              </div>
            </div>
          </section>

          {/* Legal Areas of Interest */}
          <section className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <Scale className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">Legal Areas of Interest</h2>
                <p className="text-sm text-gray-600">Areas of law you're interested in or need guidance on</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={legalAreaInput}
                  onChange={(e) => setLegalAreaInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addLegalArea())}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="e.g., Family Law, Employment Law, Contract Law"
                />
                <button
                  type="button"
                  onClick={addLegalArea}
                  className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                >
                  Add
                </button>
              </div>

              <div className="flex flex-wrap gap-2">
                {formData.legal_areas_of_interest?.map((area, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center gap-2 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                  >
                    {area}
                    <button
                      type="button"
                      onClick={() => removeLegalArea(index)}
                      className="text-blue-600 hover:text-blue-800"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>
          </section>

          {/* Active Legal Matters */}
          <section className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
                <Briefcase className="w-5 h-5 text-orange-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">Active Legal Matters</h2>
                <p className="text-sm text-gray-600">Ongoing legal cases or matters</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <input
                  type="text"
                  value={activeMatterInput.description}
                  onChange={(e) => setActiveMatterInput({ ...activeMatterInput, description: e.target.value })}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Description of matter"
                />
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={activeMatterInput.status}
                    onChange={(e) => setActiveMatterInput({ ...activeMatterInput, status: e.target.value })}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="Status"
                  />
                  <button
                    type="button"
                    onClick={addActiveMatter}
                    className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                  >
                    Add
                  </button>
                </div>
              </div>

              <div className="space-y-2">
                {formData.active_legal_matters?.map((matter, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <p className="font-medium">{matter.description}</p>
                      {matter.status && <p className="text-sm text-gray-600">Status: {matter.status}</p>}
                    </div>
                    <button
                      type="button"
                      onClick={() => removeActiveMatter(index)}
                      className="text-red-600 hover:text-red-800 text-xl"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* Legal Restrictions */}
          <section className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                <AlertCircle className="w-5 h-5 text-red-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">Legal Restrictions</h2>
                <p className="text-sm text-gray-600">Court orders, probation, restraining orders, etc.</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <input
                  type="text"
                  value={restrictionInput.type}
                  onChange={(e) => setRestrictionInput({ ...restrictionInput, type: e.target.value })}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Type of restriction"
                />
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={restrictionInput.details}
                    onChange={(e) => setRestrictionInput({ ...restrictionInput, details: e.target.value })}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="Details"
                  />
                  <button
                    type="button"
                    onClick={addRestriction}
                    className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                  >
                    Add
                  </button>
                </div>
              </div>

              <div className="space-y-2">
                {formData.legal_restrictions?.map((restriction, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-red-50 rounded-lg"
                  >
                    <div>
                      <p className="font-medium text-red-900">{restriction.type}</p>
                      {restriction.details && <p className="text-sm text-red-700">{restriction.details}</p>}
                    </div>
                    <button
                      type="button"
                      onClick={() => removeRestriction(index)}
                      className="text-red-600 hover:text-red-800 text-xl"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* Business Entities */}
          <section className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <Building className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">Business Entities</h2>
                <p className="text-sm text-gray-600">Businesses you own or have ownership interest in</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <input
                  type="text"
                  value={businessEntityInput.name}
                  onChange={(e) => setBusinessEntityInput({ ...businessEntityInput, name: e.target.value })}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Business name"
                />
                <input
                  type="text"
                  value={businessEntityInput.type}
                  onChange={(e) => setBusinessEntityInput({ ...businessEntityInput, type: e.target.value })}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Type (LLC, Corp, etc.)"
                />
                <div className="flex gap-2">
                  <input
                    type="number"
                    value={businessEntityInput.ownership_percentage}
                    onChange={(e) => setBusinessEntityInput({ ...businessEntityInput, ownership_percentage: parseFloat(e.target.value) })}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="Ownership %"
                    min="0"
                    max="100"
                  />
                  <button
                    type="button"
                    onClick={addBusinessEntity}
                    className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                  >
                    Add
                  </button>
                </div>
              </div>

              <div className="space-y-2">
                {formData.business_entities?.map((entity, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-green-50 rounded-lg"
                  >
                    <div>
                      <p className="font-medium text-green-900">{entity.name}</p>
                      <p className="text-sm text-green-700">
                        {entity.type} • {entity.ownership_percentage}% ownership
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeBusinessEntity(index)}
                      className="text-red-600 hover:text-red-800 text-xl"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* Financial Concerns */}
          <section className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
                <DollarSign className="w-5 h-5 text-yellow-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">Financial Concerns</h2>
                <p className="text-sm text-gray-600">Bankruptcy, liens, debt collection, etc.</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={financialConcernInput}
                  onChange={(e) => setFinancialConcernInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addFinancialConcern())}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="e.g., Bankruptcy, Tax Lien, Debt Collection"
                />
                <button
                  type="button"
                  onClick={addFinancialConcern}
                  className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                >
                  Add
                </button>
              </div>

              <div className="flex flex-wrap gap-2">
                {formData.financial_concerns?.map((concern, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center gap-2 px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm"
                  >
                    {concern}
                    <button
                      type="button"
                      onClick={() => removeFinancialConcern(index)}
                      className="text-yellow-600 hover:text-yellow-800"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>
          </section>

          {/* Contact Preferences */}
          <section className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <User className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">Contact & Emergency Information</h2>
                <p className="text-sm text-gray-600">How we should contact you</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Preferred Communication Method
                </label>
                <select
                  value={formData.preferred_communication || ''}
                  onChange={(e) => setFormData({ ...formData, preferred_communication: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="">Select...</option>
                  <option value="email">Email</option>
                  <option value="phone">Phone</option>
                  <option value="text">Text Message</option>
                  <option value="in-person">In-Person</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Emergency Contact Name
                </label>
                <input
                  type="text"
                  value={formData.emergency_contact_name || ''}
                  onChange={(e) => setFormData({ ...formData, emergency_contact_name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Full name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Emergency Contact Phone
                </label>
                <input
                  type="tel"
                  value={formData.emergency_contact_phone || ''}
                  onChange={(e) => setFormData({ ...formData, emergency_contact_phone: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="(555) 123-4567"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Relationship
                </label>
                <input
                  type="text"
                  value={formData.emergency_contact_relationship || ''}
                  onChange={(e) => setFormData({ ...formData, emergency_contact_relationship: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="e.g., Spouse, Parent, Sibling"
                />
              </div>
            </div>
          </section>

          {/* Submit Button */}
          <div className="flex justify-end gap-4">
            <button
              type="button"
              onClick={() => window.history.back()}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Saving...' : 'Save Client Profile'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
