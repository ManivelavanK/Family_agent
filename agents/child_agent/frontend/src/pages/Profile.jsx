import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { User, BookOpen, Plus, Trash2, Edit3, Save, X } from 'lucide-react';
import { api } from '../services/api';
import { useApp } from '../context/AppContext';
import { SkeletonText } from '../components/Skeleton';

const LEARNING_STYLES = ['Visual & Practical','Auditory','Reading/Writing','Kinesthetic','Mixed'];

export default function Profile() {
  const { refreshToken, triggerRefresh, studentId } = useApp();
  const [student, setStudent] = useState(null);
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({});
  const [saving, setSaving] = useState(false);
  const [showAddSub, setShowAddSub] = useState(false);
  const [subForm, setSubForm] = useState({ name:'', target_hours_per_week:3, current_grade:'', color:'#6366F1' });

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      try {
        const [stu, subs] = await Promise.all([api.getStudent(studentId), api.getSubjects(studentId)]);
        if (!cancelled) { setStudent(stu); setSubjects(subs); setForm(stu); }
      } finally { if (!cancelled) setLoading(false); }
    }
    load();
    return () => { cancelled = true; };
  }, [refreshToken, studentId]);

  const save = async () => {
    setSaving(true);
    try {
      await api.updateStudent(studentId, form);
      triggerRefresh(); setEditing(false);
    } finally { setSaving(false); }
  };

  const addSubject = async () => {
    if (!subForm.name.trim()) return;
    await api.createSubject({ student_id:studentId, ...subForm, target_hours_per_week:+subForm.target_hours_per_week });
    setShowAddSub(false);
    setSubForm({ name:'', target_hours_per_week:3, current_grade:'', color:'#6366F1' });
    triggerRefresh();
  };

  const delSubject = async (id) => {
    await api.deleteSubject(id);
    triggerRefresh();
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <motion.div initial={{opacity:0,y:14}} animate={{opacity:1,y:0}}>
        <h1 className="section-title flex items-center gap-2.5"><User className="text-indigo-500" size={24}/> Profile</h1>
        <p className="section-sub">Your academic identity and subject roster.</p>
      </motion.div>

      {/* Profile Card */}
      <div className="glass rounded-3xl p-6">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl gradient-indigo-purple flex items-center justify-center text-2xl font-black text-white">
              {loading ? '?' : (student?.name?.[0] ?? 'S')}
            </div>
            <div>
              <div className="font-extrabold text-navy-dark text-lg">{loading?'Loading…':student?.name}</div>
              <div className="text-sm text-gray-400">{student?.grade}</div>
            </div>
          </div>
          <button onClick={()=>{ setEditing(e=>!e); setForm(student); }} className="btn-ghost text-xs px-3 py-1.5">
            {editing?<><X size={12}/> Cancel</>:<><Edit3 size={12}/> Edit</>}
          </button>
        </div>

        {loading ? <SkeletonText lines={5}/> : editing ? (
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-[10px] font-bold uppercase tracking-wider text-gray-400 block mb-1">Full Name</label>
                <input value={form.name||''} onChange={e=>setForm(f=>({...f,name:e.target.value}))} placeholder="Full Name" className="input-base"/>
              </div>
              <div>
                <label className="text-[10px] font-bold uppercase tracking-wider text-gray-400 block mb-1">Education Stage</label>
                <select value={form.education_level||'SCHOOL'} onChange={e=>setForm(f=>({...f,education_level:e.target.value}))} className="input-base">
                  <option value="SCHOOL">School Student</option>
                  <option value="COLLEGE">College Student</option>
                </select>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-2">
              <div>
                <label className="text-[10px] font-bold uppercase tracking-wider text-gray-400 block mb-1">Age</label>
                <input type="number" value={form.age||''} onChange={e=>setForm(f=>({...f,age:+e.target.value}))} placeholder="Age" className="input-base"/>
              </div>
              <div>
                <label className="text-[10px] font-bold uppercase tracking-wider text-gray-400 block mb-1">Institution</label>
                <input value={form.institution||''} onChange={e=>setForm(f=>({...f,institution:e.target.value}))} placeholder="Institution" className="input-base"/>
              </div>
              <div>
                <label className="text-[10px] font-bold uppercase tracking-wider text-gray-400 block mb-1">Grade / Year</label>
                <input value={form.grade||''} onChange={e=>setForm(f=>({...f,grade:e.target.value}))} placeholder="Grade/Year" className="input-base"/>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-[10px] font-bold uppercase tracking-wider text-gray-400 block mb-1">Learning Style</label>
                <select value={form.learning_style||''} onChange={e=>setForm(f=>({...f,learning_style:e.target.value}))} className="input-base">
                  {LEARNING_STYLES.map(s=><option key={s}>{s}</option>)}
                </select>
              </div>
              <div>
                <label className="text-[10px] font-bold uppercase tracking-wider text-gray-400 block mb-1">Weekly Target Hours</label>
                <input type="number" value={form.weekly_target_hours||10} onChange={e=>setForm(f=>({...f,weekly_target_hours:+e.target.value}))} placeholder="Weekly target" className="input-base"/>
              </div>
            </div>
            <div>
              <label className="text-[10px] font-bold uppercase tracking-wider text-gray-400 block mb-1">Career Goal / Interest</label>
              <input value={form.career_interest||''} onChange={e=>setForm(f=>({...f,career_interest:e.target.value}))} placeholder="Career Goal" className="input-base"/>
            </div>

            <div className="border border-indigo-100 rounded-2xl p-4 bg-indigo-50/30 space-y-3">
              <h4 className="font-bold text-navy-dark text-xs uppercase tracking-wider text-indigo-500">Stage Specific Details</h4>
              {form.education_level === 'COLLEGE' ? (
                <>
                  <div className="grid grid-cols-2 gap-2">
                    <input
                      value={form.profile_metadata?.coding_platforms?.leetcode || ''}
                      onChange={e => setForm(f => ({
                        ...f,
                        profile_metadata: {
                          ...f.profile_metadata,
                          coding_platforms: { ...f.profile_metadata?.coding_platforms, leetcode: e.target.value }
                        }
                      }))}
                      placeholder="LeetCode Username"
                      className="input-base"
                    />
                    <input
                      value={form.profile_metadata?.coding_platforms?.github || ''}
                      onChange={e => setForm(f => ({
                        ...f,
                        profile_metadata: {
                          ...f.profile_metadata,
                          coding_platforms: { ...f.profile_metadata?.coding_platforms, github: e.target.value }
                        }
                      }))}
                      placeholder="GitHub Username"
                      className="input-base"
                    />
                  </div>
                  <input
                    value={form.profile_metadata?.internship_tracking || ''}
                    onChange={e => setForm(f => ({
                      ...f,
                      profile_metadata: { ...f.profile_metadata, internship_tracking: e.target.value }
                    }))}
                    placeholder="Internship Tracking (e.g. Interviewing with Google)"
                    className="input-base"
                  />
                  <input
                    value={Array.isArray(form.profile_metadata?.projects) ? form.profile_metadata.projects.join(', ') : form.profile_metadata?.projects || ''}
                    onChange={e => setForm(f => ({
                      ...f,
                      profile_metadata: { ...f.profile_metadata, projects: e.target.value.split(',').map(s=>s.trim()).filter(Boolean) }
                    }))}
                    placeholder="Projects (comma separated)"
                    className="input-base"
                  />
                  <input
                    value={Array.isArray(form.profile_metadata?.hackathons) ? form.profile_metadata.hackathons.join(', ') : form.profile_metadata?.hackathons || ''}
                    onChange={e => setForm(f => ({
                      ...f,
                      profile_metadata: { ...f.profile_metadata, hackathons: e.target.value.split(',').map(s=>s.trim()).filter(Boolean) }
                    }))}
                    placeholder="Hackathons (comma separated)"
                    className="input-base"
                  />
                  <input
                    value={Array.isArray(form.profile_metadata?.certifications) ? form.profile_metadata.certifications.join(', ') : form.profile_metadata?.certifications || ''}
                    onChange={e => setForm(f => ({
                      ...f,
                      profile_metadata: { ...f.profile_metadata, certifications: e.target.value.split(',').map(s=>s.trim()).filter(Boolean) }
                    }))}
                    placeholder="Certifications (comma separated)"
                    className="input-base"
                  />
                </>
              ) : (
                <>
                  <input
                    value={form.profile_metadata?.study_habits || ''}
                    onChange={e => setForm(f => ({
                      ...f,
                      profile_metadata: { ...f.profile_metadata, study_habits: e.target.value }
                    }))}
                    placeholder="Study Habits (e.g. Prefers quiet study at night)"
                    className="input-base"
                  />
                  <input
                    value={form.profile_metadata?.reading_progress || ''}
                    onChange={e => setForm(f => ({
                      ...f,
                      profile_metadata: { ...f.profile_metadata, reading_progress: e.target.value }
                    }))}
                    placeholder="Reading Progress (e.g. Completed Chapter 5 of History)"
                    className="input-base"
                  />
                  <input
                    value={form.profile_metadata?.unit_tests || ''}
                    onChange={e => setForm(f => ({
                      ...f,
                      profile_metadata: { ...f.profile_metadata, unit_tests: e.target.value }
                    }))}
                    placeholder="Unit Test Prep details"
                    className="input-base"
                  />
                </>
              )}
            </div>

            <button onClick={save} disabled={saving} className="btn-primary w-full mt-2">
              <Save size={14}/>{saving?'Saving…':'Save Changes'}
            </button>
          </div>
        ) : (
          <div>
            <div className="grid grid-cols-2 gap-4">
              {[
                {label:'Education Level', value:student?.education_level === 'COLLEGE' ? 'College Student' : 'School Student'},
                {label:'Age',            value:student?.age ? `${student.age} years old` : '—'},
                {label:'Institution',    value:student?.institution},
                {label:'Year / Grade',   value:student?.grade},
                {label:'Learning Style', value:student?.learning_style},
                {label:'Career Goal',    value:student?.career_interest},
                {label:'Weekly Target',  value:`${student?.weekly_target_hours||0}h / week`},
              ].map(({label,value})=>(
                <div key={label} className="bg-gray-50 rounded-xl p-3">
                  <div className="text-xs text-gray-400 font-medium">{label}</div>
                  <div className="text-sm font-semibold text-navy-dark mt-0.5">{value||'—'}</div>
                </div>
              ))}
            </div>

            {student?.profile_metadata && Object.keys(student.profile_metadata).length > 0 && (
              <div className="mt-5 border-t border-gray-100 pt-4">
                <h4 className="font-bold text-navy-dark text-sm mb-3 text-indigo-600 uppercase tracking-wider text-xs">Stage Specific Details</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {student.education_level === 'COLLEGE' ? (
                    <>
                      <div className="bg-slate-50 rounded-xl p-3">
                        <div className="text-xs text-gray-400 font-medium">Coding Platform Profiles</div>
                        <div className="text-sm font-semibold text-navy-dark mt-0.5">
                          LeetCode: {student.profile_metadata.coding_platforms?.leetcode || '—'} · GitHub: {student.profile_metadata.coding_platforms?.github || '—'}
                        </div>
                      </div>
                      <div className="bg-slate-50 rounded-xl p-3">
                        <div className="text-xs text-gray-400 font-medium">Internship Tracking</div>
                        <div className="text-sm font-semibold text-navy-dark mt-0.5">{student.profile_metadata.internship_tracking || '—'}</div>
                      </div>
                      <div className="bg-slate-50 rounded-xl p-3 col-span-2">
                        <div className="text-xs text-gray-400 font-medium">Projects</div>
                        <div className="text-sm font-semibold text-navy-dark mt-0.5">
                          {Array.isArray(student.profile_metadata.projects) ? student.profile_metadata.projects.join(', ') : student.profile_metadata.projects || '—'}
                        </div>
                      </div>
                      <div className="bg-slate-50 rounded-xl p-3 col-span-2">
                        <div className="text-xs text-gray-400 font-medium">Hackathons</div>
                        <div className="text-sm font-semibold text-navy-dark mt-0.5">
                          {Array.isArray(student.profile_metadata.hackathons) ? student.profile_metadata.hackathons.join(', ') : student.profile_metadata.hackathons || '—'}
                        </div>
                      </div>
                      <div className="bg-slate-50 rounded-xl p-3 col-span-2">
                        <div className="text-xs text-gray-400 font-medium">Certifications</div>
                        <div className="text-sm font-semibold text-navy-dark mt-0.5">
                          {Array.isArray(student.profile_metadata.certifications) ? student.profile_metadata.certifications.join(', ') : student.profile_metadata.certifications || '—'}
                        </div>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="bg-slate-50 rounded-xl p-3 col-span-2">
                        <div className="text-xs text-gray-400 font-medium">Study Habits</div>
                        <div className="text-sm font-semibold text-navy-dark mt-0.5">{student.profile_metadata.study_habits || '—'}</div>
                      </div>
                      <div className="bg-slate-50 rounded-xl p-3 col-span-2">
                        <div className="text-xs text-gray-400 font-medium">Reading Progress</div>
                        <div className="text-sm font-semibold text-navy-dark mt-0.5">{student.profile_metadata.reading_progress || '—'}</div>
                      </div>
                      <div className="bg-slate-50 rounded-xl p-3 col-span-2">
                        <div className="text-xs text-gray-400 font-medium">Unit Test Details</div>
                        <div className="text-sm font-semibold text-navy-dark mt-0.5">{student.profile_metadata.unit_tests || '—'}</div>
                      </div>
                    </>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Subjects */}
      <div className="glass rounded-3xl p-6">
        <div className="flex items-center justify-between mb-5">
          <h3 className="font-bold text-navy-dark flex items-center gap-2"><BookOpen size={16} className="text-indigo-500"/> My Subjects</h3>
          <button onClick={()=>setShowAddSub(s=>!s)} className="btn-primary text-xs px-3 py-1.5">
            <Plus size={13}/> Add Subject
          </button>
        </div>

        <AnimatePresence>
          {showAddSub && (
            <motion.div initial={{height:0,opacity:0}} animate={{height:'auto',opacity:1}} exit={{height:0,opacity:0}} className="overflow-hidden mb-4">
              <div className="bg-indigo-50 rounded-2xl p-4 space-y-3 border border-indigo-100">
                <input value={subForm.name} onChange={e=>setSubForm(f=>({...f,name:e.target.value}))} placeholder="Subject name *" className="input-base"/>
                <div className="grid grid-cols-3 gap-2">
                  <input value={subForm.current_grade} onChange={e=>setSubForm(f=>({...f,current_grade:e.target.value}))} placeholder="Grade (A, B+…)" className="input-base"/>
                  <input type="number" value={subForm.target_hours_per_week} onChange={e=>setSubForm(f=>({...f,target_hours_per_week:e.target.value}))} placeholder="h/week" className="input-base"/>
                  <input type="color" value={subForm.color} onChange={e=>setSubForm(f=>({...f,color:e.target.value}))} className="input-base h-10 p-1"/>
                </div>
                <div className="flex gap-2">
                  <button onClick={()=>setShowAddSub(false)} className="btn-ghost flex-1 text-xs">Cancel</button>
                  <button onClick={addSubject} disabled={!subForm.name.trim()} className="btn-primary flex-1 text-xs">Add</button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {loading ? <SkeletonText lines={3}/> : subjects.length===0 ? (
          <p className="text-sm text-gray-400 text-center py-6">No subjects added yet.</p>
        ) : (
          <div className="space-y-2.5">
            {subjects.map(s=>(
              <div key={s.id} className="flex items-center gap-3 px-4 py-3 rounded-xl bg-gray-50 group hover:bg-gray-100 transition-colors">
                <div className="w-3 h-3 rounded-full shrink-0" style={{background:s.color||'#6366F1'}}/>
                <span className="flex-1 font-semibold text-navy-dark text-sm">{s.name}</span>
                <span className="text-xs text-gray-400">{s.current_grade}</span>
                <span className="text-xs text-gray-400">{s.target_hours_per_week}h/wk</span>
                <button onClick={()=>delSubject(s.id)} className="opacity-0 group-hover:opacity-100 text-gray-300 hover:text-rose-500 transition-all ml-2">
                  <Trash2 size={13}/>
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
