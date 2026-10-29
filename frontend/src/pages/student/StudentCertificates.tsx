import React, { useState, useEffect } from 'react';
import { Award, Download, Calendar, CheckCircle2, ShieldCheck } from 'lucide-react';
import { CertificateItem } from '../../types';
import { api } from '../../services/api';
import toast from 'react-hot-toast';

export const StudentCertificates: React.FC = () => {
  const [certificates, setCertificates] = useState<CertificateItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getCertificates()
      .then((res) => setCertificates(res))
      .catch((err) => toast.error(err.message || 'Failed to load certificates'))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-400 border border-amber-200 dark:border-amber-800/80 mb-2">
          <Award className="w-3.5 h-3.5" />
          University Verified Credentials
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
          Earned Academic Certificates
        </h1>
        <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
          Official ReportLab PDF certificates issued upon achieving 100% course curriculum mastery and passing all continuous assessments.
        </p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center min-h-[30vh]">
          <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : certificates.length === 0 ? (
        <div className="p-12 text-center rounded-3xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800">
          <Award className="w-10 h-10 text-slate-400 mx-auto mb-2 opacity-40" />
          <h3 className="text-sm font-bold text-slate-700 dark:text-slate-200">No Certificates Earned Yet</h3>
          <p className="text-xs text-slate-500 mt-1">
            Complete all modules and passing quizzes in any enrolled course to receive your official certificate!
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {certificates.map((cert) => (
            <div
              key={cert.id}
              className="p-6 rounded-3xl bg-gradient-to-br from-white to-amber-50/20 dark:from-[#1E293B] dark:to-[#172033] border border-amber-200/80 dark:border-amber-900/60 shadow-lg space-y-4 relative overflow-hidden"
            >
              <div className="absolute top-0 right-0 p-6 pointer-events-none opacity-5 dark:opacity-10">
                <Award className="w-36 h-36 text-amber-600" />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="p-2 rounded-xl bg-amber-500/10 text-amber-600 dark:text-amber-400">
                    <ShieldCheck className="w-5 h-5" />
                  </div>
                  <span className="text-[10px] font-mono font-bold tracking-wider text-slate-500 dark:text-slate-400 uppercase">
                    UID: {cert.certificate_uid}
                  </span>
                </div>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300">
                  Accredited
                </span>
              </div>

              <div>
                <span className="text-xs text-slate-500 font-medium">Conferred upon</span>
                <h3 className="text-lg font-black text-slate-900 dark:text-white">
                  {cert.student_name}
                </h3>
              </div>

              <div>
                <span className="text-xs text-slate-500 font-medium">For completion of</span>
                <h4 className="text-sm font-bold text-indigo-600 dark:text-indigo-400">
                  {cert.course_title}
                </h4>
              </div>

              <div className="pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500">
                <span className="flex items-center gap-1.5">
                  <Calendar className="w-3.5 h-3.5 text-slate-400" />
                  {new Date(cert.completion_date).toLocaleDateString()}
                </span>

                <a
                  href={api.getCertificateDownloadUrl(cert.id)}
                  download={`EduAI_Certificate_${cert.certificate_uid}.pdf`}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold text-white bg-amber-600 hover:bg-amber-700 transition shadow-sm"
                >
                  <Download className="w-4 h-4" />
                  Download PDF
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
