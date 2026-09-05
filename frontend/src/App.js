import { BrowserRouter, Routes, Route } from "react-router-dom";

import { AuthProvider } from "./context/AuthContext";
import { ModeProvider } from "./context/ModeContext";

import AuthLayout from "./layouts/AuthLayout";
import MainLayout from "./layouts/MainLayout";
import ModeLayout from "./layouts/ModeLayout";

import ProtectedRoute from "./components/ProtectedRoute";
import RoleRedirect from "./components/RoleRedirect";

import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import ModeSelectionPage from "./pages/ModeSelectionPage";
import JudgmentComparisonPage from "./pages/JudgmentComparisonPage";
import JudgeRoute from "./components/JudgeRoute";
import LawyerRoute from "./components/LawyerRoute";
import { JudgeJudgmentComparisonPage, JudgePrecedentAnalysisPage, JudgeLegalReasoningPage, JudgeCaseLawSynthesisPage } from "./pages/judge/JudicialIntelligencePages";

import RepositoryPage from "./pages/RepositoryPage";
import UploadPage from "./pages/UploadPage";
import CaseResearchUploadPage from "./pages/CaseResearchUploadPage";

import ResearchPage from "./pages/ResearchPage";
import CaseDetailPage from "./pages/CaseDetailPage";

import CitizenAskQuestionPage from "./pages/citizen/CitizenAskQuestionPage";
import CitizenLegalResearchPage from "./pages/citizen/CitizenLegalResearchPage";
import CitizenLegalRepositoryPage from "./pages/citizen/CitizenLegalRepositoryPage";
import CitizenCaseAnalysisPage from "./pages/citizen/CitizenCaseAnalysisPage";
import AdvancedResearch from "./pages/lawyer/AdvancedResearch";
import ArgumentResearch from "./pages/lawyer/ArgumentResearch";
import CitationFinder from "./pages/lawyer/CitationFinder";
import CaseBriefGenerator from "./pages/lawyer/CaseBriefGenerator";

import NotFoundPage from "./pages/NotFoundPage";



export default function App(){


return (

<AuthProvider>

<ModeProvider>


<BrowserRouter>


<Routes>



{/* PUBLIC */}

<Route element={<MainLayout />}>

<Route
path="/"
element={<HomePage />}
/>

</Route>





{/* AUTH */}

<Route element={<AuthLayout />}>

<Route
path="/login"
element={<LoginPage />}
/>


<Route
path="/register"
element={<RegisterPage />}
/>


</Route>





{/* DASHBOARD - Role-based */}

<Route element={<ModeLayout />}>

<Route path="/judge/judgment-comparison" element={<JudgeRoute><JudgeJudgmentComparisonPage /></JudgeRoute>} />
<Route path="/judge/precedent-analysis" element={<JudgeRoute><JudgePrecedentAnalysisPage /></JudgeRoute>} />
<Route path="/judge/legal-reasoning" element={<JudgeRoute><JudgeLegalReasoningPage /></JudgeRoute>} />
<Route path="/judge/case-law-synthesis" element={<JudgeRoute><JudgeCaseLawSynthesisPage /></JudgeRoute>} />
<Route path="/lawyer/dashboard" element={<LawyerRoute><DashboardPage /></LawyerRoute>} />
<Route path="/lawyer/advanced-research" element={<LawyerRoute><AdvancedResearch /></LawyerRoute>} />
<Route path="/lawyer/argument-research" element={<LawyerRoute><ArgumentResearch /></LawyerRoute>} />
<Route path="/lawyer/citation-finder" element={<LawyerRoute><CitationFinder /></LawyerRoute>} />
<Route path="/lawyer/case-brief-generation" element={<LawyerRoute><CaseBriefGenerator /></LawyerRoute>} />
<Route
path="/dashboard"
element={
<ProtectedRoute>
<DashboardPage />
</ProtectedRoute>
}
/>
</Route>



{/* MODE SELECTION */}

<Route
path="/select-mode"
element={<ModeSelectionPage />}
/>



{/* PROTECTED */}

<Route element={<ModeLayout />}>



<Route

path="/repository"

element={

<ProtectedRoute>

<RepositoryPage />

</ProtectedRoute>

}

/>





<Route

path="/upload"

element={

<ProtectedRoute>

<UploadPage />

</ProtectedRoute>

}

/>





<Route

path="/case-research-upload"

element={

<ProtectedRoute>

<CaseResearchUploadPage />

</ProtectedRoute>

}

/>





{/* MODULE 3 */}

<Route

path="/research"

element={

<ProtectedRoute>

<ResearchPage />

</ProtectedRoute>

}

/>



<Route

path="/research/case/:id"

element={

<ProtectedRoute>

<CaseDetailPage />

</ProtectedRoute>

}

/>



{/* Judgment Comparison */}

<Route

path="/compare-judgments"

element={

<ProtectedRoute>

<JudgmentComparisonPage />

</ProtectedRoute>

}

/>


{/* Citizen Routes */}

<Route path="/citizen/ask-question" element={<ProtectedRoute><CitizenAskQuestionPage /></ProtectedRoute>} />
<Route path="/citizen/legal-research" element={<ProtectedRoute><CitizenLegalResearchPage /></ProtectedRoute>} />
<Route path="/citizen/legal-repository" element={<ProtectedRoute><CitizenLegalRepositoryPage /></ProtectedRoute>} />
<Route path="/citizen/case-analysis" element={<ProtectedRoute><CitizenCaseAnalysisPage /></ProtectedRoute>} />


</Route>





<Route

path="*"

element={<NotFoundPage />}

/>



</Routes>


</BrowserRouter>


</ModeProvider>


</AuthProvider>


);

}
