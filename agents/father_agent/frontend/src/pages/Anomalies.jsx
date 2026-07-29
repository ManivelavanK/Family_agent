import React, { useState, useEffect } from 'react';
import { useFamily } from '../context/FamilyContext';
import { anomalyApi } from '../services/anomalyApi';
import { GlassCard } from '../components/ui/GlassCard';
import { AlertTriangle, ShieldAlert, Sparkles, CheckCircle2, ShieldCheck } from 'lucide-react';

export const Anomalies = () => {
  const { familyId } = useFamily();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchAnomalies = async () => {
      setLoading(true);
      try {
        const res = await anomalyApi.getAnomalies(familyId);
        setData(res);
      } catch (err) {
        console.error('Error fetching anomalies:', err);
      } fiillly: {
        setLoading(false);
      }
    };

    fetchAnomalies();
  }, [familyId]);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#102A43] tracking-tight flex items-center gap-3">
            <AlertTriangle className="w-8 h-8 text-[#D97706]" />
            <span>Financial Anomaly Detection</span>
          </h1>
          <p className="text-[#627D98] text-sm mt-1">
            Automated scanning engine for unusual spending spikes, category shifts, and irregular bills.
          </p>
        </div>
      </div>

      {loading ? (
        <div className="py-12 text-center text-[#627D98]">Scanning financial ledger for anomalies...</div>
      ) : data ? (
        <>
          {/* Risk Level Hero */}
          <GlassCard glow={data.total_anomalies_detected > 0} className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xs font-bold text-[#627D98] uppercase tracking-wider">Overall Anomaly Status</span>
                <div className="text-3xl font-black text-[#102A43] mt-1 flex items-center gap-3">
                  <span>{data.total_anomalies_detected} Anomalies Detected</span>
                </div>
              </div>

              <span
                className={`px-3 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider border ${
                  data.overall_risk_level === 'HIGH'
                    ? 'bg-[#C53030]/10 text-[#C53030] border-[#C53030]/30'
                    : data.overall_risk_level === 'MEDIUM'
                    ? 'bg-[#D97706]/10 text-[#D97706] border-[#D97706]/30'
                    : 'bg-[#2F855A]/10 text-[#2F855A] border-[#2F855A]/30'
                }`}
              >
                Risk: {data.overall_risk_level || 'LOW'}
              </span>
            </div>
          </GlassCard>

          {/* Anomaly Cards List */}
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-[#102A43]">Detected Financial Patterns</h3>

            {data.anomalies && data.anomalies.length > 0 ? (
              <div className="space-y-4">
                {data.anomalies.map((anom, idx) => (
                  <GlassCard key={idx} className="p-5 border-l-4 border-l-[#D97706]">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex items-start gap-3">
                        <div className="p-2.5 rounded-xl bg-[#D97706]/10 text-[#D97706] shrink-0 mt-0.5">
                          <ShieldAlert className="w-5 h-5" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <h4 className="font-bold text-[#172B4D] text-base">{anom.title || anom.anomaly_type}</h4>
                            <span className="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase bg-[#D97706]/15 text-[#D97706]">
                              {anom.severity || 'Warning'}
                            </span>
                          </div>
                          <p className="text-sm text-[#172B4D] mt-1">{anom.description || anom.message}</p>
                          {anom.impact && <p className="text-xs text-[#D97706] mt-2 font-semibold">Impact: {anom.impact}</p>}
                        </div>
                      </div>
                    </div>
                  </GlassCard>
                ))}
              </div>
            ) : (
              <GlassCard className="py-12 text-center text-[#627D98]">
                <ShieldCheck className="w-10 h-10 mx-auto mb-2 text-[#2F855A] opacity-80" />
                <span className="text-[#172B4D] font-semibold">No anomalous spending detected!</span>
                <p className="text-xs text-[#627D98] mt-1">Your family transactions follow expected historical patterns.</p>
              </GlassCard>
            )}
          </div>
        </>
      ) : (
        <div className="py-12 text-center text-[#627D98]">No anomaly data available for family #{familyId}.</div>
      )}
    </div>
  );
};

export default Anomalies;
