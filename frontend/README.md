# CyberLens AI — Smart India Hackathon (SIH 2026 CHA-046)

**AI/ML Phishing Domain Detection using WHOIS/RDAP + Visual Similarity**

CyberLens AI is a cybersecurity solution built for SIH Problem Statement **CHA-046**. It combines domain registration intelligence (WHOIS/RDAP), URL entropy analysis, HTML content extraction, and computer vision layout similarity matching to protect users from lookalike phishing portals.

---

## 🌟 Key Features

- **Top Navigation Bar**: Brand identity (`CyberLens AI`), navigation pills (`Scan URL`, `Check File`, `Threat Database`, `Profile`), and `Dashboard` button.
- **Left Panel (Detailed Analysis Services)**:
  - **Phishing Check**: Credential theft & zero-day detection.
  - **Malware Scan**: Static and dynamic heuristic analysis.
  - **Brand Impersonation**: Lookalike domain & brand spoofing detection.
  - **Reset Scanner Button**: Resets scanning state cleanly.
- **Center Panel (Main Scanner Box)**:
  - Dark obsidian navy scanner card (`#111827`).
  - URL scanner input field (`https://secure-example.com`) and vibrant blue **Check Now** button (`#4361ee`).
  - Green glowing **AI Protection Active** status.
  - **AI Shield Illustration** box.
  - **8-Stage Live Inspection Pipeline**:
    1. Stage 01: Domain Discovery & DNS Resolution
    2. Stage 02: RDAP / WHOIS Parsing
    3. Stage 03: URL Structural Entropy Analysis
    4. Stage 04: HTML Content & Form Action Extraction
    5. Stage 05: Headless Screenshot Capture
    6. Stage 06: Computer Vision Visual Similarity Matching
    7. Stage 07: Neural AI Risk Engine Scoring
    8. Stage 08: Final Verdict Computation
- **Right Panel (Threat Status & Visual Risk Analytics)**:
  - **Status: Safe** card (`Website is safe`).
  - **Status: High Risk** card (`Phishing/Malware Detected`).
  - **Circular Donut Gauge Chart**: Displays live risk percentage (`94.7%`) and `DEFCON 1` threat level.
  - **Visual Risk Metric Breakdown Bars**: Visual Similarity (`96.4%`), Content & Form (`91.0%`), Domain Age (`82.0%`), URL Entropy (`76.0%`).
  - **View Report Button**: Opens full security dossier with explainable AI audit trail and JSON download.

---

## 📁 Repository Structure

```
.
├── index.html          # Main HTML entry point with Tailwind CSS & Lucide icons
├── styles.css          # Custom glassmorphic stylesheet & linear background gradient
├── app.js              # Single Page Application router, mock threat store & UI renderer
├── ai_shield_icon.jpg  # AI Protection Shield graphic asset
└── README.md           # Documentation
```

---

## 🚀 How to Run Locally

Simply clone the repository and open `index.html` in any web browser (Google Chrome, Microsoft Edge, Mozilla Firefox, Safari):

```bash
git clone https://github.com/Prutviraj159/SIH_2026.git
cd SIH_2026
```

Open `index.html` directly in your browser or serve it with any local HTTP server.

