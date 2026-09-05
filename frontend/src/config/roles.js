/**
 * Role-Based Access Control Configuration for NyayaAI
 * 
 * Defines role-to-mode mapping and role-specific features
 */

// Role to Mode mapping
export const ROLE_MODE_MAP = {
  JUDGE: 'judicial',
  LAWYER: 'legal',
  POLICE: 'investigation',
  CIVILIAN: 'citizen',
  ADMIN: 'judicial' // Admins get judicial mode by default
};

// Mode to Role mapping (reverse)
export const MODE_ROLE_MAP = {
  judicial: 'JUDGE',
  legal: 'LAWYER',
  investigation: 'POLICE',
  citizen: 'CIVILIAN'
};

// Role display names
export const ROLE_NAMES = {
  JUDGE: 'Judge',
  LAWYER: 'Lawyer',
  POLICE: 'Police',
  CIVILIAN: 'Citizen',
  ADMIN: 'Admin'
};

export const JUDGE_NAV_FEATURES = [
  { id: 'judge-comparison', name: 'Judgment Comparison', path: '/judge/judgment-comparison' },
  { id: 'judge-precedents', name: 'Precedent Analysis', path: '/judge/precedent-analysis' },
  { id: 'judge-reasoning', name: 'Legal Reasoning', path: '/judge/legal-reasoning' },
  { id: 'judge-synthesis', name: 'Case-law Synthesis', path: '/judge/case-law-synthesis' },
];

// Role-based navigation configuration
export const ROLE_FEATURES = {
  JUDGE: [
    { id: 'judgment-analysis', name: 'Judgment Analysis', path: '/case-research-upload', icon: '📄' },
    { id: 'judgment-comparison', name: 'Compare Judgments', path: '/compare-judgments', icon: '⚖️' },
    { id: 'precedent-research', name: 'Precedent Research', path: '/repository', icon: '🔍' },
    { id: 'legal-research', name: 'Legal Research', path: '/research', icon: '📚' },
    { id: 'legal-reasoning', name: 'Legal Reasoning', path: '/research', icon: '🧠' },
    { id: 'legal-trends', name: 'Legal Trends', path: '/research', icon: '📈' },
  ],
  LAWYER: [
    { id: 'advanced-search', name: 'Advanced Research', path: '/lawyer/advanced-research', icon: '🔍' },
    { id: 'argument-research', name: 'Argument Research', path: '/lawyer/argument-research', icon: '🗣️' },
    { id: 'citation-finder', name: 'Citation Finder', path: '/lawyer/citation-finder', icon: '📝' },
    { id: 'case-brief-generation', name: 'Case Brief Generation', path: '/lawyer/case-brief-generation', icon: '📋' },
  ],
  POLICE: [
    { id: 'criminal-case-research', name: 'Criminal Case Research', path: '/research', icon: '🔍' },
    { id: 'legal-provisions', name: 'Legal Provisions', path: '/research', icon: '📜' },
    { id: 'fir-analysis', name: 'FIR Analysis', path: '/upload', icon: '📄' },
    { id: 'investigation-guide', name: 'Investigation Guide', path: '/research', icon: '📋' },
    { id: 'evidence-research', name: 'Evidence Research', path: '/research', icon: '🔍' },
    { id: 'timeline-analyzer', name: 'Timeline Analyzer', path: '/upload', icon: '📅' },
  ],
  CIVILIAN: [
    { id: 'citizen-ask-question', name: 'Ask Question', path: '/citizen/ask-question', icon: '❓' },
    { id: 'citizen-legal-research', name: 'Legal Research', path: '/citizen/legal-research', icon: '🔍' },
    { id: 'citizen-legal-repository', name: 'Legal Repository', path: '/citizen/legal-repository', icon: '📚' },
    { id: 'citizen-case-analysis', name: 'Case Analysis', path: '/citizen/case-analysis', icon: '📄' },
  ]
};

// Get mode for a role
export const getModeForRole = (role) => {
  return ROLE_MODE_MAP[role] || ROLE_MODE_MAP.CIVILIAN;
};

// Get features for a role
export const getRoleFeatures = (role) => {
  if (role === 'JUDGE') return JUDGE_NAV_FEATURES;
  return ROLE_FEATURES[role] || ROLE_FEATURES.CIVILIAN;
};

// Check if user has permission for a mode
export const hasModeAccess = (userRole, targetMode) => {
  const userMode = getModeForRole(userRole);
  return userMode === targetMode;
};

// Check if user has permission for a feature
export const hasFeatureAccess = (userRole, featureId) => {
  const features = getRoleFeatures(userRole);
  return features.some(f => f.id === featureId);
};
