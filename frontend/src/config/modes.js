/**
 * NyayaAI User Modes Configuration
 * 
 * Defines the four user modes for the platform:
 * 1. Judicial Intelligence Mode
 * 2. Legal Research Mode
 * 3. Investigation Intelligence Mode
 * 4. Citizen Legal Assistance Mode
 */

export const MODES = {
  JUDICIAL: {
    id: 'judicial',
    name: 'Judicial Intelligence',
    description: 'For judges, judicial officers and court researchers',
    icon: '⚖️',
    color: 'blue',
    accent: 'text-blue-600',
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    navColor: 'text-blue-100 hover:text-white hover:bg-white/10',
    activeColor: 'bg-blue-400 text-blue-700',
    features: [
      { id: 'legal-research', name: 'Legal Research', description: 'Search and explore judgments and legal provisions', icon: '📚', path: '/research' },
      { id: 'precedent-research', name: 'Precedent Research', description: 'Identify and compare legally relevant precedents', icon: '🔍', status: 'coming-soon' },
      { id: 'judgment-analysis', name: 'Judgment Analysis', description: 'Use the existing document/case analysis functionality', icon: '📄', path: '/case-research-upload' },
      { id: 'judgment-comparison', name: 'Compare Judgments', description: 'Compare two judgments using semantic embeddings', icon: '⚖️', path: '/compare-judgments' },
      { id: 'legal-reasoning', name: 'Legal Reasoning', description: 'AI-assisted legal reasoning assistance', icon: '🧠', status: 'coming-soon' },
      { id: 'legal-trends', name: 'Legal Trends', description: 'Analyze legal trends and patterns', icon: '📈', status: 'coming-soon' },
    ]
  },
  LEGAL: {
    id: 'legal',
    name: 'Legal Research',
    description: 'For lawyers, advocates, law students and legal researchers',
    icon: '📚',
    color: 'indigo',
    accent: 'text-indigo-600',
    bg: 'bg-indigo-50',
    border: 'border-indigo-200',
    navColor: 'text-indigo-100 hover:text-white hover:bg-white/10',
    activeColor: 'bg-indigo-400 text-indigo-700',
    features: [
      { id: 'advanced-search', name: 'Advanced Legal Search', description: 'Use the existing search engine', icon: '🔍', path: '/research' },
      { id: 'case-law-research', name: 'Case Law Research', description: 'Use the existing case/judgment repository', icon: '⚖️', path: '/repository' },
      { id: 'document-analysis', name: 'Legal Document Analysis', description: 'Use the existing document processing functionality', icon: '📄', path: '/upload' },
      { id: 'citation-finder', name: 'Citation Finder', description: 'Find and verify legal citations automatically', icon: '📝', status: 'coming-soon' },
      { id: 'argument-research', name: 'Argument Research', description: 'Research legal arguments and precedents', icon: '🗣️', status: 'coming-soon' },
      { id: 'case-brief-generator', name: 'Case Brief Generator', description: 'Generate case briefs and summaries', icon: '📋', status: 'coming-soon' },
    ]
  },
  INVESTIGATION: {
    id: 'investigation',
    name: 'Investigation Intelligence',
    description: 'For police, investigators and authorized investigation professionals',
    icon: '🕵️',
    color: 'slate',
    accent: 'text-slate-600',
    bg: 'bg-slate-50',
    border: 'border-slate-200',
    navColor: 'text-slate-100 hover:text-white hover:bg-white/10',
    activeColor: 'bg-slate-400 text-slate-700',
    features: [
      { id: 'criminal-case-research', name: 'Criminal Case Research', description: 'Search existing legal database', icon: '🔍', path: '/research' },
      { id: 'legal-provisions', name: 'Relevant Legal Provisions', description: 'Find applicable legal provisions', icon: '📜', path: '/research' },
      { id: 'fir-analysis', name: 'FIR / Document Analysis', description: 'Analyze FIRs and investigation documents', icon: '📄', path: '/upload' },
      { id: 'investigation-guide', name: 'Investigation Procedure Guide', description: 'Guidelines for investigation procedures', icon: '📋', status: 'coming-soon' },
      { id: 'evidence-research', name: 'Evidence-Related Legal Research', description: 'Research evidence-related legal provisions', icon: '🔍', status: 'coming-soon' },
      { id: 'timeline-analyzer', name: 'Timeline Analyzer', description: 'Analyze timelines and events', icon: '📅', status: 'coming-soon' },
    ]
  },
  CITIZEN: {
    id: 'citizen',
    name: 'Citizen Legal Assistance',
    description: 'For citizens seeking accessible legal information',
    icon: '👤',
    color: 'navy',
    accent: 'text-navy-600',
    bg: 'bg-navy-50',
    border: 'border-navy-200',
    navColor: 'text-navy-100 hover:text-white hover:bg-white/10',
    activeColor: 'bg-white/20 text-white',
    features: [
      { id: 'citizen-ask-question', name: 'Ask Question', description: 'Chat with AI about your legal doubts', icon: '❓', path: '/citizen/ask-question' },
      { id: 'citizen-legal-research', name: 'Legal Research', description: 'Search cases, acts and judgments', icon: '🔍', path: '/citizen/legal-research' },
      { id: 'citizen-legal-repository', name: 'Legal Repository', description: 'Explore Indian legal documents', icon: '📚', path: '/citizen/legal-repository' },
      { id: 'citizen-case-analysis', name: 'Case Analysis', description: 'Upload documents and get AI insights', icon: '📄', path: '/citizen/case-analysis' },
    ]
  }
};

export const MODES_LIST = Object.values(MODES);

// Get mode by ID
export const getModeById = (modeId) => MODES[modeId.toUpperCase()] || MODES.JUDICIAL;

// Get mode by name
export const getModeByName = (modeName) => {
  const normalized = modeName.toLowerCase().replace(/\s+/g, '_');
  return MODES_LIST.find(m => m.id === normalized) || MODES.JUDICIAL;
};

// Get all features for a mode
export const getModeFeatures = (modeId) => {
  const mode = getModeById(modeId);
  return mode ? mode.features : [];
};

// Check if feature is available (not coming soon)
export const isFeatureAvailable = (feature) => {
  return !feature.status || feature.status !== 'coming-soon';
};

// Get available features for a mode
export const getAvailableFeatures = (modeId) => {
  const features = getModeFeatures(modeId);
  return features.filter(isFeatureAvailable);
};

// Get coming soon features for a mode
export const getComingSoonFeatures = (modeId) => {
  const features = getModeFeatures(modeId);
  return features.filter(f => !isFeatureAvailable(f));
};
