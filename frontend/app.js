window.addEventListener('error', function(e) {
  document.body.innerHTML += '<div style="color:red; background:white; position:fixed; top:0; z-index:9999; padding: 10px; width: 100%; word-wrap: break-word;">Error: ' + e.message + ' at ' + e.filename + ':' + e.lineno + ':' + e.colno + '<br>Stack: ' + (e.error ? e.error.stack : '') + '</div>';
});
window.addEventListener('unhandledrejection', function(e) {
  document.body.innerHTML += '<div style="color:red; background:white; position:fixed; top:40px; z-index:9999; padding: 10px; width: 100%; word-wrap: break-word;">Promise Rejection: ' + e.reason + '<br>Stack: ' + (e.reason && e.reason.stack ? e.reason.stack : '') + '</div>';
});
/**
 * CyberLens AI — Clean Cybersecurity Scanner UI/UX Platform
 * Transparent Background Team CipherSight Logo (SIH Prototype CHA-046)
 */

// ==========================================
// 1. MOCK DATA STORE
// ==========================================

let MOCK_THREATS = [
  {
    id: 'DS-9481',
    domain: 'secure-login-example.com',
    detectedAt: '2 min ago',
    defcon: 'DEFCON 1',
    riskLevel: 'critical',
    probability: 94.7,
    target: 'Bank Login',
    status: 'PHISHING',
    ageDays: 5,
    visualSim: 96.4,
    ipAddress: '104.21.54.12',
    asn: 'AS12345 BulletProof Net',
  },
  {
    id: 'DS-9480',
    domain: 'account-verification-example.net',
    detectedAt: '8 min ago',
    defcon: 'DEFCON 2',
    riskLevel: 'high',
    probability: 87.2,
    target: 'Microsoft Login',
    status: 'PHISHING',
    ageDays: 3,
    visualSim: 91.8,
    ipAddress: '185.220.101.5',
    asn: 'AS8921 Offshore Server',
  },
  {
    id: 'DS-9479',
    domain: 'bank-security-check.org',
    detectedAt: '15 min ago',
    defcon: 'DEFCON 2',
    riskLevel: 'high',
    probability: 76.8,
    target: 'Example Bank',
    status: 'SUSPICIOUS',
    ageDays: 12,
    visualSim: 79.4,
    ipAddress: '194.26.29.112',
    asn: 'AS4412 Anonymous Host',
  },
  {
    id: 'DS-9478',
    domain: 'google-example-login.com',
    detectedAt: '24 min ago',
    defcon: 'DEFCON 1',
    riskLevel: 'critical',
    probability: 91.3,
    target: 'Google Workspace',
    status: 'PHISHING',
    ageDays: 2,
    visualSim: 94.1,
    ipAddress: '45.142.212.8',
    asn: 'AS12345 BulletProof Net',
  },
  {
    id: 'DS-9477',
    domain: 'example-safe.com',
    detectedAt: '35 min ago',
    defcon: 'DEFCON 4',
    riskLevel: 'safe',
    probability: 4.2,
    target: 'Verified Portal',
    status: 'SAFE',
    ageDays: 1420,
    visualSim: 5.1,
    ipAddress: '172.67.140.2',
    asn: 'AS13335 Cloudflare Inc',
  },
  {
    id: 'DS-9476',
    domain: 'sbi-yono-update.test',
    detectedAt: '42 min ago',
    defcon: 'DEFCON 1',
    riskLevel: 'critical',
    probability: 95.8,
    target: 'SBI Yono',
    status: 'PHISHING',
    ageDays: 1,
    visualSim: 93.7,
    ipAddress: '185.193.89.44',
    asn: 'AS9012 BulletProof Net',
  },
];

