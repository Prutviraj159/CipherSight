import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('bg-gradient-to-b from-[#d4f8ff] via-[#96d8ff] to-[#6da5ff] text-slate-900', 'bg-[#0B1120] text-slate-200')
style_insert = '''
  <style>
    .glass-panel { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(56, 189, 248, 0.2); }
    .neon-text { text-shadow: 0 0 10px rgba(56, 189, 248, 0.5); }
    .neon-border { box-shadow: 0 0 15px rgba(56, 189, 248, 0.2); }
    .sidebar { border-right: 1px solid rgba(255,255,255,0.05); background: #080C17; }
    .card-service { background: rgba(30, 41, 59, 0.4) !important; border: 1px solid rgba(255,255,255,0.1) !important; color: white !important; }
    .text-slate-900 { color: #f8fafc !important; }
    .text-slate-700 { color: #cbd5e1 !important; }
    .text-slate-500 { color: #94a3b8 !important; }
    .bg-white { background-color: #1e293b !important; }
    .bg-slate-50 { background-color: #0f172a !important; }
    .bg-slate-100 { background-color: #1e293b !important; }
    .border-slate-100, .border-slate-200 { border-color: rgba(255,255,255,0.1) !important; }
    .btn-check-blue { background: linear-gradient(135deg, #0ea5e9, #2563eb) !important; box-shadow: 0 0 15px rgba(14, 165, 233, 0.4); color: white !important;}
  </style>
'''
if '<style>' not in html:
    html = html.replace('</head>', style_insert + '</head>')

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

with open('frontend/app.v2.js', 'r', encoding='utf-8') as f:
    js = f.read()

js = js.replace('<div class="min-h-screen text-slate-900 flex flex-col font-sans pb-8">', '<div class="min-h-screen text-slate-200 flex flex-row font-sans">')
js = js.replace('<main class="flex-1 px-6 sm:px-10 py-6 max-w-7xl mx-auto w-full">', '<main class="flex-1 px-6 sm:px-10 py-8 w-full">')

sidebar_html = '''
function renderTopNavbar() {
  return 
    <aside class="w-64 sidebar min-h-screen p-6 flex flex-col gap-8 hidden md:flex">
      <div class="flex items-center gap-3">
        <img src="ciphersight_logo_no_bg.png" class="w-8 h-8" />
        <span class="font-bold text-xl text-white neon-text">CyberLens</span>
      </div>
      <nav class="flex flex-col gap-4">
        <button onclick="switchTab('scan-url')" class="flex items-center gap-3 p-3 rounded-xl  transition-all">
          <i data-lucide="shield-check" class="w-5 h-5"></i> <span>Scanner</span>
        </button>
        <button onclick="switchTab('check-file')" class="flex items-center gap-3 p-3 rounded-xl  transition-all">
          <i data-lucide="file-text" class="w-5 h-5"></i> <span>File Analysis</span>
        </button>
        <button onclick="switchTab('soc-intel')" class="flex items-center gap-3 p-3 rounded-xl  transition-all">
          <i data-lucide="database" class="w-5 h-5"></i> <span>Threat DB</span>
        </button>
      </nav>
      <div class="mt-auto p-4 rounded-xl glass-panel">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center font-bold text-white shadow-[0_0_10px_rgba(59,130,246,0.5)]">S</div>
          <div><p class="text-xs font-bold text-white">System Admin</p><p class="text-[10px] text-emerald-400 font-mono">Online</p></div>
        </div>
      </div>
    </aside>
  ;
}
'''

js = re.sub(r'function renderTopNavbar\(\) \{[\s\S]*?\}\s*// CIRCULAR RISK SCORE', sidebar_html + '\\n// CIRCULAR RISK SCORE', js)

with open('frontend/app.v2.js', 'w', encoding='utf-8') as f:
    f.write(js)
