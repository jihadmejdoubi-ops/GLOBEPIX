html_content = '''<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <title>PIXEL WORLD — Strategy & Rocket Strike Edition</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
  <script src="https://cdn.jsdelivr.net/npm/topojson-client@3"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; user-select: none; -webkit-user-select: none; }
    body {
      margin: 0;
      font-family: 'Inter', sans-serif;
      background: #060a13;
      color: #f1f5f9;
      overflow-x: hidden;
    }
    .mono { font-family: 'JetBrains Mono', monospace; }

    #map-wrapper {
      position: relative;
      width: 100%;
      height: calc(100vh - 128px);
      min-height: 550px;
      background: #040914;
      border: 2px solid #1e293b;
      border-radius: 16px;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.8), inset 0 0 0 1px rgba(56, 189, 248, 0.16);
      overflow: hidden;
      transition: all 0.2s ease;
    }
    #map-wrapper:fullscreen,
    #map-wrapper.is-fullscreen {
      position: fixed !important;
      inset: 0 !important;
      width: 100vw !important;
      height: 100vh !important;
      border-radius: 0 !important;
      border: none !important;
      z-index: 9999 !important;
    }
    canvas#worldCanvas {
      display: block;
      width: 100%;
      height: 100%;
      cursor: crosshair;
      touch-action: none;
    }
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0f172a; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 999px; }
    ::-webkit-scrollbar-thumb:hover { background: #475569; }
  </style>
</head>
<body class="min-h-screen flex flex-col">

  <!-- Top Navigation Bar -->
  <header class="bg-slate-900/90 backdrop-blur-md border-b border-slate-800 px-4 py-2 sticky top-0 z-40">
    <div class="max-w-[1640px] mx-auto flex flex-wrap items-center justify-between gap-3">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-lg bg-gradient-to-br from-sky-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-500/20">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="font-extrabold tracking-tight text-lg text-white">PIXEL WORLD</h1>
            <span class="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-rose-500/15 text-rose-400 border border-rose-500/30">ROCKET WARFARE</span>
          </div>
          <p class="text-xs text-slate-400">1,000 Troops/px • 10×10 Territory = 1 Rocket (100px Blast -> Scorched 1,000 Defense)</p>
        </div>
      </div>

      <!-- Live Counters -->
      <div class="hidden xl:flex items-center gap-5 bg-slate-950/80 border border-slate-800 px-4 py-1.5 rounded-xl">
        <div>
          <div class="text-[10px] uppercase tracking-wider text-slate-400">Your Territory</div>
          <div id="stat-my-pixels" class="mono text-sm font-bold text-sky-400">0 px</div>
        </div>
        <div class="w-px h-6 bg-slate-800"></div>
        <div>
          <div class="text-[10px] uppercase tracking-wider text-slate-400">Your Army</div>
          <div id="stat-my-troops" class="mono text-sm font-bold text-amber-400">0 / 0</div>
        </div>
        <div class="w-px h-6 bg-slate-800"></div>
        <div>
          <div class="text-[10px] uppercase tracking-wider text-slate-400">Rockets Ready</div>
          <div id="stat-my-rockets" class="mono text-sm font-bold text-rose-400">0 🚀</div>
        </div>
        <div class="w-px h-6 bg-slate-800"></div>
        <div>
          <div class="text-[10px] uppercase tracking-wider text-slate-400">World Occupied</div>
          <div id="stat-painted" class="mono text-sm font-bold text-emerald-400">0</div>
        </div>
        <div class="w-px h-6 bg-slate-800"></div>
        <div>
          <div class="text-[10px] uppercase tracking-wider text-slate-400">Online</div>
          <div id="stat-online" class="mono text-sm font-bold text-violet-400">1</div>
        </div>
        <div class="w-px h-6 bg-slate-800"></div>
        <div>
          <div class="text-[10px] uppercase tracking-wider text-slate-400">Sync Status</div>
          <div id="sync-badge" class="text-xs font-semibold text-amber-400 flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span> Local / Ready
          </div>
        </div>
      </div>

      <!-- Actions & Profile -->
      <div class="flex items-center gap-2">
        <button onclick="resetEntireMatch()" class="px-3 py-1.5 rounded-lg bg-rose-950/80 hover:bg-rose-800 text-rose-200 text-xs font-semibold border border-rose-700/60 transition flex items-center gap-1.5" title="Reset map to completely empty for a fresh match">
          <span>🔄</span> New Empty Map
        </button>
        <button onclick="openModal('leaderboardModal')" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition flex items-center gap-1.5">
          <span>🏆</span> Nations
        </button>
        <button onclick="shareMapView()" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition flex items-center gap-1.5">
          <span>🔗</span> Invite Friend
        </button>
        <button onclick="openModal('supabaseModal')" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-sky-300 text-xs font-semibold border border-sky-500/30 transition flex items-center gap-1.5">
          <span>⚡</span> Supabase
        </button>
        <div id="authArea">
          <button onclick="openModal('authModal')" class="px-3.5 py-1.5 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold shadow-lg shadow-sky-600/25 transition">
            Sign In / Join
          </button>
        </div>
      </div>
    </div>
  </header>

  <!-- Main Workspace -->
  <main class="flex-1 max-w-[1640px] w-full mx-auto px-3 sm:px-5 py-2.5 flex flex-col gap-2.5">
    <div id="map-wrapper">
      <canvas id="worldCanvas"></canvas>

      <!-- Top-Left HUD: Coordinates, Troop/Scorched Inspector & Drop Zone -->
      <div class="absolute top-3 left-3 z-20 flex flex-col gap-2 pointer-events-none">
        <div class="bg-slate-900/90 backdrop-blur-md border border-slate-700/80 rounded-xl px-3.5 py-2 shadow-xl pointer-events-auto max-w-md">
          <div class="flex items-center gap-2.5 text-xs">
            <span class="mono text-slate-300" id="hud-coords">Lat: 0.00° | Lon: 0.00°</span>
            <span id="hud-terrain" class="px-2 py-0.5 rounded text-[11px] font-bold bg-slate-800 text-slate-400">LOADING WORLD...</span>
          </div>
          <div id="hud-pixel-info" class="text-[11px] text-slate-300 mt-1 font-medium">
            Empty Map Ready! Click any land pixel to found your Capital (1,000 troops).
          </div>
        </div>

        <!-- Drop Zone Landing Bar -->
        <div class="bg-slate-900/85 backdrop-blur-md border border-slate-700/80 rounded-xl p-1.5 shadow-lg pointer-events-auto flex flex-wrap items-center gap-1 max-w-lg">
          <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400 px-1.5">Drop Zone:</span>
          <button onclick="flyToRegion(0, 15, 1)" class="px-2 py-1 text-[11px] rounded-md bg-slate-800 hover:bg-sky-600 text-slate-200 hover:text-white transition">World</button>
          <button onclick="flyToRegion(-98, 39, 4)" class="px-2 py-1 text-[11px] rounded-md bg-slate-800 hover:bg-sky-600 text-slate-200 hover:text-white transition">N. America</button>
          <button onclick="flyToRegion(-58, -15, 3.8)" class="px-2 py-1 text-[11px] rounded-md bg-slate-800 hover:bg-sky-600 text-slate-200 hover:text-white transition">S. America</button>
          <button onclick="flyToRegion(15, 48, 5)" class="px-2 py-1 text-[11px] rounded-md bg-slate-800 hover:bg-sky-600 text-slate-200 hover:text-white transition">Europe</button>
          <button onclick="flyToRegion(18, 8, 3.8)" class="px-2 py-1 text-[11px] rounded-md bg-slate-800 hover:bg-sky-600 text-slate-200 hover:text-white transition">Africa</button>
          <button onclick="flyToRegion(95, 34, 3.6)" class="px-2 py-1 text-[11px] rounded-md bg-slate-800 hover:bg-sky-600 text-slate-200 hover:text-white transition">Asia</button>
          <button onclick="flyToRegion(134, -25, 4.5)" class="px-2 py-1 text-[11px] rounded-md bg-slate-800 hover:bg-sky-600 text-slate-200 hover:text-white transition">Australia</button>
        </div>
      </div>

      <!-- Top-Right Controls: Fullscreen, Zoom & Live Players Activity -->
      <div class="absolute top-3 right-3 z-20 flex flex-col items-end gap-2">
        <div class="flex items-center gap-2">
          <button onclick="toggleLiveFeed()" class="bg-slate-900/90 hover:bg-slate-800 text-violet-300 border border-violet-500/30 rounded-xl px-3 py-2 shadow-xl backdrop-blur-md flex items-center gap-1.5 text-xs font-bold transition" title="Toggle Live Players Activity">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            <span>Live Players (<span id="live-players-count">1</span>)</span>
          </button>

          <button id="fullscreenBtn" onclick="toggleFullscreen()" class="bg-slate-900/90 hover:bg-sky-600 text-white border border-slate-700/80 rounded-xl px-3 py-2 shadow-xl backdrop-blur-md flex items-center gap-2 text-xs font-bold transition" title="Toggle Fullscreen">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"/>
            </svg>
            <span id="fsBtnText">Fullscreen</span>
          </button>
        </div>

        <!-- Zoom Controls -->
        <div class="bg-slate-900/90 backdrop-blur-md border border-slate-700/80 rounded-xl p-1 shadow-xl flex flex-col gap-1">
          <button onclick="zoomStep(1.5)" class="w-9 h-9 rounded-lg hover:bg-slate-800 text-white font-bold text-lg flex items-center justify-center transition" title="Zoom In">+</button>
          <div id="zoom-level-label" class="mono text-[10px] text-center text-slate-400 py-0.5">1.0x</div>
          <button onclick="zoomStep(0.66)" class="w-9 h-9 rounded-lg hover:bg-slate-800 text-white font-bold text-lg flex items-center justify-center transition" title="Zoom Out">−</button>
          <button onclick="flyToRegion(0, 15, 1)" class="w-9 h-9 rounded-lg hover:bg-slate-800 text-slate-300 text-xs flex items-center justify-center transition" title="Reset View">⟲</button>
        </div>

        <!-- Live Players & Live Actions Panel -->
        <div id="liveActivityPanel" class="w-72 bg-slate-900/95 backdrop-blur-md border border-slate-700/90 rounded-2xl p-3 shadow-2xl text-xs">
          <div class="flex items-center justify-between border-b border-slate-800 pb-2 mb-2">
            <span class="font-bold text-white flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full bg-emerald-400"></span> Commanders & Strikes
            </span>
            <button onclick="toggleLiveFeed()" class="text-slate-400 hover:text-white text-sm">×</button>
          </div>
          <div id="onlinePlayersList" class="flex flex-wrap gap-1.5 mb-2.5 max-h-20 overflow-y-auto"></div>
          <div class="text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-1.5">War & Rocket Log</div>
          <div id="liveActionLog" class="space-y-1.5 max-h-40 overflow-y-auto pr-1"></div>
        </div>
      </div>

      <!-- Bottom-Center Nation Color, Rocket Silo & Command Bar -->
      <div class="absolute bottom-3 left-1/2 -translate-x-1/2 z-20 w-[96%] max-w-4xl bg-slate-900/95 backdrop-blur-md border border-slate-700/90 rounded-2xl px-4 py-2.5 shadow-2xl flex flex-wrap items-center justify-between gap-3">
        <div class="flex items-center gap-1.5 flex-wrap" id="paletteContainer"></div>
        <div class="flex items-center gap-2 flex-wrap">
          <label class="flex items-center gap-1.5 bg-slate-800 px-2.5 py-1.5 rounded-lg border border-slate-700 cursor-pointer text-xs text-slate-300">
            <span>Color</span>
            <input type="color" id="customColorPicker" value="#38bdf8" class="w-5 h-5 rounded cursor-pointer bg-transparent border-0" />
          </label>

          <!-- Build Rocket (Convert 10x10 = 100 pixels into 1 Rocket) -->
          <button id="buildRocketBtn" onclick="craftRocketFromTerritory()" class="px-3 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-500 text-white text-xs font-bold shadow transition flex items-center gap-1.5" title="Requires at least 10x10 (100) owned pixels. Launching sacrifices those 100 pixels!">
            <span>🚀</span> <span id="buildRocketLabel">Build Rocket (10×10)</span>
          </button>

          <!-- Toggle Rocket Aiming Mode -->
          <button id="rocketAimBtn" onclick="toggleRocketAimMode()" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-rose-600 text-rose-300 hover:text-white border border-rose-500/40 text-xs font-bold shadow transition flex items-center gap-1.5">
            <span>🎯</span> <span id="rocketAimLabel">Aim Rocket (<span id="rocketCountBadge">0</span>)</span>
          </button>

          <button id="modeToggleBtn" onclick="toggleInteractionMode()" class="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow transition flex items-center gap-1.5">
            <span>⚔️</span> <span id="modeLabel">Conquer: ON</span>
          </button>
        </div>
      </div>

      <!-- Toast -->
      <div id="mapToast" class="pointer-events-none opacity-0 transition-opacity duration-300 absolute bottom-20 left-1/2 -translate-x-1/2 z-30 bg-slate-950/95 border border-slate-700 text-white text-xs font-semibold px-4 py-2 rounded-full shadow-2xl text-center">
        Notification
      </div>
    </div>
  </main>

  <!-- Auth Modal -->
  <div id="authModal" class="hidden fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="bg-slate-900 border border-slate-700 rounded-2xl max-w-md w-full p-6 shadow-2xl">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-bold text-white">Commander Profile</h2>
        <button onclick="closeModal('authModal')" class="text-slate-400 hover:text-white text-xl">×</button>
      </div>
      <p class="text-xs text-slate-400 mb-4">Set your Nation / Commander name so allies and rivals see your territory, troops, and rocket strikes live.</p>
      <div class="space-y-3">
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Commander / Nation Name</label>
          <input id="authUsername" type="text" placeholder="e.g. TangierEmpire" class="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-sm text-white focus:outline-none focus:border-sky-500" />
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Email Address (Optional for Guest)</label>
          <input id="authEmail" type="email" placeholder="commander@pixelworld.io" class="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-sm text-white focus:outline-none focus:border-sky-500" />
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Password</label>
          <input id="authPassword" type="password" placeholder="••••••••" class="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-sm text-white focus:outline-none focus:border-sky-500" />
        </div>
        <div class="grid grid-cols-3 gap-2 pt-2">
          <button onclick="setGuestName()" class="w-full py-2.5 rounded-lg bg-slate-700 hover:bg-slate-600 text-white text-xs font-bold transition">Set Name</button>
          <button onclick="handleAuth('signin')" class="w-full py-2.5 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold transition">Sign In</button>
          <button onclick="handleAuth('signup')" class="w-full py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition">Register</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Leaderboard Modal -->
  <div id="leaderboardModal" class="hidden fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="bg-slate-900 border border-slate-700 rounded-2xl max-w-2xl w-full p-6 shadow-2xl max-h-[85vh] flex flex-col">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-lg font-bold text-white">World Nations & Military Power</h2>
          <p class="text-xs text-slate-400">Ranked by territory size (each pixel holds up to 1,000 troops)</p>
        </div>
        <button onclick="closeModal('leaderboardModal')" class="text-slate-400 hover:text-white text-xl">×</button>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 overflow-y-auto pr-1">
        <div class="bg-slate-950/70 border border-slate-800 rounded-xl p-4">
          <h3 class="text-xs font-bold uppercase tracking-wider text-sky-400 mb-3">Largest Nations</h3>
          <div id="playerLeaderboardList" class="space-y-2 text-xs"></div>
        </div>
        <div class="bg-slate-950/70 border border-slate-800 rounded-xl p-4">
          <h3 class="text-xs font-bold uppercase tracking-wider text-emerald-400 mb-3">Continental Control</h3>
          <div id="regionStatsList" class="space-y-2.5 text-xs"></div>
        </div>
      </div>
    </div>
  </div>

  <!-- Supabase Modal -->
  <div id="supabaseModal" class="hidden fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="bg-slate-900 border border-slate-700 rounded-2xl max-w-lg w-full p-6 shadow-2xl">
      <div class="flex items-center justify-between mb-3">
        <h2 class="text-lg font-bold text-white">Supabase Live Backend Setup</h2>
        <button onclick="closeModal('supabaseModal')" class="text-slate-400 hover:text-white text-xl">×</button>
      </div>
      <p class="text-xs text-slate-400 mb-4">
        Enter your Supabase Project URL and Publishable Key after running <code class="text-emerald-400">supabase_setup.sql</code>.
      </p>
      <div class="space-y-3">
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Supabase Project URL</label>
          <input id="sbUrlInput" type="text" placeholder="https://xyzcompany.supabase.co" class="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-xs mono text-white" />
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Supabase Publishable / Anon Key</label>
          <input id="sbKeyInput" type="password" placeholder="sb_publishable_..." class="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-xs mono text-white" />
        </div>
        <div class="flex justify-end gap-2 pt-2">
          <button onclick="saveSupabaseConfig()" class="px-4 py-2 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold">Connect & Sync</button>
        </div>
      </div>
    </div>
  </div>

<script>
/**
 * ============================================================================
 * 1. SUPABASE CONFIGURATION & GAME CONSTANTS
 * ============================================================================
 */
let SUPABASE_URL = localStorage.getItem('pw_sb_url') || 'https://jtenooggifivyjkhigoq.supabase.co';
let SUPABASE_ANON_KEY = localStorage.getItem('pw_sb_key') || 'sb_publishable_phnn7CcyELGiAlxVxZPbxQ_slhsyPLV';
let supabaseClient = null;
let realtimeChannel = null;

// Core Troop & Rocket Constants
const MAX_TROOPS = 1000;            // Every owned pixel holds up to 1,000 troops
const NEUTRAL_DEFENSE = 500;        // Normal empty land costs 500 troops to colonize
const SCORCHED_DEFENSE = 1000;      // Empty land hit by a rocket has 1,000 defense!
const ATTACK_BATCH = 500;           // Standard attack wave per supporting pixel
const REGEN_PER_SEC = 100;          // +100 troops/sec recovery per owned pixel
const COLONIZE_DURATION_MS = 1000;  // 1 second colonization timer
const ROCKET_PIXEL_COST = 100;      // 10x10 = 100 pixels required & erased on launch
const ROCKET_BLAST_RADIUS = 10;     // 10x10 square = 100 pixels destroyed on impact

/**
 * ============================================================================
 * 2. REAL GEOGRAPHIC WORLD MAP LOADER (1,000,000 LAND PIXELS)
 * ============================================================================
 */
const GRID_W = 2000;
const GRID_H = 1000;
const landMask = new Uint8Array(GRID_W * GRID_H);
const coastlineEdges = [];

const FALLBACK_POLYGONS = [
  [[-168,66],[-162,70],[-140,69],[-115,69],[-95,70],[-78,62],[-64,60],[-55,52],[-67,44],[-75,38],[-81,31],[-80,25],[-84,30],[-97,26],[-97,20],[-87,21],[-83,10],[-78,8],[-92,15],[-105,20],[-114,31],[-122,37],[-124,48],[-140,59],[-162,55],[-166,60]],
  [[-45,60],[-55,72],[-68,76],[-35,83],[-18,75],[-24,68]],
  [[-78,9],[-62,10],[-48,-1],[-35,-6],[-39,-15],[-48,-26],[-58,-38],[-67,-55],[-75,-48],[-71,-30],[-76,-14],[-81,-5],[-80,1]],
  [[-9,37],[-9,43],[-2,43],[2,51],[9,54],[11,58],[6,63],[20,70],[40,67],[60,68],[60,55],[44,47],[30,46],[23,37],[16,41],[9,44],[0,39],[-5,36]],
  [[-5,50],[1,51],[-1,55],[-6,58],[-4,51]],
  [[-6,35],[10,37],[20,32],[32,31],[39,21],[51,12],[41,-2],[35,-20],[26,-34],[18,-34],[12,-15],[9,4],[-8,5],[-17,14],[-13,27]],
  [[49,-12],[50,-16],[47,-25],[44,-25],[47,-13]],
  [[27,41],[41,42],[60,55],[72,72],[105,77],[140,72],[178,66],[162,55],[135,44],[126,35],[121,31],[108,21],[105,9],[98,8],[88,22],[77,8],[67,25],[56,27],[48,29],[39,21],[32,36],[27,37]],
  [[130,31],[137,35],[141,41],[145,44],[139,40],[131,34]],
  [[96,5],[105,-5],[114,-8],[126,-6],[124,1],[110,2],[98,2]],
  [[131,-1],[141,-3],[150,-10],[141,-8],[135,-4]],
  [[114,-22],[130,-12],[142,-11],[151,-24],[150,-37],[139,-35],[124,-33],[114,-28]],
  [[173,-35],[178,-38],[171,-43],[167,-46],[174,-42]]
];

function pointInRing(lon, lat, ring) {
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const xi = ring[i][0], yi = ring[i][1];
    const xj = ring[j][0], yj = ring[j][1];
    const intersect = ((yi > lat) !== (yj > lat)) &&
      (lon < (xj - xi) * (lat - yi) / ((yj - yi) || 1e-9) + xi);
    if (intersect) inside = !inside;
  }
  return inside;
}

function pointInGeometry(lon, lat, geom) {
  if (!geom) return false;
  if (geom.type === 'Polygon') {
    if (!pointInRing(lon, lat, geom.coordinates[0])) return false;
    for (let h = 1; h < geom.coordinates.length; h++) {
      if (pointInRing(lon, lat, geom.coordinates[h])) return false;
    }
    return true;
  }
  if (geom.type === 'MultiPolygon') {
    for (let p = 0; p < geom.coordinates.length; p++) {
      const poly = geom.coordinates[p];
      if (pointInRing(lon, lat, poly[0])) {
        let inHole = false;
        for (let h = 1; h < poly.length; h++) {
          if (pointInRing(lon, lat, poly[h])) { inHole = true; break; }
        }
        if (!inHole) return true;
      }
    }
  }
  return false;
}

function extractCoastlines() {
  coastlineEdges.length = 0;
  for (let y = 1; y < GRID_H - 1; y++) {
    for (let x = 1; x < GRID_W - 1; x++) {
      const idx = y * GRID_W + x;
      if (landMask[idx] === 1) {
        if (landMask[idx - 1] === 0) coastlineEdges.push([x, y, x, y + 1]);
        if (landMask[idx + 1] === 0) coastlineEdges.push([x + 1, y, x + 1, y + 1]);
        if (landMask[idx - GRID_W] === 0) coastlineEdges.push([x, y, x + 1, y]);
        if (landMask[idx + GRID_W] === 0) coastlineEdges.push([x, y + 1, x + 1, y + 1]);
      }
    }
  }
}

function rasterizeFallbackMap() {
  landMask.fill(0);
  for (let y = 0; y < GRID_H; y++) {
    const lat = 84 - (y / GRID_H) * 142;
    for (let x = 0; x < GRID_W; x++) {
      const lon = -180 + (x / GRID_W) * 360;
      for (let p = 0; p < FALLBACK_POLYGONS.length; p++) {
        if (pointInRing(lon, lat, FALLBACK_POLYGONS[p])) {
          landMask[y * GRID_W + x] = 1;
          break;
        }
      }
    }
  }
  extractCoastlines();
  document.getElementById('hud-terrain').textContent = 'WORLD READY';
}

async function upgradeToRealWorldMap() {
  try {
    const res = await fetch('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json', { cache: 'force-cache' });
    if (res.ok && window.topojson) {
      const worldTopo = await res.json();
      const geo = window.topojson.feature(worldTopo, worldTopo.objects.countries);
      const features = geo.features.filter(f => f.id !== '010');
      const nextMask = new Uint8Array(GRID_W * GRID_H);

      for (let y = 0; y < GRID_H; y++) {
        const lat = 84 - (y / GRID_H) * 142;
        for (let x = 0; x < GRID_W; x++) {
          const lon = -180 + (x / GRID_W) * 360;
          for (let f = 0; f < features.length; f++) {
            if (pointInGeometry(lon, lat, features[f].geometry)) {
              nextMask[y * GRID_W + x] = 1;
              break;
            }
          }
        }
      }

      landMask.set(nextMask);
      extractCoastlines();
      document.getElementById('hud-terrain').textContent = 'REAL WORLD READY';
    }
  } catch (e) {
    console.warn('Keeping fallback map:', e);
  }
}

/**
 * ============================================================================
 * 3. STATE, EMPTY MAP START, TROOP & ROCKET ENGINE
 * ============================================================================
 */
const PALETTE = [
  '#ef4444', '#f97316', '#f59e0b', '#eab308', '#84cc16', '#22c55e',
  '#10b981', '#06b6d4', '#38bdf8', '#3b82f6', '#6366f1', '#8b5cf6',
  '#d946ef', '#ec4899', '#ffffff', '#94a3b8'
];

let selectedColor = '#38bdf8';
let conquerMode = true;
let rocketAimMode = false;
let readyRockets = parseInt(localStorage.getItem('pw_rockets_v4') || '0', 10);

const clientId = 'cmd_' + Math.random().toString(36).slice(2, 8);
let currentUser = JSON.parse(localStorage.getItem('pw_user') || 'null');
if (!currentUser) {
  currentUser = { username: 'Nation_' + Math.floor(100 + Math.random() * 900) };
}

// Each owned pixel: { x, y, color, owner, region, baseTroops, updatedAt, colonizingUntil }
const paintedPixels = new Map();
// Scorched pixels destroyed by rockets: key "x,y" -> timestamp (empty land requiring 1,000 troops!)
const scorchedPixels = new Map();
// Active visual explosion effects
const explosionEffects = [];

const livePlayers = new Map();
const liveActionLog = [];
const broadcastChannel = ('BroadcastChannel' in window) ? new BroadcastChannel('pixel_world_rocket_v4') : null;

livePlayers.set(clientId, {
  id: clientId,
  username: currentUser.username,
  gx: Math.floor(GRID_W / 2),
  gy: Math.floor(GRID_H / 2),
  color: selectedColor,
  actionText: 'Ready on empty map',
  updatedAt: Date.now()
});

function getPixelTroops(pixel, now = Date.now()) {
  if (!pixel) return NEUTRAL_DEFENSE;
  if (pixel.colonizingUntil && now < pixel.colonizingUntil) {
    return 0;
  }
  const effectiveStart = Math.max(pixel.updatedAt || now, pixel.colonizingUntil || 0);
  const elapsedSec = Math.max(0, (now - effectiveStart) / 1000);
  const base = typeof pixel.baseTroops === 'number' ? pixel.baseTroops : MAX_TROOPS;
  return Math.min(MAX_TROOPS, Math.floor(base + elapsedSec * REGEN_PER_SEC));
}

function getPlayerOwnedPixels(username) {
  const list = [];
  paintedPixels.forEach(p => {
    if (p.owner === username) list.push(p);
  });
  return list;
}

function getAdjacentOwnedPixels(gx, gy, username) {
  const dirs = [[-1,0],[1,0],[0,-1],[0,1],[-1,-1],[1,-1],[-1,1],[1,1]];
  const adj = [];
  for (const [dx, dy] of dirs) {
    const p = paintedPixels.get(`${gx + dx},${gy + dy}`);
    if (p && p.owner === username) adj.push(p);
  }
  return adj;
}

function getContinentName(lon, lat) {
  if (lon < -25 && lat > 12) return 'North America';
  if (lon < -30 && lat <= 12) return 'South America';
  if (lon >= -25 && lon <= 45 && lat > 35) return 'Europe';
  if (lon >= -25 && lon <= 55 && lat <= 35) return 'Africa';
  if (lon > 110 && lat < -10) return 'Australia';
  return 'Asia';
}

function recordLiveAction(playerName, actionDesc, color, gx, gy) {
  const { lat, lon } = gridToLatLon(gx, gy);
  liveActionLog.unshift({
    playerName,
    actionDesc,
    color,
    lat: lat.toFixed(1),
    lon: lon.toFixed(1),
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  });
  if (liveActionLog.length > 25) liveActionLog.pop();
  renderLivePanel();
}

function renderLivePanel() {
  const now = Date.now();
  livePlayers.forEach((p, id) => {
    if (id !== clientId && now - p.updatedAt > 30000) {
      livePlayers.delete(id);
    }
  });

  const count = livePlayers.size;
  document.getElementById('stat-online').textContent = count;
  document.getElementById('live-players-count').textContent = count;

  const playersEl = document.getElementById('onlinePlayersList');
  playersEl.innerHTML = Array.from(livePlayers.values()).map(p => `
    <button onclick="flyToGrid(${p.gx}, ${p.gy}, 8)" class="flex items-center gap-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 px-2 py-1 rounded-lg text-[11px] font-semibold text-slate-200 transition" title="Jump to ${p.username}">
      <span class="w-2 h-2 rounded-full" style="background:${p.color}"></span>
      <span>${p.username}</span>
    </button>
  `).join('');

  const logEl = document.getElementById('liveActionLog');
  logEl.innerHTML = liveActionLog.length
    ? liveActionLog.map(item => `
      <div class="bg-slate-950/80 border border-slate-800/90 rounded-lg px-2.5 py-1.5 flex items-center justify-between gap-2">
        <div class="truncate">
          <span class="font-bold" style="color:${item.color}">${item.playerName}</span>
          <span class="text-slate-300"> ${item.actionDesc}</span>
          <div class="text-[10px] mono text-slate-500">(${item.lat}°, ${item.lon}°)</div>
        </div>
        <span class="text-[10px] mono text-slate-500 shrink-0">${item.time}</span>
      </div>
    `).join('')
    : '<div class="text-slate-500 text-[11px]">Empty map ready! Click any land pixel to start your Capital.</div>';
}

function persistLocalState() {
  localStorage.setItem('pw_pixels_rocket_v4', JSON.stringify(Array.from(paintedPixels.entries())));
  localStorage.setItem('pw_scorched_rocket_v4', JSON.stringify(Array.from(scorchedPixels.entries())));
  localStorage.setItem('pw_rockets_v4', String(readyRockets));
}

function loadLocalState() {
  try {
    const saved = localStorage.getItem('pw_pixels_rocket_v4');
    if (saved) JSON.parse(saved).forEach(([k, v]) => paintedPixels.set(k, v));
    const scorched = localStorage.getItem('pw_scorched_rocket_v4');
    if (scorched) JSON.parse(scorched).forEach(([k, v]) => scorchedPixels.set(k, v));
  } catch (e) {}
  updateStatsUI();
}

/**
 * ============================================================================
 * 4. CAMERA & VIEWPORT CONTROLS
 * ============================================================================
 */
const canvas = document.getElementById('worldCanvas');
const ctx = canvas.getContext('2d', { alpha: false });

const camera = {
  x: GRID_W / 2,
  y: GRID_H / 2.3,
  zoom: 1,
  targetX: GRID_W / 2,
  targetY: GRID_H / 2.3,
  targetZoom: 1,
  vx: 0,
  vy: 0
};

let isDragging = false;
let dragMoved = false;
let lastPointer = { x: 0, y: 0 };
let hoverCell = { x: -1, y: -1, isLand: false, region: 'Ocean' };

function resizeCanvas() {
  const wrapper = document.getElementById('map-wrapper');
  const w = Math.max(300, wrapper.clientWidth || window.innerWidth - 32);
  const h = Math.max(400, wrapper.clientHeight || 550);
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  canvas.width = w * dpr;
  canvas.height = h * dpr;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
}
window.addEventListener('resize', resizeCanvas);

function getBaseScale() {
  const wrapper = document.getElementById('map-wrapper');
  const w = Math.max(300, wrapper.clientWidth || window.innerWidth - 32);
  const h = Math.max(400, wrapper.clientHeight || 550);
  return Math.min(w / GRID_W, h / GRID_H);
}

function screenToGrid(sx, sy) {
  const wrapper = document.getElementById('map-wrapper');
  const w = Math.max(300, wrapper.clientWidth || window.innerWidth - 32);
  const h = Math.max(400, wrapper.clientHeight || 550);
  const scale = getBaseScale() * camera.zoom;
  const gx = Math.floor(camera.x + (sx - w / 2) / scale);
  const gy = Math.floor(camera.y + (sy - h / 2) / scale);
  return { gx, gy };
}

function gridToLatLon(gx, gy) {
  const lon = -180 + (gx / GRID_W) * 360;
  const lat = 84 - (gy / GRID_H) * 142;
  return { lat, lon };
}

function flyToGrid(gx, gy, targetZoom) {
  camera.targetX = Math.max(0, Math.min(GRID_W, gx));
  camera.targetY = Math.max(0, Math.min(GRID_H, gy));
  camera.targetZoom = Math.max(0.8, Math.min(50, targetZoom));
  camera.vx = 0;
  camera.vy = 0;
}

function flyToRegion(lon, lat, targetZoom) {
  const gx = ((lon + 180) / 360) * GRID_W;
  const gy = ((84 - lat) / 142) * GRID_H;
  flyToGrid(gx, gy, targetZoom);
}

function zoomStep(factor) {
  camera.targetZoom = Math.max(0.8, Math.min(50, camera.targetZoom * factor));
}

function toggleFullscreen() {
  const wrapper = document.getElementById('map-wrapper');
  if (!document.fullscreenElement) {
    if (wrapper.requestFullscreen) {
      wrapper.requestFullscreen().catch(() => wrapper.classList.toggle('is-fullscreen'));
    } else {
      wrapper.classList.toggle('is-fullscreen');
    }
  } else {
    document.exitFullscreen();
  }
}

document.addEventListener('fullscreenchange', () => {
  document.getElementById('fsBtnText').textContent = document.fullscreenElement ? 'Exit Fullscreen' : 'Fullscreen';
  setTimeout(resizeCanvas, 50);
});

/**
 * ============================================================================
 * 5. ROCKET CRAFTING (10x10 = 100 PIXELS) & 100-PIXEL STRIKE MECHANICS
 * ============================================================================
 */
function findBest10x10Block(username) {
  const myPixels = getPlayerOwnedPixels(username);
  if (myPixels.length < ROCKET_PIXEL_COST) return null;

  const ownedSet = new Set(myPixels.map(p => `${p.x},${p.y}`));
  // First look for an exact contiguous 10x10 square (100 pixels)
  for (const p of myPixels) {
    let all100 = true;
    const block = [];
    for (let dy = 0; dy < 10 && all100; dy++) {
      for (let dx = 0; dx < 10; dx++) {
        const k = `${p.x + dx},${p.y + dy}`;
        if (!ownedSet.has(k)) {
          all100 = false;
          break;
        }
        block.push(k);
      }
    }
    if (all100) return block;
  }

  // Fallback if player has 100+ pixels in an irregular border shape: pick 100 outer pixels
  return myPixels
    .slice(-ROCKET_PIXEL_COST)
    .map(p => `${p.x},${p.y}`);
}

function craftRocketFromTerritory() {
  const myPixels = getPlayerOwnedPixels(currentUser.username);
  if (myPixels.length < ROCKET_PIXEL_COST) {
    showToast(`🚀 Need 10×10 (100 pixels) to build a Rocket! You have ${myPixels.length}/100 px.`);
    return;
  }
  readyRockets += 1;
  rocketAimMode = true;
  persistLocalState();
  updateStatsUI();
  updateRocketUI();
  showToast('🚀 Rocket armed! Click anywhere on the map to strike a 10×10 (100px) area!');
}

function toggleRocketAimMode() {
  if (readyRockets <= 0) {
    const myPixels = getPlayerOwnedPixels(currentUser.username);
    if (myPixels.length >= ROCKET_PIXEL_COST) {
      craftRocketFromTerritory();
    } else {
      showToast(`🚀 Build a Rocket first! Requires 10×10 (100 pixels). You have ${myPixels.length}/100.`);
    }
    return;
  }
  rocketAimMode = !rocketAimMode;
  updateRocketUI();
  showToast(rocketAimMode ? '🎯 Rocket Aiming ON: Click any target on the map!' : '🎯 Rocket Aiming paused.');
}

function updateRocketUI() {
  const badge = document.getElementById('rocketCountBadge');
  if (badge) badge.textContent = readyRockets;
  const aimBtn = document.getElementById('rocketAimBtn');
  if (rocketAimMode && readyRockets > 0) {
    aimBtn.className = 'px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white border border-rose-300 text-xs font-bold shadow-lg shadow-rose-600/40 animate-pulse flex items-center gap-1.5';
  } else {
    aimBtn.className = 'px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-rose-600 text-rose-300 hover:text-white border border-rose-500/40 text-xs font-bold shadow transition flex items-center gap-1.5';
  }
}

async function launchRocketAt(targetGx, targetGy) {
  if (readyRockets <= 0) {
    rocketAimMode = false;
    updateRocketUI();
    return;
  }

  // Verify the launcher still owns the 100 pixels carrying the rocket
  const sacrificeKeys = findBest10x10Block(currentUser.username);
  if (!sacrificeKeys || sacrificeKeys.length < ROCKET_PIXEL_COST) {
    readyRockets = 0;
    rocketAimMode = false;
    persistLocalState();
    updateStatsUI();
    updateRocketUI();
    showToast('⚠️ Rocket lost! You no longer hold 100 pixels to launch it.');
    return;
  }

  const now = Date.now();
  // 1. Erase the 100 pixels (10x10) carrying the rocket from the launcher's territory
  const erasedCoords = [];
  for (const k of sacrificeKeys) {
    const p = paintedPixels.get(k);
    if (p) {
      erasedCoords.push({ x: p.x, y: p.y });
      paintedPixels.delete(k);
    }
  }

  // 2. Destroy a 10x10 square (100 pixels) around targetGx, targetGy -> empty land with 1,000 defense!
  const startX = Math.max(0, Math.min(GRID_W - ROCKET_BLAST_RADIUS, targetGx - 5));
  const startY = Math.max(0, Math.min(GRID_H - ROCKET_BLAST_RADIUS, targetGy - 5));
  const blastedCoords = [];

  for (let dy = 0; dy < ROCKET_BLAST_RADIUS; dy++) {
    for (let dx = 0; dx < ROCKET_BLAST_RADIUS; dx++) {
      const bx = startX + dx;
      const by = startY + dy;
      if (landMask[by * GRID_W + bx] === 1) {
        const bKey = `${bx},${by}`;
        paintedPixels.delete(bKey);
        scorchedPixels.set(bKey, now);
        blastedCoords.push({ x: bx, y: by });
      }
    }
  }

  readyRockets = Math.max(0, readyRockets - 1);
  rocketAimMode = false;
  explosionEffects.push({ gx: startX + 5, gy: startY + 5, createdAt: now });

  persistLocalState();
  updateStatsUI();
  updateRocketUI();

  const { lat, lon } = gridToLatLon(targetGx, targetGy);
  const region = getContinentName(lon, lat);
  const desc = `launched a ROCKET on ${region} (100px scorched -> 1,000 defense)!`;
  recordLiveAction(currentUser.username, desc, '#f43f5e', targetGx, targetGy);
  broadcastLivePresence(targetGx, targetGy, 'launched ROCKET strike!');

  const strikePayload = {
    attacker: currentUser.username,
    erasedCoords,
    blastedCoords,
    centerGx: startX + 5,
    centerGy: startY + 5,
    timestamp: now
  };

  if (broadcastChannel) {
    broadcastChannel.postMessage({ type: 'ROCKET_STRIKE', payload: strikePayload });
  }
  if (realtimeChannel) {
    realtimeChannel.send({ type: 'broadcast', event: 'rocket_strike', payload: strikePayload });
  }
  if (supabaseClient) {
    // Remove erased & blasted pixels from Supabase pixels table
    for (const c of erasedCoords) {
      supabaseClient.from('pixels').delete().match({ x: c.x, y: c.y });
    }
    for (const c of blastedCoords) {
      supabaseClient.from('pixels').delete().match({ x: c.x, y: c.y });
    }
  }

  showToast('💥 ROCKET IMPACT! 100 pixels obliterated (now 1,000 defense) & 100 launch pixels consumed.');
}

/**
 * ============================================================================
 * 6. COLONIZATION & COMBAT LOGIC (1000 MAX / 500 NORMAL / 1000 SCORCHED)
 * ============================================================================
 */
function broadcastLivePresence(gx, gy, actionText) {
  const payload = {
    id: clientId,
    username: currentUser.username,
    gx, gy,
    color: selectedColor,
    actionText,
    updatedAt: Date.now()
  };
  livePlayers.set(clientId, payload);
  renderLivePanel();

  if (broadcastChannel) broadcastChannel.postMessage({ type: 'PRESENCE', payload });
  if (realtimeChannel) realtimeChannel.send({ type: 'broadcast', event: 'player_activity', payload });
}

async function syncPixelToNetwork(pixelRecord) {
  const key = `${pixelRecord.x},${pixelRecord.y}`;
  scorchedPixels.delete(key);
  paintedPixels.set(key, pixelRecord);
  persistLocalState();
  updateStatsUI();

  if (broadcastChannel) {
    broadcastChannel.postMessage({ type: 'PIXEL_SYNC', payload: pixelRecord });
  }

  if (supabaseClient) {
    const { error } = await supabaseClient
      .from('pixels')
      .upsert({
        x: pixelRecord.x,
        y: pixelRecord.y,
        color: pixelRecord.color,
        owner_name: pixelRecord.owner,
        region: pixelRecord.region,
        updated_at: new Date(pixelRecord.updatedAt).toISOString()
      }, { onConflict: 'x,y' });
    if (error) console.warn('Supabase sync:', error.message);
  }
}

async function handleConquerAt(gx, gy) {
  if (gx < 0 || gx >= GRID_W || gy < 0 || gy >= GRID_H) return;
  const isLand = landMask[gy * GRID_W + gx] === 1;

  if (!isLand) {
    showToast('🌊 Sea Border Lock: Oceans cannot be colonized!');
    return;
  }

  // If Rocket Aiming Mode is active, fire the rocket!
  if (rocketAimMode) {
    await launchRocketAt(gx, gy);
    return;
  }

  const now = Date.now();
  const key = `${gx},${gy}`;
  const target = paintedPixels.get(key);
  const myPixels = getPlayerOwnedPixels(currentUser.username);
  const { lat, lon } = gridToLatLon(gx, gy);
  const region = getContinentName(lon, lat);

  // CASE A: First pixel ever (Founding Capital with 1,000 troops)
  if (myPixels.length === 0) {
    if (target) {
      showToast(`⚔️ ${target.owner} owns this land! Click empty land first to found your Capital.`);
      return;
    }
    const capital = {
      x: gx, y: gy,
      color: selectedColor,
      owner: currentUser.username,
      region,
      baseTroops: MAX_TROOPS,
      updatedAt: now,
      colonizingUntil: 0
    };
    await syncPixelToNetwork(capital);
    const desc = `founded Capital in ${region} (1,000 troops)`;
    recordLiveAction(currentUser.username, desc, selectedColor, gx, gy);
    broadcastLivePresence(gx, gy, desc);
    showToast('🚩 Capital founded! 1,000 troops ready.');
    return;
  }

  // CASE B: Clicking own pixel -> Status check
  if (target && target.owner === currentUser.username) {
    const currentTroops = getPixelTroops(target, now);
    if (target.colonizingUntil && now < target.colonizingUntil) {
      showToast('⏳ Colonizing in progress (1s)...');
    } else {
      showToast(`🛡️ Your garrison: ${currentTroops} / ${MAX_TROOPS} troops (+100/s)`);
    }
    return;
  }

  // Must attack/colonize adjacent to owned territory
  const adjacentAllies = getAdjacentOwnedPixels(gx, gy, currentUser.username);
  if (adjacentAllies.length === 0) {
    showToast('🧭 Expand from your borders! Click a pixel next to your territory.');
    return;
  }

  // Gather available attack power (500 troops per adjacent pixel that has >= 500 troops)
  const readySources = adjacentAllies
    .map(p => ({ pixel: p, troops: getPixelTroops(p, now) }))
    .filter(item => item.troops >= ATTACK_BATCH)
    .sort((a, b) => b.troops - a.troops);

  if (readySources.length === 0) {
    showToast('⏳ Need at least 500 troops in an adjacent pixel! Recovering +100/s...');
    return;
  }

  // CASE C: Empty Neutral Land (500 defense normally, OR 1,000 defense if scorched by a rocket!)
  if (!target) {
    const isScorched = scorchedPixels.has(key);
    const requiredDefense = isScorched ? SCORCHED_DEFENSE : NEUTRAL_DEFENSE;

    if (isScorched) {
      // Requires 1,000 troops (2 adjacent pixels with 500 each, or 1 pixel with 1,000)
      const singleFull = readySources.find(s => s.troops >= SCORCHED_DEFENSE);
      if (singleFull) {
        singleFull.pixel.baseTroops = singleFull.troops - SCORCHED_DEFENSE;
        singleFull.pixel.updatedAt = now;
        await syncPixelToNetwork(singleFull.pixel);
      } else if (readySources.length >= 2) {
        for (const src of readySources.slice(0, 2)) {
          src.pixel.baseTroops = src.troops - ATTACK_BATCH;
          src.pixel.updatedAt = now;
          await syncPixelToNetwork(src.pixel);
        }
      } else {
        showToast('☢️ Scorched Crater (1,000 defense)! Need 1,000 troops from 1 full pixel or 2 adjacent pixels.');
        return;
      }
    } else {
      const attacker = readySources[0];
      attacker.pixel.baseTroops = attacker.troops - NEUTRAL_DEFENSE;
      attacker.pixel.updatedAt = now;
      await syncPixelToNetwork(attacker.pixel);
    }

    const colonizedPixel = {
      x: gx, y: gy,
      color: selectedColor,
      owner: currentUser.username,
      region,
      baseTroops: 0,
      updatedAt: now + COLONIZE_DURATION_MS,
      colonizingUntil: now + COLONIZE_DURATION_MS
    };
    await syncPixelToNetwork(colonizedPixel);

    const desc = isScorched
      ? `reclaimed scorched land in ${region} (1,000 cost)`
      : `colonized land in ${region} (1s)`;
    recordLiveAction(currentUser.username, desc, selectedColor, gx, gy);
    broadcastLivePresence(gx, gy, desc);
    showToast(`🚩 Colonizing! Ready in 1s (Cost: ${requiredDefense} troops)`);
    return;
  }

  // CASE D: Enemy Pixel (up to 1,000 defense)
  const enemyTroops = getPixelTroops(target, now);
  const sourcesNeeded = enemyTroops > ATTACK_BATCH && readySources.length >= 2 ? 2 : 1;
  const usedSources = readySources.slice(0, sourcesNeeded);
  const totalAttackPower = usedSources.length * ATTACK_BATCH;

  for (const src of usedSources) {
    src.pixel.baseTroops = src.troops - ATTACK_BATCH;
    src.pixel.updatedAt = now;
    await syncPixelToNetwork(src.pixel);
  }

  if (totalAttackPower >= enemyTroops) {
    const conqueredPixel = {
      x: gx, y: gy,
      color: selectedColor,
      owner: currentUser.username,
      region,
      baseTroops: 0,
      updatedAt: now + COLONIZE_DURATION_MS,
      colonizingUntil: now + COLONIZE_DURATION_MS
    };
    await syncPixelToNetwork(conqueredPixel);

    const desc = `conquered ${target.owner}'s land in ${region}!`;
    recordLiveAction(currentUser.username, desc, selectedColor, gx, gy);
    broadcastLivePresence(gx, gy, desc);
    showToast(`⚔️ Victory! Conquered ${target.owner}'s pixel (colonizing in 1s)`);
  } else {
    const remainingEnemy = Math.max(0, enemyTroops - totalAttackPower);
    target.baseTroops = remainingEnemy;
    target.updatedAt = now;
    await syncPixelToNetwork(target);

    const desc = `attacked ${target.owner} (${remainingEnemy} troops left)`;
    recordLiveAction(currentUser.username, desc, selectedColor, gx, gy);
    broadcastLivePresence(gx, gy, desc);
    showToast(`💥 Hit ${target.owner} for -${totalAttackPower}! Enemy left with ${remainingEnemy} troops.`);
  }
}

/**
 * ============================================================================
 * 7. RESET MATCH TO COMPLETELY EMPTY MAP (FOR FRESH FRIEND GAMES)
 * ============================================================================
 */
async function resetEntireMatch() {
  paintedPixels.clear();
  scorchedPixels.clear();
  readyRockets = 0;
  rocketAimMode = false;
  liveActionLog.length = 0;
  localStorage.removeItem('pw_pixels_rocket_v4');
  localStorage.removeItem('pw_scorched_rocket_v4');
  localStorage.setItem('pw_rockets_v4', '0');

  updateStatsUI();
  updateRocketUI();
  renderLivePanel();

  if (broadcastChannel) {
    broadcastChannel.postMessage({ type: 'MAP_RESET' });
  }
  if (realtimeChannel) {
    realtimeChannel.send({ type: 'broadcast', event: 'map_reset', payload: { by: currentUser.username } });
  }
  if (supabaseClient) {
    // Clear all rows in pixels table so shared link starts 100% empty
    await supabaseClient.from('pixels').delete().gte('x', 0);
  }

  showToast('🌍 Map wiped clean! Both you and your friend start from zero.');
}

/**
 * ============================================================================
 * 8. OPTIMIZED RENDERER (EMPTY LAND, SCORCHED CRATERS, ROCKET PREVIEW & BLASTS)
 * ============================================================================
 */
function renderLoop() {
  const now = Date.now();
  camera.x += (camera.targetX - camera.x) * 0.16;
  camera.y += (camera.targetY - camera.y) * 0.16;
  camera.zoom += (camera.targetZoom - camera.zoom) * 0.18;

  if (!isDragging && (Math.abs(camera.vx) > 0.01 || Math.abs(camera.vy) > 0.01)) {
    camera.targetX = Math.max(0, Math.min(GRID_W, camera.targetX + camera.vx));
    camera.targetY = Math.max(0, Math.min(GRID_H, camera.targetY + camera.vy));
    camera.vx *= 0.88;
    camera.vy *= 0.88;
  }

  document.getElementById('zoom-level-label').textContent = `${camera.zoom.toFixed(1)}x`;

  const wrapper = document.getElementById('map-wrapper');
  const W = Math.max(300, wrapper.clientWidth || window.innerWidth - 32);
  const H = Math.max(400, wrapper.clientHeight || 550);
  const scale = getBaseScale() * camera.zoom;

  ctx.fillStyle = '#050c1a';
  ctx.fillRect(0, 0, W, H);

  const minX = Math.max(0, Math.floor(camera.x - (W / 2) / scale) - 1);
  const maxX = Math.min(GRID_W - 1, Math.ceil(camera.x + (W / 2) / scale) + 1);
  const minY = Math.max(0, Math.floor(camera.y - (H / 2) / scale) - 1);
  const maxY = Math.min(GRID_H - 1, Math.ceil(camera.y + (H / 2) / scale) + 1);

  // 1. Render Empty Landmass
  ctx.fillStyle = '#18253a';
  for (let y = minY; y <= maxY; y++) {
    const sy = H / 2 + (y - camera.y) * scale;
    const rowOffset = y * GRID_W;
    let runStart = -1;
    for (let x = minX; x <= maxX + 1; x++) {
      const isLand = x <= maxX && landMask[rowOffset + x] === 1;
      if (isLand && runStart === -1) runStart = x;
      else if (!isLand && runStart !== -1) {
        const sx = W / 2 + (runStart - camera.x) * scale;
        ctx.fillRect(sx, sy, Math.ceil((x - runStart) * scale), Math.ceil(scale));
        runStart = -1;
      }
    }
  }

  // 2. Render Scorched Rocket Craters (Empty pixels with 1,000 defense)
  scorchedPixels.forEach((_, key) => {
    const [sxGrid, syGrid] = key.split(',').map(Number);
    if (sxGrid >= minX && sxGrid <= maxX && syGrid >= minY && syGrid <= maxY) {
      const sx = W / 2 + (sxGrid - camera.x) * scale;
      const sy = H / 2 + (syGrid - camera.y) * scale;
      const size = Math.max(1.5, scale);
      ctx.fillStyle = '#291d24';
      ctx.fillRect(sx, sy, size, size);
      if (scale >= 8) {
        ctx.strokeStyle = 'rgba(244, 63, 94, 0.45)';
        ctx.lineWidth = 1;
        ctx.strokeRect(sx, sy, size, size);
      }
    }
  });

  // 3. Render Owned Pixels & Troop Strength
  paintedPixels.forEach((p) => {
    if (p.x >= minX && p.x <= maxX && p.y >= minY && p.y <= maxY) {
      const sx = W / 2 + (p.x - camera.x) * scale;
      const sy = H / 2 + (p.y - camera.y) * scale;
      const size = Math.max(1.5, scale);

      const isColonizing = p.colonizingUntil && now < p.colonizingUntil;
      ctx.save();
      if (isColonizing) {
        ctx.globalAlpha = 0.55 + 0.35 * Math.sin(now / 90);
      }
      ctx.fillStyle = p.color;
      ctx.fillRect(sx, sy, size, size);
      ctx.restore();

      if (scale >= 12) {
        const troops = getPixelTroops(p, now);
        const ratio = troops / MAX_TROOPS;
        ctx.fillStyle = 'rgba(2, 6, 23, 0.75)';
        ctx.fillRect(sx + 1, sy + size - 4, size - 2, 3);
        ctx.fillStyle = isColonizing ? '#fbbf24' : (ratio >= 1 ? '#4ade80' : '#38bdf8');
        ctx.fillRect(sx + 1, sy + size - 4, (size - 2) * ratio, 3);

        if (scale >= 26) {
          ctx.fillStyle = '#ffffff';
          ctx.font = 'bold 9px JetBrains Mono, monospace';
          ctx.textAlign = 'center';
          ctx.fillText(isColonizing ? '1s...' : troops, sx + size / 2, sy + size / 2 + 2);
          ctx.textAlign = 'left';
        }
      }
    }
  });

  // 4. Optimized Coastline Rendering
  ctx.strokeStyle = '#38bdf8';
  ctx.lineWidth = Math.min(2.0, Math.max(0.9, scale * 0.16));
  const edgeStep = camera.zoom < 1.5 ? 2 : 1;
  ctx.beginPath();
  for (let i = 0; i < coastlineEdges.length; i += edgeStep) {
    const e = coastlineEdges[i];
    if (e[0] >= minX && e[0] <= maxX + 1 && e[1] >= minY && e[1] <= maxY + 1) {
      ctx.moveTo(W / 2 + (e[0] - camera.x) * scale, H / 2 + (e[1] - camera.y) * scale);
      ctx.lineTo(W / 2 + (e[2] - camera.x) * scale, H / 2 + (e[3] - camera.y) * scale);
    }
  }
  ctx.stroke();

  // 5. Rocket Impact Shockwaves
  for (let i = explosionEffects.length - 1; i >= 0; i--) {
    const ex = explosionEffects[i];
    const age = now - ex.createdAt;
    if (age > 1600) {
      explosionEffects.splice(i, 1);
      continue;
    }
    const progress = age / 1600;
    const cx = W / 2 + (ex.gx - camera.x) * scale;
    const cy = H / 2 + (ex.gy - camera.y) * scale;
    const radius = (5 + progress * 14) * scale;
    ctx.save();
    ctx.strokeStyle = `rgba(244, 63, 94, ${1 - progress})`;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(cx, cy, radius, 0, Math.PI * 2);
    ctx.stroke();
    ctx.restore();
  }

  // 6. Live Commanders Presence Cursors
  livePlayers.forEach((p, id) => {
    if (id === clientId) return;
    const px = W / 2 + (p.gx - camera.x) * scale;
    const py = H / 2 + (p.gy - camera.y) * scale;
    if (px >= -80 && px <= W + 80 && py >= -40 && py <= H + 40) {
      ctx.save();
      ctx.strokeStyle = p.color;
      ctx.lineWidth = 2;
      ctx.strokeRect(px - 4, py - 4, Math.max(8, scale + 8), Math.max(8, scale + 8));

      ctx.font = 'bold 11px Inter, sans-serif';
      const label = `${p.username} • ${p.actionText}`;
      const tw = ctx.measureText(label).width + 12;
      ctx.fillStyle = 'rgba(15, 23, 42, 0.92)';
      ctx.fillRect(px + 8, py - 18, tw, 18);
      ctx.strokeStyle = p.color;
      ctx.lineWidth = 1;
      ctx.strokeRect(px + 8, py - 18, tw, 18);
      ctx.fillStyle = '#f8fafc';
      ctx.fillText(label, px + 14, py - 5);
      ctx.restore();
    }
  });

  // 7. Hover Cell or 10x10 (100px) Rocket Blast Zone Preview
  if (hoverCell.x >= 0 && hoverCell.x < GRID_W && hoverCell.y >= 0 && hoverCell.y < GRID_H) {
    if (rocketAimMode && readyRockets > 0) {
      const startX = Math.max(0, Math.min(GRID_W - ROCKET_BLAST_RADIUS, hoverCell.x - 5));
      const startY = Math.max(0, Math.min(GRID_H - ROCKET_BLAST_RADIUS, hoverCell.y - 5));
      const rx = W / 2 + (startX - camera.x) * scale;
      const ry = H / 2 + (startY - camera.y) * scale;
      const rw = ROCKET_BLAST_RADIUS * scale;
      ctx.save();
      ctx.fillStyle = 'rgba(244, 63, 94, 0.28)';
      ctx.fillRect(rx, ry, rw, rw);
      ctx.strokeStyle = '#f43f5e';
      ctx.lineWidth = 2.5;
      ctx.strokeRect(rx, ry, rw, rw);
      ctx.restore();
    } else {
      const hx = W / 2 + (hoverCell.x - camera.x) * scale;
      const hy = H / 2 + (hoverCell.y - camera.y) * scale;
      ctx.strokeStyle = hoverCell.isLand ? '#ffffff' : '#ef4444';
      ctx.lineWidth = 2;
      ctx.strokeRect(hx, hy, Math.max(3, scale), Math.max(3, scale));
    }
  }

  requestAnimationFrame(renderLoop);
}

/**
 * ============================================================================
 * 9. POINTER & WHEEL INTERACTION
 * ============================================================================
 */
let lastPresenceSent = 0;

canvas.addEventListener('pointerdown', (e) => {
  isDragging = true;
  dragMoved = false;
  lastPointer = { x: e.clientX, y: e.clientY };
  camera.vx = 0;
  camera.vy = 0;
  canvas.setPointerCapture(e.pointerId);
});

canvas.addEventListener('pointermove', (e) => {
  const rect = canvas.getBoundingClientRect();
  const { gx, gy } = screenToGrid(e.clientX - rect.left, e.clientY - rect.top);
  const now = Date.now();

  if (gx >= 0 && gx < GRID_W && gy >= 0 && gy < GRID_H) {
    const isLand = landMask[gy * GRID_W + gx] === 1;
    const { lat, lon } = gridToLatLon(gx, gy);
    const region = isLand ? getContinentName(lon, lat) : 'Ocean';
    hoverCell = { x: gx, y: gy, isLand, region };

    document.getElementById('hud-coords').textContent = `Lat: ${lat.toFixed(2)}° | Lon: ${lon.toFixed(2)}°`;
    const el = document.getElementById('hud-terrain');
    if (rocketAimMode && readyRockets > 0) {
      el.textContent = `🎯 ROCKET TARGET (10×10 = 100px)`;
      el.className = 'px-2 py-0.5 rounded text-[11px] font-bold bg-rose-600/30 text-rose-300 border border-rose-500/50';
    } else if (isLand) {
      el.textContent = `LAND • ${region.toUpperCase()}`;
      el.className = 'px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30';
    } else {
      el.textContent = 'SEA BORDER • LOCKED';
      el.className = 'px-2 py-0.5 rounded text-[11px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30';
    }

    const key = `${gx},${gy}`;
    const existing = paintedPixels.get(key);
    const isScorched = scorchedPixels.has(key);

    if (rocketAimMode && readyRockets > 0) {
      document.getElementById('hud-pixel-info').textContent = 'Click to launch Rocket! Destroys 100 pixels (leaves 1,000 defense) & erases 100 of your pixels.';
    } else if (!isLand) {
      document.getElementById('hud-pixel-info').textContent = 'Ocean waters are locked by coastline borders.';
    } else if (existing) {
      const troops = getPixelTroops(existing, now);
      const status = (existing.colonizingUntil && now < existing.colonizingUntil)
        ? 'Colonizing (1s)...'
        : `${troops} / ${MAX_TROOPS} troops`;
      document.getElementById('hud-pixel-info').textContent = `Owner: ${existing.owner} • Garrison: ${status}`;
    } else if (isScorched) {
      document.getElementById('hud-pixel-info').textContent = '☢️ Scorched Empty Land (1,000 defense) • Requires 1,000 troops to colonize';
    } else {
      const myCount = getPlayerOwnedPixels(currentUser.username).length;
      document.getElementById('hud-pixel-info').textContent = myCount === 0
        ? `Empty Land • Click to found Capital (1,000 troops)`
        : `Neutral Land (500 defense) • Click adjacent border to colonize in 1s`;
    }

    if (now - lastPresenceSent > 1000) {
      lastPresenceSent = now;
      broadcastLivePresence(gx, gy, isLand ? `in ${region}` : 'at coast');
    }
  }

  if (!isDragging) return;
  const dx = e.clientX - lastPointer.x;
  const dy = e.clientY - lastPointer.y;
  if (Math.hypot(dx, dy) > 4) dragMoved = true;

  if (dragMoved) {
    const scale = getBaseScale() * camera.zoom;
    camera.targetX = Math.max(0, Math.min(GRID_W, camera.targetX - dx / scale));
    camera.targetY = Math.max(0, Math.min(GRID_H, camera.targetY - dy / scale));
    camera.x = camera.targetX;
    camera.y = camera.targetY;
    camera.vx = (-dx / scale) * 0.35;
    camera.vy = (-dy / scale) * 0.35;
  }
  lastPointer = { x: e.clientX, y: e.clientY };
});

canvas.addEventListener('pointerup', (e) => {
  isDragging = false;
  if (!dragMoved && (conquerMode || rocketAimMode)) {
    const rect = canvas.getBoundingClientRect();
    const { gx, gy } = screenToGrid(e.clientX - rect.left, e.clientY - rect.top);
    handleConquerAt(gx, gy);
  }
});

canvas.addEventListener('wheel', (e) => {
  e.preventDefault();
  const rect = canvas.getBoundingClientRect();
  const sx = e.clientX - rect.left;
  const sy = e.clientY - rect.top;
  const factor = e.deltaY < 0 ? 1.25 : 0.8;
  const nextZoom = Math.max(0.8, Math.min(50, camera.targetZoom * factor));

  const W = rect.width, H = rect.height;
  const oldScale = getBaseScale() * camera.targetZoom;
  const newScale = getBaseScale() * nextZoom;
  const worldX = camera.targetX + (sx - W / 2) / oldScale;
  const worldY = camera.targetY + (sy - H / 2) / oldScale;

  camera.targetZoom = nextZoom;
  camera.targetX = Math.max(0, Math.min(GRID_W, worldX - (sx - W / 2) / newScale));
  camera.targetY = Math.max(0, Math.min(GRID_H, worldY - (sy - H / 2) / newScale));
}, { passive: false });

/**
 * ============================================================================
 * 10. UI, STATS LOOP, LEADERBOARD & SUPABASE REALTIME
 * ============================================================================
 */
function initPalette() {
  const container = document.getElementById('paletteContainer');
  PALETTE.forEach(hex => {
    const btn = document.createElement('button');
    btn.className = 'w-6 h-6 rounded-full border-2 transition transform hover:scale-110 ' +
      (hex === selectedColor ? 'border-white scale-110 ring-2 ring-sky-400' : 'border-slate-700');
    btn.style.backgroundColor = hex;
    btn.onclick = () => {
      selectedColor = hex;
      document.querySelectorAll('#paletteContainer button').forEach(b => {
        b.className = 'w-6 h-6 rounded-full border-2 border-slate-700 transition transform hover:scale-110';
      });
      btn.className = 'w-6 h-6 rounded-full border-2 border-white scale-110 ring-2 ring-sky-400 transition';
    };
    container.appendChild(btn);
  });

  document.getElementById('customColorPicker').addEventListener('input', (e) => {
    selectedColor = e.target.value;
  });
}

function toggleInteractionMode() {
  conquerMode = !conquerMode;
  const btn = document.getElementById('modeToggleBtn');
  const lbl = document.getElementById('modeLabel');
  if (conquerMode) {
    btn.className = 'px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow transition flex items-center gap-1.5';
    lbl.textContent = 'Conquer: ON';
  } else {
    btn.className = 'px-3 py-1.5 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-200 text-xs font-bold shadow transition flex items-center gap-1.5';
    lbl.textContent = 'Scout / Pan';
  }
}

function toggleLiveFeed() {
  document.getElementById('liveActivityPanel').classList.toggle('hidden');
}

function showToast(msg) {
  const toast = document.getElementById('mapToast');
  toast.textContent = msg;
  toast.classList.remove('opacity-0');
  clearTimeout(window._toastTimer);
  window._toastTimer = setTimeout(() => toast.classList.add('opacity-0'), 3200);
}

function openModal(id) {
  if (id === 'leaderboardModal') renderLeaderboards();
  document.getElementById(id).classList.remove('hidden');
}
function closeModal(id) {
  document.getElementById(id).classList.add('hidden');
}

function renderAuthUI() {
  const area = document.getElementById('authArea');
  const isRegistered = !!localStorage.getItem('pw_user');
  if (isRegistered) {
    area.innerHTML = `
      <div class="flex items-center gap-2 bg-slate-800 border border-slate-700 px-3 py-1.5 rounded-lg">
        <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
        <span class="text-xs font-bold text-white">${currentUser.username}</span>
        <button onclick="signOutPlayer()" class="text-[11px] text-rose-400 hover:text-rose-300 ml-1">Exit</button>
      </div>
    `;
  } else {
    area.innerHTML = `
      <button onclick="openModal('authModal')" class="px-3.5 py-1.5 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold shadow-lg shadow-sky-600/25 transition">
        ${currentUser.username}
      </button>
    `;
  }
}

function setGuestName() {
  const username = document.getElementById('authUsername').value.trim();
  if (!username) { showToast('Enter a Nation / Commander name.'); return; }
  currentUser = { username };
  localStorage.setItem('pw_user', JSON.stringify(currentUser));
  livePlayers.set(clientId, { ...livePlayers.get(clientId), username });
  renderAuthUI();
  renderLivePanel();
  updateStatsUI();
  closeModal('authModal');
  showToast(`Commander ${username} ready!`);
}

async function handleAuth(mode) {
  const username = document.getElementById('authUsername').value.trim() || currentUser.username;
  const email = document.getElementById('authEmail').value.trim();
  const password = document.getElementById('authPassword').value.trim();
  if (!email || !password) { setGuestName(); return; }

  if (supabaseClient) {
    const res = mode === 'signup'
      ? await supabaseClient.auth.signUp({ email, password, options: { data: { username } } })
      : await supabaseClient.auth.signInWithPassword({ email, password });
    if (res.error) { showToast(res.error.message); return; }
  }

  currentUser = { username, email };
  localStorage.setItem('pw_user', JSON.stringify(currentUser));
  livePlayers.set(clientId, { ...livePlayers.get(clientId), username });
  renderAuthUI();
  renderLivePanel();
  updateStatsUI();
  closeModal('authModal');
  showToast(`Welcome, Commander ${username}!`);
}

function signOutPlayer() {
  localStorage.removeItem('pw_user');
  currentUser = { username: 'Nation_' + Math.floor(100 + Math.random() * 900) };
  if (supabaseClient) supabaseClient.auth.signOut();
  renderAuthUI();
  renderLivePanel();
  updateStatsUI();
}

function updateStatsUI() {
  const now = Date.now();
  let myCount = 0;
  let myTroops = 0;

  paintedPixels.forEach(p => {
    if (p.owner === currentUser.username) {
      myCount++;
      myTroops += getPixelTroops(p, now);
    }
  });

  document.getElementById('stat-my-pixels').textContent = `${myCount.toLocaleString()} px`;
  document.getElementById('stat-my-troops').textContent = `${myTroops.toLocaleString()} / ${(myCount * MAX_TROOPS).toLocaleString()}`;
  document.getElementById('stat-my-rockets').textContent = `${readyRockets} 🚀`;
  document.getElementById('stat-painted').textContent = paintedPixels.size.toLocaleString('en-US');

  const buildBtn = document.getElementById('buildRocketBtn');
  const buildLbl = document.getElementById('buildRocketLabel');
  if (buildBtn && buildLbl) {
    if (myCount >= ROCKET_PIXEL_COST) {
      buildBtn.className = 'px-3 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-extrabold shadow-lg shadow-amber-500/30 transition flex items-center gap-1.5';
      buildLbl.textContent = `Build Rocket (${myCount}/100 px)`;
    } else {
      buildBtn.className = 'px-3 py-1.5 rounded-lg bg-slate-800 text-slate-400 border border-slate-700 text-xs font-semibold transition flex items-center gap-1.5';
      buildLbl.textContent = `Rocket (${myCount}/100 px)`;
    }
  }
}

function renderLeaderboards() {
  const now = Date.now();
  const nations = {};
  const regionCounts = {};

  paintedPixels.forEach(p => {
    if (!nations[p.owner]) nations[p.owner] = { pixels: 0, troops: 0 };
    nations[p.owner].pixels += 1;
    nations[p.owner].troops += getPixelTroops(p, now);

    const reg = p.region || 'Asia';
    regionCounts[reg] = (regionCounts[reg] || 0) + 1;
  });

  const sortedNations = Object.entries(nations).sort((a, b) => b[1].pixels - a[1].pixels).slice(0, 10);
  document.getElementById('playerLeaderboardList').innerHTML = sortedNations.length
    ? sortedNations.map(([name, info], i) => `
      <div class="flex items-center justify-between bg-slate-900 px-3 py-2 rounded-lg border border-slate-800">
        <div class="flex items-center gap-2">
          <span class="mono font-bold text-sky-400">#${i + 1}</span>
          <span class="font-semibold">${name}</span>
        </div>
        <div class="text-right">
          <div class="mono font-bold text-emerald-400">${info.pixels.toLocaleString()} px</div>
          <div class="mono text-[10px] text-amber-400">${info.troops.toLocaleString()} troops</div>
        </div>
      </div>
    `).join('')
    : '<p class="text-slate-500">Map is empty — no nations founded yet.</p>';

  const sortedRegions = Object.entries(regionCounts).sort((a, b) => b[1] - a[1]);
  document.getElementById('regionStatsList').innerHTML = sortedRegions.length
    ? sortedRegions.map(([reg, count]) => `
      <div class="bg-slate-900 px-3 py-2 rounded-lg border border-slate-800">
        <div class="flex justify-between mb-1"><span class="font-semibold">${reg}</span><span class="mono text-sky-400">${count.toLocaleString()} px</span></div>
        <div class="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
          <div class="h-full bg-emerald-500" style="width:${Math.min(100, Math.max(4, (count / paintedPixels.size) * 100))}%"></div>
        </div>
      </div>
    `).join('')
    : '<p class="text-slate-500">No continental control yet.</p>';
}

function shareMapView() {
  const url = new URL(window.location.origin + window.location.pathname);
  url.searchParams.set('fresh', '1');
  navigator.clipboard?.writeText(url.toString());
  showToast('🔗 Fresh Empty-Map Invite Link copied! Send it to your friend.');
}

function saveSupabaseConfig() {
  const u = document.getElementById('sbUrlInput').value.trim();
  const k = document.getElementById('sbKeyInput').value.trim();
  if (!u || !k) return;
  localStorage.setItem('pw_sb_url', u);
  localStorage.setItem('pw_sb_key', k);
  SUPABASE_URL = u;
  SUPABASE_ANON_KEY = k;
  closeModal('supabaseModal');
  connectSupabase();
}

function applyRemoteRocketStrike(payload) {
  if (!payload) return;
  const now = Date.now();
  (payload.erasedCoords || []).forEach(c => paintedPixels.delete(`${c.x},${c.y}`));
  (payload.blastedCoords || []).forEach(c => {
    const k = `${c.x},${c.y}`;
    paintedPixels.delete(k);
    scorchedPixels.set(k, now);
  });
  explosionEffects.push({ gx: payload.centerGx, gy: payload.centerGy, createdAt: now });
  persistLocalState();
  updateStatsUI();
  recordLiveAction(payload.attacker || 'Rival', 'launched a ROCKET strike (100px scorched)!', '#f43f5e', payload.centerGx, payload.centerGy);
  showToast(`💥 ROCKET ALERT! ${payload.attacker || 'A commander'} scorched 100 pixels!`);
}

async function connectSupabase(skipInitialLoad = false) {
  if (!SUPABASE_URL || !SUPABASE_ANON_KEY || !window.supabase) return;
  try {
    supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

    if (skipInitialLoad) {
      await supabaseClient.from('pixels').delete().gte('x', 0);
    } else {
      const { data, error } = await supabaseClient.from('pixels').select('*').limit(50000);
      if (!error && data) {
        data.forEach(row => {
          if (landMask[row.y * GRID_W + row.x] === 1) {
            const ts = row.updated_at ? new Date(row.updated_at).getTime() : Date.now();
            paintedPixels.set(`${row.x},${row.y}`, {
              x: row.x, y: row.y,
              color: row.color,
              owner: row.owner_name || 'Nation',
              region: row.region || 'Asia',
              baseTroops: MAX_TROOPS,
              updatedAt: ts,
              colonizingUntil: 0
            });
          }
        });
        updateStatsUI();
      }
    }

    realtimeChannel = supabaseClient
      .channel('pixel_world_live_channel')
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'pixels' }, payload => {
        const row = payload.new;
        if (row && landMask[row.y * GRID_W + row.x] === 1) {
          const key = `${row.x},${row.y}`;
          scorchedPixels.delete(key);
          const existing = paintedPixels.get(key);
          const ts = row.updated_at ? new Date(row.updated_at).getTime() : Date.now();
          if (!existing || existing.owner !== row.owner_name || Math.abs((existing.updatedAt || 0) - ts) > 1500) {
            paintedPixels.set(key, {
              x: row.x, y: row.y,
              color: row.color,
              owner: row.owner_name || 'Nation',
              region: row.region || 'Asia',
              baseTroops: 0,
              updatedAt: ts,
              colonizingUntil: ts
            });
            updateStatsUI();
            recordLiveAction(row.owner_name || 'Nation', `captured land in ${row.region || 'world'}`, row.color, row.x, row.y);
          }
        }
      })
      .on('postgres_changes', { event: 'UPDATE', schema: 'public', table: 'pixels' }, payload => {
        const row = payload.new;
        if (row && landMask[row.y * GRID_W + row.x] === 1) {
          const key = `${row.x},${row.y}`;
          scorchedPixels.delete(key);
          const existing = paintedPixels.get(key);
          const ts = row.updated_at ? new Date(row.updated_at).getTime() : Date.now();
          if (!existing || existing.owner !== row.owner_name || Math.abs((existing.updatedAt || 0) - ts) > 1500) {
            paintedPixels.set(key, {
              x: row.x, y: row.y,
              color: row.color,
              owner: row.owner_name || 'Nation',
              region: row.region || 'Asia',
              baseTroops: 0,
              updatedAt: ts,
              colonizingUntil: ts
            });
            updateStatsUI();
          }
        }
      })
      .on('postgres_changes', { event: 'DELETE', schema: 'public', table: 'pixels' }, payload => {
        const oldRow = payload.old;
        if (oldRow && typeof oldRow.x === 'number' && typeof oldRow.y === 'number') {
          paintedPixels.delete(`${oldRow.x},${oldRow.y}`);
          updateStatsUI();
        }
      })
      .on('broadcast', { event: 'rocket_strike' }, ({ payload }) => {
        if (payload && payload.attacker !== currentUser.username) {
          applyRemoteRocketStrike(payload);
        }
      })
      .on('broadcast', { event: 'map_reset' }, ({ payload }) => {
        paintedPixels.clear();
        scorchedPixels.clear();
        readyRockets = 0;
        rocketAimMode = false;
        persistLocalState();
        updateStatsUI();
        updateRocketUI();
        showToast(`🌍 ${payload?.by || 'Commander'} started a fresh empty map!`);
      })
      .on('broadcast', { event: 'player_activity' }, ({ payload }) => {
        if (payload && payload.id !== clientId) {
          livePlayers.set(payload.id, { ...payload, updatedAt: Date.now() });
          renderLivePanel();
        }
      })
      .subscribe((status) => {
        if (status === 'SUBSCRIBED') {
          broadcastLivePresence(Math.floor(camera.x), Math.floor(camera.y), 'ready on map');
        }
      });

    document.getElementById('sync-badge').innerHTML = '<span class="w-2 h-2 rounded-full bg-emerald-400"></span> Supabase Live';
    document.getElementById('sync-badge').className = 'text-xs font-semibold text-emerald-400 flex items-center gap-1.5';
  } catch (err) {
    console.error(err);
  }
}

if (broadcastChannel) {
  broadcastChannel.onmessage = (e) => {
    if (e.data?.type === 'PIXEL_SYNC') {
      const p = e.data.payload;
      const k = `${p.x},${p.y}`;
      scorchedPixels.delete(k);
      paintedPixels.set(k, p);
      updateStatsUI();
    } else if (e.data?.type === 'ROCKET_STRIKE') {
      applyRemoteRocketStrike(e.data.payload);
    } else if (e.data?.type === 'MAP_RESET') {
      paintedPixels.clear();
      scorchedPixels.clear();
      readyRockets = 0;
      rocketAimMode = false;
      persistLocalState();
      updateStatsUI();
      updateRocketUI();
    } else if (e.data?.type === 'PRESENCE') {
      const p = e.data.payload;
      if (p.id !== clientId) {
        livePlayers.set(p.id, { ...p, updatedAt: Date.now() });
        renderLivePanel();
      }
    }
  };
}

setInterval(() => {
  updateStatsUI();
}, 500);

setInterval(renderLivePanel, 5000);

window.addEventListener('DOMContentLoaded', async () => {
  document.getElementById('sbUrlInput').value = SUPABASE_URL;
  document.getElementById('sbKeyInput').value = SUPABASE_ANON_KEY;
  initPalette();
  renderAuthUI();
  updateRocketUI();
  renderLivePanel();
  resizeCanvas();

  rasterizeFallbackMap();

  const params = new URLSearchParams(window.location.search);
  const isFreshInvite = params.get('fresh') === '1';

  if (isFreshInvite) {
    // Start 100% from scratch on an empty map when opening a fresh invite link
    paintedPixels.clear();
    scorchedPixels.clear();
    readyRockets = 0;
    persistLocalState();
    updateStatsUI();
    updateRocketUI();
    // Clean ?fresh=1 from URL bar so refreshing later doesn't wipe ongoing match
    window.history.replaceState({}, document.title, window.location.pathname);
    showToast('🌍 Fresh Empty Map started! Click any land pixel to found your Capital.');
  } else {
    loadLocalState();
  }

  requestAnimationFrame(renderLoop);

  if (params.has('lat') && params.has('lon')) {
    flyToRegion(parseFloat(params.get('lon')), parseFloat(params.get('lat')), parseFloat(params.get('z') || '4'));
  }

  await connectSupabase(isFreshInvite);
  await upgradeToRealWorldMap();
});
</script>
</body>
</html>
'''

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Updated index.html with fresh empty map start + 10x10 Rocket mechanic")