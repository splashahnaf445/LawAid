import React, { useState } from 'react';
import { 
  FileCheck2, 
  UploadCloud, 
  ShieldAlert, 
  CheckCircle, 
  AlertCircle, 
  FileText, 
  Lock, 
  Scale, 
  User, 
  Mail, 
  Phone, 
  KeyRound, 
  MapPin, 
  Briefcase,
  Trash2
} from 'lucide-react';
import { lawAidApi } from '../services/api';

export default function LawyerRegistration({ onRegistrationSuccess }) {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    password: '',
    honorific: 'Adv.',
    headline: 'Advocate, Supreme Court / Judges Court',
    bar_council_no: '',
    bar_association: 'Dhaka Bar Association',
    district: 'Dhaka',
    specialization: 'Civil Litigation, Property Law',
    consultation_fee: '1500',
    years_experience: '5',
    bio: ''
  });

  const [nidFile, setNidFile] = useState(null);
  const [barCertFile, setBarCertFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successResult, setSuccessResult] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e, type) => {
    const file = e.target.files[0];
    if (!file) return;

    // Check size limit: 15MB
    if (file.size > 15 * 1024 * 1024) {
      alert(`File "${file.name}" is too large. Maximum allowed size is 15MB.`);
      return;
    }

    if (type === 'nid') {
      setNidFile(file);
    } else {
      setBarCertFile(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');

    // Validation (FR-2)
    if (!nidFile) {
      setErrorMsg('Please upload your National ID (NID) card (PDF, PNG, or JPG).');
      return;
    }
    if (!barCertFile) {
      setErrorMsg('Please upload your Bangladesh Bar Council Certificate / Sanad (PDF, PNG, or JPG).');
      return;
    }
    if (!formData.bar_council_no.trim()) {
      setErrorMsg('Please enter your official Bar Council Sanad Number (e.g. SC-7841 or DH-9124).');
      return;
    }

    setLoading(true);
    try {
      const payload = new FormData();
      Object.keys(formData).forEach(key => {
        payload.append(key, formData[key]);
      });
      payload.append('nid_document', nidFile);
      payload.append('bar_certificate_document', barCertFile);

      const result = await lawAidApi.registerLawyer(payload);
      setSuccessResult(result);
      if (onRegistrationSuccess) {
        onRegistrationSuccess(result);
      }
    } catch (err) {
      console.error('Registration error:', err);
      if (typeof err === 'object') {
        const firstErrorKey = Object.keys(err)[0];
        const val = err[firstErrorKey];
        setErrorMsg(`${firstErrorKey}: ${Array.isArray(val) ? val.join(' ') : val}`);
      } else {
        setErrorMsg('Registration failed. Please check your network and input data.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto my-8 p-6 md:p-8 bg-white rounded-2xl shadow-xl border border-slate-200">
      {/* Title Header */}
      <div className="flex items-start justify-between border-b border-slate-100 pb-6 mb-8">
        <div>
          <div className="flex items-center gap-2.5 text-amber-600 font-bold text-xs uppercase tracking-wider mb-1">
            <Scale size={18} />
            <span>Advocate Verification Onboarding</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight">
            Lawyer Registration & Credential Verification
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            Compliant with SRS FR-2 & NFR-4: Identification documents are encrypted and reviewed by platform administrators.
          </p>
        </div>
        <span className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-semibold">
          <Lock size={12} className="text-slate-500" />
          AES-128 Encrypted Storage
        </span>
      </div>

      {/* Success Notification Modal / Screen */}
      {successResult ? (
        <div className="p-8 text-center bg-slate-50 rounded-2xl border border-emerald-200 shadow-inner">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-emerald-100 text-emerald-600 mb-4">
            <CheckCircle size={36} />
          </div>
          <h2 className="text-2xl font-bold text-slate-900 mb-2">Registration Submitted for Verification!</h2>
          <p className="text-slate-600 max-w-lg mx-auto text-sm mb-6">
            Thank you, <strong className="text-slate-900">{formData.honorific} {formData.full_name}</strong>. Your account has been registered with Bar Council ID <strong className="text-slate-900">{formData.bar_council_no}</strong>.
          </p>

          <div className="max-w-md mx-auto p-4 bg-white rounded-xl border border-slate-200 text-left text-sm space-y-2 mb-6">
            <div className="flex justify-between">
              <span className="text-slate-500">Status:</span>
              <span className="font-semibold px-2 py-0.5 rounded bg-amber-100 text-amber-800 text-xs">
                Pending Admin Verification (FR-3)
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Search Visibility:</span>
              <span className="font-semibold text-rose-600 text-xs">
                Hidden from public search until approved
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Uploaded Documents:</span>
              <span className="font-semibold text-slate-700 text-xs">
                NID & Bar Certificate (Encrypted at rest)
              </span>
            </div>
          </div>

          <p className="text-xs text-slate-500 max-w-md mx-auto mb-6">
            Our platform administrators will review your credentials against Bangladesh Bar Council records. Once approved, the official <strong>LawAid Verified Advocate</strong> badge will appear on your profile and you will become discoverable to clients.
          </p>

          <button
            onClick={() => {
              setSuccessResult(null);
              setNidFile(null);
              setBarCertFile(null);
            }}
            className="px-6 py-2.5 rounded-xl bg-slate-900 text-white font-medium text-sm hover:bg-slate-800 transition shadow"
          >
            Register Another Lawyer
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-8">
          {errorMsg && (
            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-sm flex items-start gap-3">
              <AlertCircle size={18} className="shrink-0 mt-0.5" />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* Section 1: Account Information */}
          <div>
            <h2 className="text-base font-bold text-slate-900 mb-4 flex items-center gap-2">
              <span className="flex items-center justify-center w-6 h-6 rounded-full bg-slate-900 text-white text-xs">1</span>
              Personal & Account Information
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Full Name (as per Bar Sanad) *</label>
                <div className="relative">
                  <User size={16} className="absolute left-3 top-3 text-slate-400" />
                  <input
                    type="text"
                    name="full_name"
                    required
                    placeholder="e.g. Syeda Farhana Begum"
                    value={formData.full_name}
                    onChange={handleInputChange}
                    className="w-full pl-9 pr-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Email Address *</label>
                <div className="relative">
                  <Mail size={16} className="absolute left-3 top-3 text-slate-400" />
                  <input
                    type="email"
                    name="email"
                    required
                    placeholder="advocate@dhakabar.gov.bd"
                    value={formData.email}
                    onChange={handleInputChange}
                    className="w-full pl-9 pr-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Phone Number (+8801...) *</label>
                <div className="relative">
                  <Phone size={16} className="absolute left-3 top-3 text-slate-400" />
                  <input
                    type="text"
                    name="phone"
                    required
                    placeholder="+88017XXXXXXXX"
                    value={formData.phone}
                    onChange={handleInputChange}
                    className="w-full pl-9 pr-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Password *</label>
                <div className="relative">
                  <KeyRound size={16} className="absolute left-3 top-3 text-slate-400" />
                  <input
                    type="password"
                    name="password"
                    required
                    placeholder="Min 6 characters"
                    value={formData.password}
                    onChange={handleInputChange}
                    className="w-full pl-9 pr-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Section 2: Professional Legal Credentials */}
          <div className="border-t border-slate-100 pt-6">
            <h2 className="text-base font-bold text-slate-900 mb-4 flex items-center gap-2">
              <span className="flex items-center justify-center w-6 h-6 rounded-full bg-slate-900 text-white text-xs">2</span>
              Professional Legal Credentials
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Honorific Title</label>
                <select
                  name="honorific"
                  value={formData.honorific}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                >
                  <option value="Adv.">Advocate (Adv.)</option>
                  <option value="Barrister">Barrister</option>
                  <option value="Senior Adv.">Senior Advocate</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Bar Council Sanad / ID Number *</label>
                <input
                  type="text"
                  name="bar_council_no"
                  required
                  placeholder="e.g. SC-7841 or DH-9124"
                  value={formData.bar_council_no}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 text-sm font-mono uppercase font-bold border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Bar Association *</label>
                <input
                  type="text"
                  name="bar_association"
                  required
                  placeholder="e.g. Supreme Court Bar Association"
                  value={formData.bar_association}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">District / Jurisdiction *</label>
                <select
                  name="district"
                  value={formData.district}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                >
                  <option value="Dhaka">Dhaka</option>
                  <option value="Chittagong">Chittagong</option>
                  <option value="Sylhet">Sylhet</option>
                  <option value="Rajshahi">Rajshahi</option>
                  <option value="Khulna">Khulna</option>
                  <option value="Barisal">Barisal</option>
                  <option value="Rangpur">Rangpur</option>
                  <option value="Mymensingh">Mymensingh</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Specialization / Practice Area *</label>
                <input
                  type="text"
                  name="specialization"
                  required
                  placeholder="e.g. Civil Litigation, Writ, Property Law"
                  value={formData.specialization}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Consultation Fee (BDT) *</label>
                <input
                  type="number"
                  name="consultation_fee"
                  min="0"
                  step="100"
                  value={formData.consultation_fee}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>
            </div>
          </div>

          {/* Section 3: Document Uploads (FR-2, NFR-4) */}
          <div className="border-t border-slate-100 pt-6">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-slate-900 text-white text-xs">3</span>
                Identification & Verification Documents (Mandatory)
              </h2>
              <span className="text-xs text-rose-600 font-medium">* Required for Verification</span>
            </div>
            <p className="text-slate-500 text-xs mb-4">
              Per Bangladesh Bar Council compliance, you must upload your National ID and Bar Council Certificate for identity authentication.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* NID Upload Card */}
              <div className="p-4 rounded-xl border-2 border-dashed border-slate-300 bg-slate-50/50 hover:bg-slate-50 transition">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
                    <FileText size={16} className="text-amber-600" />
                    National ID (NID) Card *
                  </span>
                  <span className="text-[10px] text-slate-500 uppercase font-semibold">PDF, PNG, JPG (Max 15MB)</span>
                </div>

                {nidFile ? (
                  <div className="p-3 bg-white rounded-lg border border-slate-200 flex items-center justify-between">
                    <div className="flex items-center gap-2 truncate">
                      <FileCheck2 size={20} className="text-emerald-600 shrink-0" />
                      <div className="truncate">
                        <p className="text-xs font-semibold text-slate-800 truncate">{nidFile.name}</p>
                        <p className="text-[10px] text-slate-400">{(nidFile.size / 1024).toFixed(1)} KB</p>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => setNidFile(null)}
                      className="p-1 text-slate-400 hover:text-rose-600 transition"
                      title="Remove file"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                ) : (
                  <label className="flex flex-col items-center justify-center py-6 cursor-pointer group">
                    <UploadCloud size={32} className="text-slate-400 group-hover:text-amber-600 transition mb-2" />
                    <span className="text-xs font-medium text-slate-700 group-hover:text-amber-700">
                      Click to upload National ID (NID)
                    </span>
                    <span className="text-[11px] text-slate-400 mt-0.5">Scanned copy or digital Smart NID</span>
                    <input
                      type="file"
                      accept=".pdf,.png,.jpg,.jpeg"
                      onChange={(e) => handleFileChange(e, 'nid')}
                      className="hidden"
                    />
                  </label>
                )}
              </div>

              {/* Bar Certificate Upload Card */}
              <div className="p-4 rounded-xl border-2 border-dashed border-slate-300 bg-slate-50/50 hover:bg-slate-50 transition">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
                    <Scale size={16} className="text-amber-600" />
                    Bar Council Certificate / Sanad *
                  </span>
                  <span className="text-[10px] text-slate-500 uppercase font-semibold">PDF, PNG, JPG (Max 15MB)</span>
                </div>

                {barCertFile ? (
                  <div className="p-3 bg-white rounded-lg border border-slate-200 flex items-center justify-between">
                    <div className="flex items-center gap-2 truncate">
                      <FileCheck2 size={20} className="text-emerald-600 shrink-0" />
                      <div className="truncate">
                        <p className="text-xs font-semibold text-slate-800 truncate">{barCertFile.name}</p>
                        <p className="text-[10px] text-slate-400">{(barCertFile.size / 1024).toFixed(1)} KB</p>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => setBarCertFile(null)}
                      className="p-1 text-slate-400 hover:text-rose-600 transition"
                      title="Remove file"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                ) : (
                  <label className="flex flex-col items-center justify-center py-6 cursor-pointer group">
                    <UploadCloud size={32} className="text-slate-400 group-hover:text-amber-600 transition mb-2" />
                    <span className="text-xs font-medium text-slate-700 group-hover:text-amber-700">
                      Click to upload Bar Council Sanad
                    </span>
                    <span className="text-[11px] text-slate-400 mt-0.5">Official Sanad Certificate with seal</span>
                    <input
                      type="file"
                      accept=".pdf,.png,.jpg,.jpeg"
                      onChange={(e) => handleFileChange(e, 'bar')}
                      className="hidden"
                    />
                  </label>
                )}
              </div>
            </div>

            {/* SRS Security Notice Box */}
            <div className="mt-4 p-4 rounded-xl bg-slate-900 text-slate-300 text-xs flex items-start gap-3 border border-slate-800">
              <Lock size={18} className="text-amber-400 shrink-0 mt-0.5" />
              <div>
                <strong className="text-white block mb-0.5">
                  SRS NFR-4 & FR-2 Security Guarantee:
                </strong>
                Uploaded documents are encrypted upon ingestion with AES-128-CBC authenticated encryption.
                They are stored as raw ciphertext on private storage and are accessible strictly to authorized LawAid compliance administrators. Public clients and third parties can never access or view your uploaded identity files.
              </div>
            </div>
          </div>

          {/* Submit Action Button */}
          <div className="border-t border-slate-100 pt-6 flex items-center justify-between">
            <span className="text-xs text-slate-500">
              By registering, you confirm the authenticity of your Bar Council credentials.
            </span>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-bold text-sm transition shadow-lg shadow-amber-600/20 disabled:opacity-50 flex items-center gap-2 cursor-pointer"
            >
              {loading ? (
                <>
                  <span className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></span>
                  Encrypting & Submitting...
                </>
              ) : (
                <>
                  <FileCheck2 size={18} />
                  Submit Registration for Verification
                </>
              )}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