const MOCK_ANALYSIS_DATA = {
  'secure-example.com': {
    domain: 'secure-example.com',
    probability: 94.7,
    verdictLabel: 'LIKELY PHISHING',
    defcon: 'DEFCON 1 CRITICAL',
    riskLevel: 'critical',
    targetBrand: 'Microsoft Login',
    confidence: '99.4% Neural Certainty',
    
    breakdown: {
      domainRisk: 82,
      urlRisk: 76,
      contentRisk: 91,
      visualRisk: 96,
    },

    domainIntel: {
      domain: 'secure-example.com',
      created: '12 Aug 2026',
      ageDays: 5,
      registrar: 'NameCheap / Offshore Privacy Guard Ltd.',
      tld: '.com',
      https: true,
      nameservers: 2,
      riskStatus: 'HIGH RISK SIGNAL',
    },

    urlIntel: {
      length: 54,
      subdomains: 3,
      hyphens: 4,
      numbers: 2,
      suspiciousKeywords: 2,
      https: true,
      highlightedSegments: [
        { text: 'secure-', flag: true },
        { text: 'login-', flag: true },
        { text: 'verify-', flag: true },
        { text: 'example.com', flag: false },
      ]
    },

    contentIntel: {
      htmlSimilarity: 87,
      textSimilarity: 91,
      cssSimilarity: 82,
      formSimilarity: 89,
      overallSimilarity: 91,
      overallStatus: 'CRITICAL',
    },

    visualIntel: {
      similarityScore: 96.4,
      target: 'Microsoft Login',
      logoMatch: 94,
      layoutMatch: 91,
      colorMatch: 87,
      formMatch: 90,
      referenceTitle: 'Official Microsoft Account Sign-In',
      scannedTitle: 'Sign in to your Microsoft account',
    },

    infrastructure: {
      hostingProvider: 'Stark-Infrastructure Offshore Host',
      asn: 'AS12345',
      asnOrg: 'BulletProof Networks S.A.',
      ipAddress: '104.21.54.12',
      country: 'Bulgaria (BG)',
    },

    reasons: [
      { type: 'danger', title: '🔴 Recently Registered Domain (5 Days)', description: 'Domain registered 5 days ago via offshore privacy shield (Bulgaria BG).' },
      { type: 'danger', title: '🔴 High Visual Similarity (96.4%)', description: 'Computer vision neural model detected 96.4% layout match to Microsoft Login.' },
      { type: 'danger', title: '🔴 Suspicious URL Keyword Entropy', description: 'Multiple authentication tokens (secure, login, verify) detected in subdomains.' },
      { type: 'danger', title: '🔴 Untrusted Credential Collection Action', description: 'Form targets unverified PHP endpoint /api/collect_credentials.php.' },
      { type: 'safe', title: '🟢 HTTPS Certificate Active', description: 'Let\'s Encrypt TLS certificate active (Issued 5 days ago).' },
    ]
  }
};

// App Global State
let state = {
  activeTab: 'scan-url',
  scanInput: 'https://secure-example.com',
  isScanning: false,
  scanStep: 0,
  reportModalDomain: null,
};

// ==========================================
// 2. HELPER UI COMPONENTS
// ==========================================

function getRiskBadge(score, level) {
  const derived = level || (score >= 80 ? 'critical' : score >= 60 ? 'high' : score >= 30 ? 'medium' : 'safe');
  let style = '';
  let defconText = '';

  switch (derived) {
    case 'critical':
      style = 'bg-red-50 border-red-200 text-red-700 font-bold';
      defconText = 'DEFCON 1 CRITICAL';
      break;
    case 'high':
      style = 'bg-orange-50 border-orange-200 text-orange-700 font-bold';
      defconText = 'DEFCON 2 HIGH';
      break;
    case 'medium':
      style = 'bg-amber-50 border-amber-200 text-amber-700 font-bold';
      defconText = 'DEFCON 3 MEDIUM';
      break;
    default:
      style = 'bg-emerald-50 border-emerald-200 text-emerald-700 font-bold';
      defconText = 'DEFCON 4 SAFE';
      break;
  }

  return `
    <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono border ${style}">
      <span class="w-2 h-2 rounded-full ${derived === 'critical' ? 'bg-red-500 animate-pulse' : 'bg-current'}"></span>
      <span>${score}% ${defconText}</span>
    </span>
  `;
}

// TOP NAVBAR WITH TRANSPARENT LOGO
function renderTopNavbar() {
  const active = state.activeTab;

  return `
    <header class="py-4 px-6 sm:px-10 flex items-center justify-between max-w-7xl mx-auto w-full">
      <!-- Left Brand Logo -->
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-2xl bg-slate-900 border border-slate-700/60 p-1 text-cyan-400 flex items-center justify-center shadow-lg">
          <img src="ciphersight_logo_no_bg.png" alt="Team CipherSight Logo" class="w-full h-full object-contain">
        </div>
        <span class="font-extrabold text-xl text-slate-900 tracking-tight">CyberLens AI</span>
      </div>

      <!-- Center Navigation Pills -->
      <div class="flex items-center gap-1.5 bg-white/40 p-1.5 rounded-2xl backdrop-blur-md border border-white/60 shadow-sm">
        <button
          onclick="switchTab('scan-url')"
          class="nav-pill ${active === 'scan-url' ? 'active' : ''}"
        >
          <i data-lucide="shield-check" class="w-4 h-4 ${active === 'scan-url' ? 'text-[#4361ee]' : 'text-slate-700'}"></i>
          <span>Scan URL</span>
        </button>

        <button
          onclick="switchTab('check-file')"
          class="nav-pill ${active === 'check-file' ? 'active' : ''}"
        >
          <i data-lucide="file-text" class="w-4 h-4 ${active === 'check-file' ? 'text-[#4361ee]' : 'text-slate-700'}"></i>
          <span>Check File</span>
        </button>

        <button
          onclick="switchTab('soc-intel')"
          class="nav-pill ${active === 'soc-intel' ? 'active' : ''}"
        >
          <i data-lucide="database" class="w-4 h-4 ${active === 'soc-intel' ? 'text-[#4361ee]' : 'text-slate-700'}"></i>
          <span>Threat Database</span>
        </button>

        <!-- User Profile Pill -->
        <button class="w-9 h-9 rounded-xl bg-indigo-500/20 text-[#4361ee] flex items-center justify-center hover:bg-indigo-500/30 transition-colors ml-1">
          <i data-lucide="user" class="w-5 h-5"></i>
        </button>
      </div>

      <!-- Right Action Button -->
      <button
        onclick="switchTab('soc-intel')"
        class="px-5 py-2.5 rounded-xl btn-dashboard text-white font-extrabold text-sm flex items-center gap-2 shadow-md"
      >
        <i data-lucide="layout-grid" class="w-4 h-4"></i>
        <span>Dashboard</span>
      </button>
    </header>
  `;
}

// CIRCULAR RISK SCORE GAUGE & VISUAL DETAILS
function renderRightCircleGraphCard() {
  const scan = window.SCAN_DATA && window.SCAN_DATA[state.scanInput.replace(/^https?:\/\//, "").replace(/\/$/, "")];
  const mapped = scan ? window.scanMapper.mapScanResponse(scan) : null;
  const targetScore = mapped && mapped.riskScore !== "N/A" ? mapped.riskScore * 100 : 0;
  const currentStep = state.scanStep;
  const currentScore = Math.min(targetScore, (currentStep / 8) * targetScore).toFixed(1);
  const strokeDash = 251.2;
  const strokeOffset = strokeDash - (strokeDash * currentScore) / 100;

  return `
    <div class="card-service p-5 space-y-4 shadow-md border-red-200">
      <div class="flex items-center justify-between pb-2 border-b border-slate-100">
        <h3 class="text-xs font-extrabold text-slate-900 flex items-center gap-1.5">
          <i data-lucide="pie-chart" class="w-4 h-4 text-red-500"></i> Visual Risk Analytics
        </h3>
        <span class="text-[10px] font-mono font-bold px-2 py-0.5 rounded ${mapped && mapped.riskLevel === 'critical' ? 'bg-red-50 border border-red-200 text-red-600' : 'bg-slate-50 border border-slate-200 text-slate-600'}">${mapped && mapped.riskLevel === 'critical' ? 'DEFCON 1' : 'DEFCON 3'}</span>
      </div>

      <!-- Circular Donut Graph Gauge -->
      <div class="relative w-32 h-32 mx-auto flex items-center justify-center my-1">
        <svg class="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="40" stroke="#f1f5f9" stroke-width="9" fill="transparent" />
          <circle
            cx="50"
            cy="50"
            r="40"
            stroke="#ef4444"
            stroke-width="9"
            stroke-linecap="round"
            fill="transparent"
            stroke-dasharray="251.2"
            stroke-dashoffset="${strokeOffset}"
            class="transition-all duration-500 ease-out"
          />
        </svg>
        <div class="absolute flex flex-col items-center justify-center text-center">
          <span class="text-xl font-extrabold text-red-600 font-mono tracking-tight">${currentScore}%</span>
          <span class="text-[9px] font-bold text-slate-400 uppercase tracking-widest">Risk Score</span>
        </div>
      </div>

      <!-- Visual Breakdown Details Bars -->
      <div class="space-y-2.5 font-mono text-[11px]">
        <div>
          <div class="flex justify-between text-slate-600 mb-0.5">
            <span>Visual Similarity</span>
            <strong class="text-red-600 font-bold">96.4%</strong>
          </div>
          <div class="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
            <div class="h-full bg-red-500 rounded-full" style="width: 96.4%"></div>
          </div>
          <div class="text-[9px] text-slate-400 mt-0.5 font-sans">Target: Microsoft Login</div>
        </div>

        <div>
          <div class="flex justify-between text-slate-600 mb-0.5">
            <span>Content & Form</span>
            <strong class="text-red-600 font-bold">91.0%</strong>
          </div>
          <div class="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
            <div class="h-full bg-red-500 rounded-full" style="width: 91%"></div>
          </div>
        </div>

        <div>
          <div class="flex justify-between text-slate-600 mb-0.5">
            <span>Domain Age Risk</span>
            <strong class="text-orange-600 font-bold">82.0%</strong>
          </div>
          <div class="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
            <div class="h-full bg-orange-500 rounded-full" style="width: 82%"></div>
          </div>
          <div class="text-[9px] text-slate-400 mt-0.5 font-sans">5 Days Old (Bulgaria BG)</div>
        </div>

        <div>
          <div class="flex justify-between text-slate-600 mb-0.5">
            <span>URL Entropy</span>
            <strong class="text-amber-600 font-bold">76.0%</strong>
          </div>
          <div class="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
            <div class="h-full bg-amber-500 rounded-full" style="width: 76%"></div>
          </div>
        </div>
      </div>
    </div>
  `;
}

// ==========================================
// 3. MAIN DASHBOARD CONTENT
// ==========================================

function renderScanURLView() {
  const steps = [
    { title: 'DOMAIN', status: state.scanStep >= 1 ? 'completed' : state.scanStep === 0 && state.isScanning ? 'active' : 'pending' },
    { title: 'RDAP / WHOIS', status: state.scanStep >= 2 ? 'completed' : state.scanStep === 1 ? 'active' : 'pending' },
    { title: 'URL ANALYSIS', status: state.scanStep >= 3 ? 'completed' : state.scanStep === 2 ? 'active' : 'pending' },
    { title: 'HTML / CONTENT', status: state.scanStep >= 4 ? 'completed' : state.scanStep === 3 ? 'active' : 'pending' },
    { title: 'SCREENSHOT', status: state.scanStep >= 5 ? 'completed' : state.scanStep === 4 ? 'active' : 'pending' },
    { title: 'VISUAL SIMILARITY', status: state.scanStep >= 6 ? 'completed' : state.scanStep === 5 ? 'active' : 'pending' },
    { title: 'AI RISK ENGINE', status: state.scanStep >= 7 ? 'completed' : state.scanStep === 6 ? 'active' : 'pending' },
    { title: 'FINAL VERDICT', status: state.scanStep >= 8 ? 'completed' : state.scanStep === 7 ? 'active' : 'pending' },
  ];

  return `
    <div class="flex flex-col lg:flex-row items-start justify-between gap-6 max-w-7xl mx-auto w-full">
      
      <!-- LEFT COLUMN: DETAILED ANALYSIS SERVICES (310px Fixed Width) -->
      <div class="w-full lg:w-[310px] shrink-0 glass-panel p-5 space-y-4">
        <h2 class="text-base font-extrabold text-slate-900 tracking-tight">Detailed Analysis services</h2>

        <!-- Card 1: Phishing Check -->
        <div class="card-service p-4 space-y-2.5">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-xl bg-sky-50 border border-sky-200 text-sky-600 flex items-center justify-center shrink-0">
              <i data-lucide="mail" class="w-4 h-4"></i>
            </div>
            <h3 class="font-extrabold text-slate-900 text-sm">Phishing Check</h3>
          </div>
          <p class="text-slate-600 text-xs leading-relaxed">
            Phishing, Credential Theft, and Zero-Day detection. Advanced algorithmic matching.
          </p>
          <div class="pt-2 border-t border-slate-100 text-[10px] font-mono text-slate-500 space-y-1">
            <div class="font-bold text-slate-700">Threat Map Legend</div>
            <div class="flex items-center gap-3">
              <span class="flex items-center gap-1 text-emerald-600"><span class="w-2 h-2 rounded-full bg-emerald-500"></span> Threat Point</span>
              <span class="flex items-center gap-1 text-red-600"><span class="w-2 h-2 rounded-full bg-red-500"></span> Malware Point</span>
            </div>
          </div>
        </div>

        <!-- Card 2: Malware Scan -->
        <div class="card-service p-4 space-y-2.5">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-xl bg-sky-50 border border-sky-200 text-sky-600 flex items-center justify-center shrink-0">
              <i data-lucide="cpu" class="w-4 h-4"></i>
            </div>
            <h3 class="font-extrabold text-slate-900 text-sm">Malware Scan</h3>
          </div>
          <p class="text-slate-600 text-xs leading-relaxed">
            Static and Dynamic file analysis. Heuristic scanning of all links and downloads.
          </p>
          <div class="pt-2 border-t border-slate-100 text-[10px] font-mono text-slate-500 space-y-0.5">
            <div class="font-bold text-slate-700">Scan History</div>
            <div class="text-slate-400 truncate">Scan History: -snippet: 31 2018-04 ...</div>
          </div>
        </div>

        <!-- Card 3: Brand Impersonation -->
        <div class="card-service p-4 space-y-2.5">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-xl bg-purple-50 border border-purple-200 text-purple-600 flex items-center justify-center shrink-0">
              <i data-lucide="user-x" class="w-4 h-4"></i>
            </div>
            <h3 class="font-extrabold text-slate-900 text-sm">Brand Impersonation</h3>
          </div>
          <p class="text-slate-600 text-xs leading-relaxed">
            AI-powered detection of lookalike domains and brand spoofing. Global patent-pending technology.
          </p>
          <div class="pt-2 border-t border-slate-100 text-[10px] font-mono text-slate-500 flex items-center justify-between">
            <span class="font-bold text-slate-700">Domain Reputation Score:</span>
            <span class="font-extrabold text-indigo-600">80</span>
          </div>
        </div>

        <!-- RECTANGLE 1: RESET BUTTON -->
        ${(state.isScanning || state.scanStep > 0) ? `
          <button
            onclick="handleResetScan()"
            class="w-full py-3.5 px-4 rounded-2xl bg-white/90 hover:bg-white text-slate-700 hover:text-slate-900 border border-slate-300/80 font-extrabold text-sm flex items-center justify-center gap-2 shadow-sm transition-all hover:scale-[1.02]"
          >
            <i data-lucide="rotate-ccw" class="w-4 h-4 text-slate-600"></i>
            <span>Reset Scanner</span>
          </button>
        ` : ''}

      </div>

      <!-- CENTER COLUMN: MAIN DARK SCANNER CARD + PIPELINE (Flex-1) -->
      <div class="flex-1 w-full min-w-0 space-y-6">
        
        <!-- Dark Obsidian Scanner Card -->
        <div class="dark-scanner-card p-6 flex flex-col md:flex-row items-center justify-between gap-6">
          <!-- Left Input Form & Button -->
          <div class="flex-1 w-full space-y-4">
            <form onsubmit="handleQuickScan(event)" class="space-y-3.5">
              <!-- URL Input Field -->
              <div>
                <input
                  type="text"
                  id="quick-scan-input"
                  value="${state.scanInput}"
                  placeholder="https://secure-example.com"
                  class="w-full px-4 py-3 rounded-2xl bg-white text-slate-900 placeholder-slate-400 font-sans text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
                />
              </div>

              <!-- Check Now Pill Button -->
              <button
                type="submit"
                class="w-full py-3.5 rounded-full btn-check-blue text-white font-extrabold text-base tracking-wide shadow-md"
              >
                <span>${state.isScanning ? 'Scanning...' : 'Check Now'}</span>
              </button>

              <!-- Green Glowing Subtitle -->
              <div class="text-center font-mono text-xs text-emerald-400 font-bold tracking-wide">
                AI Protection Active
              </div>
            </form>
          </div>

          <!-- Right Transparent Logo Unit -->
          <div class="shrink-0 flex flex-col items-center justify-center space-y-2 p-3.5 rounded-2xl bg-slate-950/80 border border-slate-800/80 w-36 text-center shadow-lg">
            <div class="w-24 h-16 relative flex items-center justify-center">
              <img src="ciphersight_logo_no_bg.png" alt="Team CipherSight Logo" class="w-full h-full object-contain drop-shadow-[0_0_12px_rgba(0,240,255,0.4)]">
            </div>
            <span class="text-[11px] font-mono font-bold text-cyan-400">Team CipherSight</span>
          </div>
        </div>

        <!-- In-Page Inspection Pipeline (Expands underneath) -->
        <div id="home-scan-container" class="space-y-6 font-mono">
          ${(state.isScanning || state.scanStep > 0) ? `
            <div class="space-y-6 pt-2">
              
              <div class="text-center space-y-1">
                <h2 class="text-lg font-extrabold text-slate-900 flex items-center justify-center gap-2">
                  <i data-lucide="crosshair" class="w-5 h-5 text-[#4361ee]"></i> Domain Security Inspection
                </h2>
                <p class="text-xs text-slate-600">
                  Multi-stage AI pipeline execution for: <span class="text-[#4361ee] font-bold">${state.scanInput}</span>
                </p>
              </div>

              <!-- Clean 8-Stage Execution Card -->
              <div class="card-service p-6 space-y-5 text-center">
                <div class="text-xs font-bold text-slate-500 uppercase tracking-widest">
                  LIVE PIPELINE EXECUTION STATUS
                </div>

                <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center text-xs">
                  ${steps.map((s, idx) => `
                    <div class="p-3 rounded-2xl border transition-all ${
                      s.status === 'completed'
                        ? 'bg-emerald-50 border-emerald-200 text-emerald-700 font-extrabold shadow-sm'
                        : s.status === 'active'
                        ? 'bg-blue-50 border-blue-400 text-blue-700 font-extrabold animate-pulse'
                        : 'bg-slate-50 border-slate-200 text-slate-400'
                    }">
                      <div class="text-[10px] text-slate-400 mb-0.5">STAGE 0${idx + 1}</div>
                      <div class="font-extrabold text-xs flex items-center justify-center gap-1.5">
                        ${s.status === 'completed' ? '<i data-lucide="check" class="w-3.5 h-3.5 text-emerald-600"></i>' : ''}
                        ${s.status === 'active' ? '<i data-lucide="loader-2" class="w-3.5 h-3.5 text-[#4361ee] animate-spin"></i>' : ''}
                        <span>${s.title}</span>
                      </div>
                    </div>
                  `).join('')}
                </div>
              </div>

              <!-- Telemetry Stream Ticker -->
              <div class="card-service p-4 space-y-1.5 text-xs text-left">
                <div class="flex items-center justify-between pb-2 border-b border-slate-100 text-[#4361ee] font-bold text-xs">
                  <span class="flex items-center gap-2">
                    <i data-lucide="terminal" class="w-4 h-4 text-[#4361ee]"></i> Telemetry Log Stream
                  </span>
                  <span class="text-slate-500 text-[10px]">${state.isScanning ? 'Streaming logs...' : 'Complete'}</span>
                </div>
                <div class="${state.scanStep >= 1 ? 'text-emerald-700 font-semibold' : 'text-slate-400'}">✓ [0x1A] Domain discovered & DNS A records resolved</div>
                <div class="${state.scanStep >= 2 ? 'text-emerald-700 font-semibold' : 'text-slate-400'}">✓ [0x1B] RDAP / WHOIS parsed (Domain age: 5 Days)</div>
                <div class="${state.scanStep >= 3 ? 'text-emerald-700 font-semibold' : 'text-slate-400'}">✓ [0x1C] URL entropy analyzed (Suspicious keywords detected)</div>
                <div class="${state.scanStep >= 4 ? 'text-emerald-700 font-semibold' : 'text-slate-400'}">✓ [0x1D] HTML DOM extracted (Untrusted form endpoint /api/collect.php)</div>
                <div class="${state.scanStep >= 5 ? 'text-emerald-700 font-semibold' : 'text-slate-400'}">✓ [0x1E] Headless screenshot captured</div>
                <div class="${state.scanStep >= 6 ? 'text-emerald-700 font-semibold' : 'text-slate-400'}">✓ [0x1F] Computer vision matching 96.4% match to Microsoft Login</div>
                <div class="${state.scanStep >= 7 ? 'text-emerald-700 font-semibold' : 'text-slate-400'}">✓ [0x20] Neural risk model scoring finished</div>
              </div>

            </div>
          ` : ''}
        </div>

      </div>

      <!-- RIGHT COLUMN: STATUS SUMMARY PANEL (270px Fixed Width) -->
      <div class="w-full lg:w-[270px] shrink-0 glass-panel p-5 space-y-4">
        
        <!-- Card 1: Status: Safe -->
        <div class="card-service p-4 space-y-2">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-600 flex items-center justify-center shrink-0">
              <i data-lucide="check-circle-2" class="w-5 h-5 text-emerald-600"></i>
            </div>
            <div>
              <h3 class="font-extrabold text-slate-900 text-sm leading-tight">Status: Safe</h3>
              <div class="text-xs text-slate-500">Website is safe</div>
            </div>
          </div>
          <div class="text-[10px] font-mono text-slate-400 pt-1 border-t border-slate-100">
            <strong>Data:</strong> Inreactive data
          </div>
        </div>

        <!-- Card 2: Status: High Risk -->
        <div class="card-service p-4 space-y-2">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-xl bg-red-50 border border-red-200 text-red-600 flex items-center justify-center shrink-0">
              <i data-lucide="alert-octagon" class="w-5 h-5 text-red-600"></i>
            </div>
            <div>
              <h3 class="font-extrabold text-slate-900 text-sm leading-tight">Status: High Risk</h3>
              <div class="text-xs text-red-600 font-bold">Phishing/Malware Detected</div>
            </div>
          </div>
          <div class="text-[10px] font-mono text-slate-400 pt-1 border-t border-slate-100">
            <strong>Data:</strong> High Risk
          </div>
        </div>

        <!-- CIRCLE GRAPH & VISUAL DETAILS CARD -->
        ${(state.isScanning || state.scanStep > 0) ? renderRightCircleGraphCard() : ''}

        <!-- RECTANGLE 2: VIEW REPORT BUTTON -->
        ${(state.isScanning || state.scanStep > 0) ? `
          <button
            onclick="openReportModal('secure-example.com')"
            class="w-full py-3.5 px-4 rounded-2xl btn-check-blue text-white font-extrabold text-sm flex items-center justify-center gap-2 shadow-md transition-all hover:scale-[1.02]"
          >
            <i data-lucide="file-text" class="w-4 h-4 text-white"></i>
            <span>View Report</span>
          </button>
        ` : ''}

      </div>

    </div>
  `;
}

function renderCheckFileView() {
  return `
    <div class="max-w-3xl mx-auto py-8 card-service p-8 space-y-6 text-center">
      <div class="w-16 h-16 rounded-3xl bg-sky-50 border border-sky-200 text-[#4361ee] flex items-center justify-center mx-auto">
        <i data-lucide="upload-cloud" class="w-8 h-8"></i>
      </div>
      <div class="space-y-2">
        <h2 class="text-2xl font-extrabold text-slate-900">Upload File for Threat Inspection</h2>
        <p class="text-slate-600 text-xs font-sans max-w-md mx-auto">
          Drag and drop suspicious HTML, EML, PDF, or executable files to inspect embedded malicious links and phishing scripts.
        </p>
      </div>

      <div class="border-2 border-dashed border-blue-300 rounded-2xl p-10 bg-slate-50/50 hover:bg-slate-50 transition-colors cursor-pointer space-y-3">
        <i data-lucide="file-up" class="w-10 h-10 text-blue-400 mx-auto"></i>
        <div class="text-xs text-slate-700 font-medium">
          <span class="text-[#4361ee] font-bold">Click to browse</span> or drop file here
        </div>
        <div class="text-[10px] text-slate-500 font-mono">Max size: 25MB (HTML, EML, PDF, EXE)</div>
      </div>
    </div>
  `;
}

function renderSOCIntelView() {
  return `
    <div class="max-w-6xl mx-auto py-4 card-service p-6 space-y-4 font-mono text-xs">
      <div class="flex items-center justify-between pb-3 border-b border-slate-100">
        <h3 class="text-sm font-extrabold text-slate-900 flex items-center gap-2">
          <i data-lucide="database" class="w-4 h-4 text-[#4361ee]"></i> Threat Intelligence Database
        </h3>
        <span class="text-slate-500 text-[11px]">Real-time Threat Feed</span>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="text-slate-600 uppercase text-[10px] border-b border-slate-200 bg-slate-50">
              <th class="py-3 px-3">Domain</th>
              <th class="py-3 px-3">Age</th>
              <th class="py-3 px-3">Risk Level</th>
              <th class="py-3 px-3">Visual Match</th>
              <th class="py-3 px-3">Target</th>
              <th class="py-3 px-3 text-right">Verdict</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            ${MOCK_THREATS.map(t => `
              <tr class="hover:bg-slate-50 transition-colors cursor-pointer" onclick="openReportModal('${t.domain}')">
                <td class="py-3 px-3 font-bold text-slate-900">${t.domain}</td>
                <td class="py-3 px-3 text-slate-500">${t.ageDays} days</td>
                <td class="py-3 px-3">${getRiskBadge(t.probability, t.riskLevel)}</td>
                <td class="py-3 px-3 text-[#4361ee] font-bold">${t.visualSim}%</td>
                <td class="py-3 px-3 text-slate-700 font-sans">${t.target}</td>
                <td class="py-3 px-3 text-right font-bold text-red-600">${t.status}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

// Router & Event Handlers
function switchTab(tabId) {
  state.activeTab = tabId;
  router();
}

function router() {
  const app = document.getElementById('app');
  let content = '';

  switch (state.activeTab) {
    case 'check-file':
      content = renderCheckFileView();
      break;
    case 'soc-intel':
      content = renderSOCIntelView();
      break;
    case 'scan-url':
    default:
      content = renderScanURLView();
      break;
  }

  app.innerHTML = `
    <div class="min-h-screen text-slate-900 flex flex-col font-sans pb-8">
      <!-- TOP NAVBAR -->
      ${renderTopNavbar()}

      <!-- MAIN CONTENT VIEW -->
      <main class="flex-1 px-6 sm:px-10 py-6 max-w-7xl mx-auto w-full">
        ${content}
      </main>
    </div>

    ${state.reportModalDomain ? renderReportModalHTML(state.reportModalDomain) : ''}
  `;

  if (window.lucide) {
    window.lucide.createIcons();
  }
}

function handleQuickScan(e) {
  e.preventDefault();
  const val = document.getElementById('quick-scan-input')?.value || 'https://secure-example.com';
  state.scanInput = val;
  startScanAnimation();
}

function handleResetScan() {
  state.isScanning = false;
  state.scanStep = 0;
  state.scanInput = 'https://secure-example.com';
  router();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function startScanAnimation() {
  state.isScanning = true;
  state.scanStep = 0;
  router();

  setTimeout(() => {
    const scanContainer = document.getElementById('home-scan-container');
    if (scanContainer) {
      scanContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }, 50);

  const interval = setInterval(() => {
    state.scanStep += 1;
    router();

    if (state.scanStep >= 8) {
      clearInterval(interval);
      state.isScanning = false;
    }
  }, 350);
}

function openReportModal(domain) {
  state.reportModalDomain = domain;
  router();
}

function closeReportModal() {
  state.reportModalDomain = null;
  router();
}

function renderReportModalHTML(domain) {
    const scan = window.SCAN_DATA && window.SCAN_DATA[domain];
  if (!scan) return '<div>No data</div>';
  const riskPercent = (scan.risk_score * 100).toFixed(1);
  const verdictLabel = scan.status.toUpperCase() === 'NEEDS_REVIEW' ? scan.risk_level.toUpperCase() : scan.status.toUpperCase();
  const data = {
    reasons: scan.explanation.map(e => ({title: e.signal + ': ' + e.detail}))
  };

  return `
    <div class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="w-full max-w-xl card-service p-8 space-y-6 font-mono text-xs">
        <div class="flex justify-between items-center border-b border-slate-100 pb-4">
          <h4 class="font-extrabold text-slate-900 text-base flex items-center gap-2">
            <i data-lucide="file-text" class="w-5 h-5 text-[#4361ee]"></i> Security Report: ${domain}
          </h4>
          <button onclick="closeReportModal()" class="text-slate-400 hover:text-slate-700 text-lg font-bold">&times;</button>
        </div>

        <div class="grid grid-cols-2 gap-4 text-slate-700">
          <div class="p-3 rounded-xl bg-slate-50 border border-slate-200">
            <span class="text-slate-400 block text-[10px]">VERDICT</span>
            <strong class="text-red-600 font-bold text-sm">${riskPercent}% ${verdictLabel}</strong>
          </div>
          <div class="p-3 rounded-xl bg-slate-50 border border-slate-200">
            <span class="text-slate-400 block text-[10px]">VISUAL MATCH</span>
            <strong class="text-emerald-600 font-bold text-sm">${scan.target_brand ? scan.target_brand.name : 'Unknown'}</strong>
          </div>
        </div>

        <div class="space-y-2">
          <div class="font-bold text-slate-900 text-xs">Explainable AI Audit:</div>
          ${data.reasons.map(r => `
            <div class="p-3 rounded-xl bg-slate-50 border border-slate-200 text-slate-700 text-[11px]">
              ${r.title}
            </div>
          `).join('')}
        </div>

        <div class="flex gap-3 pt-2">
          <a
            href="data:text/json;charset=utf-8,${encodeURIComponent(JSON.stringify(MOCK_ANALYSIS_DATA['secure-example.com'], null, 2))}"
            download="CyberLens-report-${domain}.json"
            class="flex-1 py-3 btn-check-blue font-bold rounded-xl text-center shadow-sm text-xs"
          >
            Download JSON Dossier
          </a>
          <button onclick="closeReportModal()" class="px-5 py-3 bg-slate-100 hover:bg-slate-200 rounded-xl text-slate-700 font-bold text-xs">Close</button>
        </div>
      </div>
    </div>
  `;
}

window.addEventListener('load', () => {
  router();
});

// === BACKEND INTEGRATION ===
window.BACKEND_TOKEN = null;

async function initBackend() {
    const API = window.ENV.API_BASE_URL;
    try {
        const authRes = await fetch(API + '/auth/token?username=admin&password=change-me', {method: 'POST'});
        const authData = await authRes.json();
        window.BACKEND_TOKEN = authData.access_token;
        console.log("Logged in to Backend!", authData);

        const brandsRes = await fetch(API + '/brands', {headers: {Authorization: 'Bearer ' + window.BACKEND_TOKEN}});
        const brands = await brandsRes.json();
        console.log("Brands loaded:", brands);

        const scansRes = await fetch(API + '/scans', {headers: {Authorization: 'Bearer ' + window.BACKEND_TOKEN}});
        const scans = await scansRes.json();
        window.SCAN_DATA = {};
        scans.forEach(s => window.SCAN_DATA[s.normalized_domain] = s);
        
        MOCK_THREATS = scans.map(scan => {
            const mapped = window.scanMapper.mapScanResponse(scan);
            return {
                id: 'DS-' + mapped.scanId,
                domain: mapped.domain,
                detectedAt: mapped.createdAt,
                defcon: mapped.riskLevel === 'critical' ? 'DEFCON 1' : 'DEFCON 3',
                riskLevel: mapped.riskLevel,
                probability: mapped.riskScore !== 'N/A' ? mapped.riskScore * 100 : 0,
                target: mapped.targetBrand ? mapped.targetBrand.name : 'Unknown',
                status: mapped.verdict,
                ageDays: mapped.domainAge,
                visualSim: mapped.visualMatch !== 'N/A' ? (mapped.visualMatch * 100).toFixed(1) : 'N/A'
            };
        });
        router();
    } catch(e) {
        console.error("Backend integration failed", e);
    }
}

const originalHandleQuickScan = handleQuickScan;
window.handleQuickScan = async function(e) {
    e.preventDefault();
    const val = document.getElementById('quick-scan-input')?.value || 'https://secure-example.com';
    state.scanInput = val;
    startScanAnimation();
    
    if (window.BACKEND_TOKEN) {
        try {
            await fetch(window.ENV.API_BASE_URL + '/scans', {
                method: 'POST',
                headers: {
                    'Authorization': 'Bearer ' + window.BACKEND_TOKEN,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: val, enrichment: {} })
            });
            setTimeout(initBackend, 1500); 
        } catch(e) {
            console.error("Scan submission failed", e);
        }
    }
}

document.addEventListener('DOMContentLoaded', initBackend);









